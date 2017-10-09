import csv
import os
import re
import sys


class TuneList:

    def __init__(self, path):
		# Is path local or remote?
        source = 'remote' if re.search(r'^(http|ftp)', path) else 'local'
        self._read_file(path, source)

    def _read_file(self, path, source):
        """
        Take a path to a csv file.
        Return contents as csv file. Formatted as follows:
            [index, dance, title, key, instrument, difficulty]
        """
        if source == 'remote':
            def open_file(): return urllib.request.urlopen(path)
        else:
            def open_file(): return open(path)

        try:
            f = open_file()
        except FileNotFoundError:
            print("Cannot find list file. Exiting.")
            exit()
        reader = csv.reader(f)
        # Read the CSV file into a list, lower-casing all values.
        self.list_of_tunes = [[i]+[value.lower() for value in row] for i,row \
                              in enumerate(reader)]
        f.close()
        return self.list_of_tunes

    def search(self, query):
        """
        Search list of tunes for query.
        Arguments
            query (str): the query to search for
        """

        difficulty = None
        key = None

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
                difficulty = int(query[1][2])
            else:
                # Key is prepended by 'in'
                key = query[2]

        if len(query) > 3:
            # Then last argument must be difficulty
            # Difficulty is formatted as *=n
            difficulty = int(query[-1][2])

        return self._filter(dance, key, difficulty)

    def _filter(self, dance, key, difficulty):
        # The possibilities are:
        # dance
        # dance in key
        # dance in difficulty
        # dance in key and difficulty

        if dance:
            tunes_indices  = set([r[0] for r in self.list_of_tunes if dance in r[1]])

        if key:
            tunes_indices = set.intersection(set([r[0] for r in self.list_of_tunes if key\
                                          in r[3]]), tunes_indices)
        if difficulty:
            tunes_indices = set.intersection(set([r[0] for r in self.list_of_tunes if '*'\
                                         * difficulty == r[5]]), tunes_indices)

        tunes = [r for r in self.list_of_tunes if r[0] in tunes_indices]
        return tunes


    def random_set(self, query):
        pass

def usage():
    print("Usage")

def main():
    if len(sys.argv) < 3:
        return usage()

    command, query = sys.argv[1].lower(), [a.lower() for a in sys.argv[2:]]
    t = TuneList('list.csv')

    if command == 'search':
        print(t.search(query))

    if command == 'set':
        t.random_set(query)



if __name__ == '__main__':
    main()

