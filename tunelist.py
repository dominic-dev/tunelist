#!/usr/bin/python3
import codecs
import csv
import os
import operator
import random
import re
import urllib.request
import sys

from settings import PATH_TO_FILE, TITLE_INDEX, DANCE_INDEX, KEY_INDEX, DIFFICULTY_INDEX
import weights


MODES = {
    'major' : ('', 'maj', 'major', '+'),
    'minor': ('m', 'min', 'minor', 'dor', 'dorian'),
}

class TuneList:
    """
    TuneList.
    """

    def __init__(self, path):
		# Is path local or remote?
        source = 'remote' if re.search(r'^(http|ftp)', path) else 'local'
        self._read_file(path, source)

        self.selected_tunes = []
        self.difficulty = None

    def search(self, query):
        """
        Search list of tunes for query.
        Arguments
            query (str): the query to search for
        """

        key = None
        difficulty = None

        # First argument can be either dance or difficulty.
        if '*' in query[0]:
            difficulty = query[0]
            # return query with difficulty
        else:
            dance = query[0]

        if len(query) > 1:
            # Second argument may be key or difficulty
            # Difficulty is formatted as *=n
            if '*' in query[1]:
                difficulty = QueryParser._parse_difficulty(query[1])
            else:
                # Key is prepended by 'in'
                key = query[2]

        if len(query) > 3:
            # Then last argument must be difficulty
            # Difficulty is formatted as *=n
            difficulty = QueryParser._parse_difficulty(query[-1])


        return self._filter(dance, key, difficulty)

    def random_set(self, query):
        """
        Take a title of a tune, or space separated keys.
        Return a set of tunes.
        Arguments:
            query (list): the arguments to be processed as query.
        """

        option, query = query[0], query[1:]
        # Is difficulty in query?
        if '*' in query[-1]:
            self.difficulty = QueryParser._parse_difficulty(query.pop())

        # Create set from title
        if option == '-t':
            title = ' '.join(query)
            self._create_random_set_from_title(title)

        # TODO
        # Create set by keys
        else:
            pass

    def _create_random_set_from_title(self, title, n=3):
        """
        Find a tune by title, return a random set.
        """
        # Find tune.
        result =[r for r in self.list_of_tunes if title.lower() in\
               r[TITLE_INDEX].lower()]

        # Search may return multiple results. Allow user to choose.
        if len(result) == 1:
            tune = result[0]
        elif len(result) > 1:
            print("Your search returned multiple results.")
            [print(str(i+1).ljust(5), r[TITLE_INDEX].ljust(30), r[KEY_INDEX]) for i,r\
                                                                in enumerate(result)]
            while True:
                selection = input("Please type in the number of the tune you which to select.\n")
                # Answer must be a valid integer.
                try:
                    selection = int(selection)-1
                except:
                    selection = None
                # Answer must be within the range of the results.
                else:
                    if selection not in range(len(result)):
                        selection = None

                if selection is None:
                    print("The number you entered is not valid.")
                else:
                    break

            tune = result[selection]
            print(tune)
        else:
            raise TuneNotFoundError

        # Create set
        self._generate_random_sequence(tune)

        #print(self.selected_tunes)

        [print(*['{} ({}) {}'.format(t[TITLE_INDEX], t[KEY_INDEX],\
                              t[DIFFICULTY_INDEX]).title()], sep=', ')\
         for t in self.selected_tunes]

    def _filter(self, dance=None, key=None, difficulty=None, title=None):
        """
        Filter the list of tunes by dance, key and difficulty.
        """
        # The possibilities are:
        # dance
        # dance in key
        # dance in difficulty
        # dance in key and difficulty

        # Start with entire pool.
        tunes_indices = [r[0] for r in self.list_of_tunes]

        # Filters
        if dance:
            tunes_indices  = set.intersection(set([r[0] for r in \
                            self.list_of_tunes if dance in r[DANCE_INDEX]]), tunes_indices)

        if key:
            keys = QueryParser._parse_key(key)
            tunes_indices = set.intersection(set([r[0] for r in \
                            self.list_of_tunes if any(k in \
                            r[KEY_INDEX].lower().split() for k in keys)]), tunes_indices)
        if difficulty:
            operator_, digit = difficulty
            # Filter by operator(difficulty_in_data, difficuly_in_query)
            tunes_indices = set.intersection(set([r[0] for r in \
                            self.list_of_tunes if operator_(len(r[DIFFICULTY_INDEX]), digit)]),\
                            tunes_indices)
        if title:
            tunes_indices  = set.intersection(set([r[0] for r in self.list_of_tunes \
                                  if title in r[TITLE_INDEX]]), tunes_indices)

        tunes = [r for r in self.list_of_tunes if r[0] in tunes_indices]
        return tunes

    def _generate_random_sequence(self, tune, position=None, n=3):
        """
        Take a tune and return a random sequence of tunes based on weights.
        Arguments
        position (int): Where the specified tune appears in the sequence.
        n (int): The number of tunes to return.
        """
        self.selected_tunes = [tune]
        if position is None:
            position = new_position = random.randint(1,n)

        current_position = tune_position = position
        # Start going forward
        forward = True

        # Begin filling sequence
        N = 1
        while N < n:
            if forward:
                # If the end of the sequence is reached, start going backward
                # starting from the inital tune.
                if current_position == n:
                    forward = False
                    current_position = tune_position - 1
                    continue

                key =  QueryParser._parse_key(self.selected_tunes[-1][KEY_INDEX])[0]
                tune = self._random_tune(tune)
                if not tune:
                    continue
                self.selected_tunes.append(tune)
                current_position += 1
            else:
                if current_position == 0:
                    # Done
                    break
                key = QueryParser._parse_key(self.selected_tunes[0][KEY_INDEX])[0]
                tune = self._random_tune(tune, forward=False)
                if not tune:
                    continue
                self.selected_tunes.insert(0, tune)
                current_position -= 1

            N += 1

    def _random_tune(self, tune, forward=True):
        """
        Take a tune, return a random tune to follow or precede it. Based on weights
        specified in weights.py
        Arguments:
            tune (list) : The tune to be processed.
            forward (bool) : Get tune to follow it if true, to precede it if
            false.
        """
        # Tune may have multiple keys, select the first.
        key = tune[KEY_INDEX]
        if ' ' in key or ',' in key:
            key = key.split(', ')[0]
        # Parse the key, and select the first mode notation.
        key = QueryParser._parse_key(tune[KEY_INDEX])[0]

        if forward:
            try:
                w = weights.WEIGHTS[key]
            # Return a random key from the tuple if no weights are available
            except KeyError:
                print('No weight found for {}'.format(key))
                population = None
            else:
                total = sum(w.values())
                cumulative_weights = [v / total * 100 for v in cumulative(w.values())]
                population = w.keys()
        else:
            absolute_weights_backwards = { k : v[key] * len(v) for k,v in weights.WEIGHTS.items() if\
                          key in v.keys()}
            total = sum(absolute_weights_backwards.values())
            # Divide the absolute value by the new total to get the new
            # probability, and calculate the cumulative weights.
            cumulative_weights = [w for w in \
                                  cumulative([v / total * 100 for k,v in absolute_weights_backwards.items()])
                                 ]
            population =  absolute_weights_backwards.keys()

        # Choose weighted random key if data is available.
        if population:
            key = self._weighted_random(population, cumulative_weights)
        # If no valid data was found, choose a random key.
        else:
            key = ('d', 'g', 'em', 'bm', 'am')[random.randint(0,4)]

        # The tunes to choose from, filtered by key.
        # Tunes that were already chosen are filtered out.
        pool = [t for t in self._filter(tune[DANCE_INDEX], key,\
                        self.difficulty) if t not in self.selected_tunes]
        #pool = [t for t in self.list_of_tunes if key in t[KEY_INDEX] and t not\
        #       in self.selected_tunes]

        if not pool:
            return None
        return pool[random.randint(0,len(pool)-1)]

    def _weighted_random(self, population, cumulative_weights):
        """
        Take a population and cumulative weights, return a value from
        population.
        """
        random_number = random.randint(0,100)
        for i,p in enumerate(population):
            if cumulative_weights[i] == random_number or \
               cumulative_weights[i] > random_number:
               return p

    def _read_file(self, path, source):
        """
        Take path to a csv file.
        Return list from contents of csv file. Formatted as follows:
            [index, dance, title, key, instrument, difficulty]
        """

        if source == 'remote':
            f = urllib.request.urlopen(path)
            reader = csv.reader(codecs.iterdecode(f, 'utf-8'))
        else:
            f = open(path)
            reader = csv.reader(f)

        # Read the CSV file into a list, lower-casing all values.
        self.list_of_tunes = [[i]+[value.lower() for value in row] for i,row \
                              in enumerate(reader)]

        f.close()
        return self.list_of_tunes


class TuneNotFoundError(Exception):
    pass


class QueryParser:
    """
    Read query string, return parsed item.
    """
    @classmethod
    def _parse_difficulty(cls, string):
        """
        Take difficulty string from argument. e.g. *=2
        Return tuple: operator(object), digit(int)
        """
        # Operator objects.
        operators = {
          '=' : operator.eq,
          'l' : operator.lt,
          'g' : operator.gt
        }
        operator_, digit = string[1:] # ommit '*'
        # Return operator (object), digit (int)
        return (operators[operator_], int(digit))

    @classmethod
    def _parse_key(cls, string):
        """
        Take key string from argument.
        Return list of possible modes and notations.
        """
        mode = 'major'
        if len(string) > 1:
            if string[1:] in MODES['minor']:
                mode = 'minor'
        return [string[0].lower() + m for m in MODES[mode]]

    @classmethod
    def _parse_title(cls, string):
        """
        Take title string. Return title.
        """
        m = re.search(r'.*?(\'|")(.*)(\'|").*', string)
        title = m.group(2) if m else None
        return title


def cumulative(list_):
    """
    Take a list, return cumulative list.
    """
    total = 0
    for x in list_:
        total += x
        yield total


def usage():
    print("Usage")


def main():
    if len(sys.argv) < 3:
        return usage()

    command, query = sys.argv[1].lower(), [a.lower() for a in sys.argv[2:]]
    t = TuneList(PATH_TO_FILE)

    if command == 'search':
        result = t.search(query)
        if result:
            [print(r) for r in result]
        else:
            print('Nothing found.')

    if command == 'set':
        t.random_set(query)


if __name__ == '__main__':
    main()

