import doctest
import split
import unittest

class TestSplit(unittest.TestCase):
    "Tests for split.py."

    def test_everything(self):
        tests=[
            (['hello', 'world'], []),
            ([], []),
            (['[title]', 'text'], [('title',['text'])]),
            (['[title]', 'text', 'more'], [('title',['text', 'more'])]),
            (['text', '[title]'], [('title',[])]),
            (['[title]', '[title]'], [('title',[]), ('title', [])]),
            (['[title]', 'not a [title]'], [('title',['not a [title]'])]),
        ]
        for t in tests:
            expected = t[1]
            got = list(split.strings(t[0]))
            self.assertEqual(got, expected)

class TestDocs(unittest.TestCase):
    def test_docs(self):
        doctest.testmod(split, globs={'split':split})

if __name__ == '__main__':
    unittest.main()