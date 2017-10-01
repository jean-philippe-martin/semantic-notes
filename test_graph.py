import unittest
import graph
import doctest
from kb import KB

class TestGraph(unittest.TestCase):
 
    def test_neighbors(self):
        kb=KB({'a': {'e': ['beta']}, 'beta': {}, 'ch': {'e': ['a']}, 'd': {}})
        for start in ['a', 'beta', 'ch']:
            # Be OK whether it returns a set or list
            got=sorted(list(graph.neighbors(kb, 'e', start)))
            expect=['a','beta','ch']
            self.assertEqual(got, expect)

    def test_neighbors_aka(self):
        kb=KB({'a': {'e': ['baby']}, 'beta': {'aka': ['baby']}, 'ch': {'e': ['a']}, 'd': {}})
        for start in ['a', 'beta', 'ch']:
            # Be OK whether it returns a set or list
            got=sorted(list(graph.neighbors(kb, 'e', start)))
            expect=['a','beta','ch']
            self.assertEqual(got, expect)

    def test_predecessors(self):
        kb=KB({'apple': {'color': ['red']}, 
            'red': {'isa': ['color']},
            'water': {'color': ['blue']},
            'blueberry': {'color': ['green', 'blue']}})
        tests = [
            # straightforward case
            ('red', ['apple']),
            # multiple predecessors
            ('blue', ['water', 'blueberry']),
            # predecessor that isn't a key itself
            ('green', ['blueberry']),
        ]
        for color, expected in tests:
            got = graph.predecessors(kb, 'color', color)
            self.assertEqual(got, expected)

    def test_roots_among(self):
        kb = KB({'apple': {'isa': ['fruit']}, 
              'fruit': {'isa': ['edible']},
              'chocolate': {'isa': ['edible']}, 
             })
        got = graph.roots_among(kb, 'isa', set(['apple', 'fruit']))
        expected = set(['apple'])
        self.assertEqual(got, expected)
        # a -> i -> z -> a
        #   -> j -> m, n
        #   -> k -> o, p
        kb = KB({ 
            'a': {'e': ['i', 'j', 'k']},
            'i': {'e': ['z']},
            'j': {'e': ['m', 'n']},
            'k': {'e': ['o', 'p']},
            'z': {'e': ['a']},
            })
        tests = [
            ( set([]) , set([]) ),
            ( set(['a' ]) , set(['a']) ),
            ( set(['a', 'i' ]) , set(['a']) ),
            ( set(['a', 'i', 'z']) , set([]) ),
            ( set(['j', 'k']) , set(['j', 'k']) ),
            # mention a node that's not a key (only a value)
            ( set(['j', 'k', 'm', 'n']) , set(['j', 'k']) ),
        ]
        for input, expected in  tests:
            got = graph.roots_among(kb, 'e', input)
            self.assertEqual(got, expected)
        
    def test_ancestors(self):
        kb = KB({'apple': {'isa': ['fruit']}, 
              'fruit': {'isa': ['edible']},
              'chocolate': {'isa': ['edible']}, 
             })
        got = set(graph.ancestors(kb, 'isa', 'edible'))
        expected = set(['fruit', 'apple', 'chocolate'])
        self.assertEqual(got, expected)
        # a -> b -> e -> f, g
        #        -> d
        #   -> c
        kb = KB({'alpha': {'E': ['b', 'c']},
              'b': {'E': ['d', 'e']},
              'e': {'E': ['f', 'g']},
              })
        tests = [
            ('g', set(['alpha','b','e'])),
            ('alpha', set([])),
            ('c', set(['alpha'])),
        ]
        for key, expected in tests:
            got = set(graph.ancestors(kb, 'E', key))
            self.assertEqual(got, expected)
            expected2 = expected.union(set([key]))
            got2 = set(graph.ancestors_orequal(kb, 'E', key))
            self.assertEqual(got2, expected2)


class TestDocs(unittest.TestCase):
    def test_docs(self):
        doctest.testmod(graph)



def test():
    suite = unittest.TestLoader().loadTestsFromTestCase(TestGraph)
    suite2 = unittest.TestLoader().loadTestsFromTestCase(TestDocs)
    suite.addTests(suite2)
    unittest.TextTestRunner(verbosity=0).run(suite)

if __name__ == '__main__':
    unittest.main()