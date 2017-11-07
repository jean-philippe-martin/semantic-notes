import doctest
import interpret
from parse import units
import unittest
import graph
from kb import unique

class TestPlanets(unittest.TestCase):
  "Tests for parse.py."

  def test_planets(self):
    # shorthand
    kg = units.kg
    # load the data
    pages, kb = interpret.file('samples/planets.txt')
    # The KB holds the quantities with units, so we can combine them
    # meaningfully even though one is in kg and the other in "earth_mass".
    got = unique(kb['the earth']['mass']) + unique(kb['mars']['mass'])
    self.assertTrue(6E24*kg < got < 7E24*kg)

  def test_sum(self):
    # shorthand
    kg = units.kg
    # load the data
    pages, kb = interpret.file('samples/planets.txt')
    # grab everything that's a planet
    planets = graph.ancestors(kb, 'isa', 'planet')
    # sum their mass
    total_mass = sum(unique(kb[x]['mass']) for x in planets)
    # we don't have all the planets in the sample... once we do,
    # we'll have to update this test!
    self.assertTrue(6E24*kg < total_mass < 8E24*kg)

  def test_split(self):
    foo=['abc', 12, 'd\ne', 13]
    b,a = interpret.split_contents(foo, '\n')
    self.assertEquals(b, ['abc', 12, 'd'])
    self.assertEquals(a, ['e', 13])
    foo=['abc', 12, 'de']
    b,a = interpret.split_contents(foo, '\n')
    self.assertEquals(b, foo)
    self.assertEquals(a, [])
    foo=['abc', 12, '\n']
    b,a = interpret.split_contents(foo, '\n')
    self.assertEquals(b, ['abc',12,''])
    self.assertEquals(a, [''])

  def test_split_all_one(self):
    foo=['abc', 12, 'd\ne', 13]
    ret = interpret.split_all(foo, '\n')
    b=ret[0]
    a=ret[1]
    self.assertEquals(b, ['abc', 12, 'd'])
    self.assertEquals(a, ['e', 13])
    foo=['abc', 12, 'de']
    ret = interpret.split_all(foo, '\n')
    b=ret[0]
    self.assertEquals(b, foo)
    self.assertEquals(len(ret), 1)
    foo=['abc', 12, '\n']
    ret = interpret.split_all(foo, '\n')
    b=ret[0]
    a=ret[1]
    self.assertEquals(b, ['abc', 12])
    self.assertEquals(a, [''])
    
  def test_split_all_multi(self):
    foo=['abc', 12, 'd\ne', 13, '\n', 14]
    parts = interpret.split_all(foo, '\n')
    self.assertEquals(parts[0], ['abc', 12, 'd'])
    self.assertEquals(parts[1], ['e', 13])
    self.assertEquals(parts[2], ['', 14])
    self.assertEquals(len(parts), 3)

  def test_table(self):
    p,kb=interpret.file('samples/table.txt')

if __name__ == '__main__':
    unittest.main()