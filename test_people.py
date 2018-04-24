import doctest
import interpret
import unittest
import people

class TestPeople(unittest.TestCase):
  "Tests for people.py."

  def test_people(self):
    # load the data
    pages, kb = interpret.file('testdata/people.txt')
    people.fixup(kb)
    # inferred from the fact he's a son
    self.assertTrue('man' in kb['Bob']['isa'])
    # inferred from known gender and the fact that Joe's married to her.
    self.assertTrue('Joe' in kb['Jill']['husband'])
    # Jill is a woman (since she's a wife), and Ahab is her brother,
    # so Jill is Ahab's sister
    self.assertTrue('Jill' in kb['Ahab']['sister'])
    # Bob -[mother]-> Jill -[brother]-> Ahab
    # So Ahab is Bob's uncle
    self.assertTrue('Ahab' in kb['Bob']['uncle'])
    

if __name__ == '__main__':
    unittest.main()