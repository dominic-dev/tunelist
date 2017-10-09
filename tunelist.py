#!/usr/bin/python3
import csv
import os
import operator
import re
import sys

DANCE_INDEX = 1
TITLE_INDEX = 2
KEY_INDEX = 3
DIFFICULTY_INDEX = 5

class TuneList:

    def __init__(self, path):
        # File exists?
        if not os.path.exists(path):
            raise FileNotFoundError('Cannot find file.')
		# Is path local or remote?
        source = 'remote' if re.search(r'^(http|ftp)', path) else 'local'
        self._read_file(path, source)

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
                difficulty = self._parse_difficulty(query[1])
            else:
                # Key is prepended by 'in'
                key = query[2]

        if len(query) > 3:
            # Then last argument must be difficulty
            # Difficulty is formatted as *=n
            difficulty = self._parse_difficulty(query[-1])


        return self._filter(dance, key, difficulty)

    def random_set(self, query):
        """
        Take a title of a tune, or space separated keys.
        Return a set of tunes.
        Arguments:
            query (list): the arguments to be processed as query.
        """

        # Create set by title
        if any((c in ('"', "'")) for c in ' '.join(query)):
            title = self._parse_title(query)
            self._create_set_from_title(title)

        # Create set by keys
        else:
            # TODO
            pass

    def _create_set_from_title(self, n=3):
        # TODO
        pass

    def _create_set_from_keys(self, keys, difficulty=None):
        """
        Take list of keys, return list of tunes.
        Arguments:
            keys (list) : Keys to filter tunes by
            difficulty (dict) : Difficulty to filter tunes by.
        """
        # TODO
        pass


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
            keys = self._parse_key(key)
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

    def _parse_difficulty(self, string):
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

    def _parse_key(self, string):
        """
        Take key string from argument.
        Return list of possible modes and notations.
        """
        modes = {
            'major' : ('', 'maj', 'major', '+'),
            'minor': ('m', 'min', 'minor', 'dor', 'dorian'),
        }
        mode = 'major'
        if len(string) > 1:
            if string[1:] in modes['minor']:
                mode = 'minor'
        return [string[0].lower() + m for m in modes[mode]]

    def _parse_title(self, string):
        """
        Take title string. Return title.
        """
        m = re.search(r'.*?(\'|")(.*)(\'|").*', string)
        title = m.group(2) if m else None
        return title

    def _read_file(self, path, source):
        """
        Take path to a csv file.
        Return list from contents of csv file. Formatted as follows:
            [index, dance, title, key, instrument, difficulty]
        """

        if source == 'remote':
            f = urllib.request.urlopen(path)
        else:
            f = open(path)
        reader = csv.reader(f)
        # Read the CSV file into a list, lower-casing all values.
        self.list_of_tunes = [[i]+[value.lower() for value in row] for i,row \
                              in enumerate(reader)]
        f.close()
        return self.list_of_tunes



def usage():
    print("Usage")


def main():
    if len(sys.argv) < 3:
        return usage()

    command, query = sys.argv[1].lower(), [a.lower() for a in sys.argv[2:]]
    t = TuneList('list.csv')

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

