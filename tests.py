import unittest
import tunelist

DANCE_INDEX = 1
TITLE_INDEX = 2
KEY_INDEX = 3
DIFFICULTY_INDEX = 5

class TestTuneList(unittest.TestCase):
    t = tunelist.TuneList('list.csv')
    def test_result_is_list(self):
        self.assertIsInstance(self.t.list_of_tunes, list)

    def test_result_it_not_empty(self):
        self.assertTrue(self.t.list_of_tunes)

    def test_file_not_found(self):
        with self.assertRaises(FileNotFoundError):
            t = tunelist.TuneList('')

    def test_dance(self):
        result = self.t.search(['reel'])
        for row in result:
            self.assertEqual('reel', row[DANCE_INDEX])

    def test_key(self):
        result = self.t.search(['reel', 'in', 'D'])
        for row in result:
            self.assertEqual(row[DANCE_INDEX], 'reel')
            self.assertIn(row[KEY_INDEX].lower(), ('d', 'd+', 'dmajor',
                                                   'dmaj'))
    def test_title(self):
        result = self.t.search(['reel'])
        filtered = self.t._filter(title='wind')
        for row in filtered:
            self.assertIn('wind', row[TITLE_INDEX])


    def test_difficulty_equals(self):
        result = self.t.search(['reel', '*=2'])
        for row in result:
            self.assertEqual(row[DIFFICULTY_INDEX], '**')

    def test_difficulty_greater_than(self):
        result = self.t.search(['reel', '*g1'])
        for row in result:
            self.assertIn(row[DIFFICULTY_INDEX], ('**', '***'))

    def test_difficulty_less_than(self):
        result = self.t.search(['reel', '*l3'])
        for row in result:
            self.assertIsNot(row[DIFFICULTY_INDEX], '***')

if __name__ == "__main__":
    unittest.main()
