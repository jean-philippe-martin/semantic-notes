import doctest
import kb
import unittest

class TestKB(unittest.TestCase):
  "Tests for kb.py."

  def test_get(self):
    d={'a': {'b': 'c'}}
    x = kb.KB(d)
    self.assertEqual(x['a']['b'], 'c')
    self.assertEqual(x.get('a', 'default')['b'], 'c')
    self.assertEqual(x.get('z', {'b': 'x'})['b'], 'x')

  def test_is_same_page(self):
    d={'a': {'b': 'c'}}
    x = kb.KB(d)
    self.assertEqual(x.is_same_page('a', 'a'), True)
    self.assertEqual(x.is_same_page('a', 'z'), False)

  def test_get_attribute(self):
    d={'a': {'b': 'c'}}
    x = kb.KB(d)
    self.assertEqual(x.get_attribute('a', 'b'), 'c')
    self.assertEqual(x.get_attribute('a', 'z'), None)
    self.assertEqual(x.get_attribute('z', 'z'), None)

  def test_keys(self):
    d={'a': {'b': 'c'}, 'x': {'y': 'z'}}
    x = kb.KB(d)
    self.assertEqual(sorted(list(x.keys())), ['a','x'])

  def test_aka(self):
    d={'a': {'b': 'c', 'aka': ['alpha']}}
    x = kb.KB(d)
    self.assertEqual(x.get_attribute('alpha','b'), 'c')
    self.assertEqual(x['alpha']['b'], 'c')

  def test_has_key(self):
    d={'a': {'b': 'c', 'aka': ['alpha']}}
    x = kb.KB(d)
    self.assertEqual(x.has_key('a'), True)
    self.assertEqual(x.has_key('alpha'), True)

  def test_case_insensitive(self):
    d={'bob': {'w': 'guy'}, 'BOB': {'w': 'abbreviation'}, 'Bobby': {'w': 'name'},
    'Ace': {'w': '1'}, 'aCe': {'w': '2'}, 'acE': {'w': '3'}}
    x = kb.KB(d)
    self.assertEqual(x.get_attribute('bob','w'), 'guy')
    self.assertEqual(x.get_attribute('BOB','w'), 'abbreviation')
    self.assertEqual(x.get_attribute('Bob','w'), 'guy')
    self.assertEqual(x['bobby']['w'], 'name')
    self.assertEqual(x['BOBby']['w'], 'name')
    self.assertEqual(x.is_same_page('bobby', 'BobbY'), True)
    self.assertEqual(x.is_same_page('bob', 'BOB'), False)
    self.assertEqual(x.get_attribute('Ace','w'), '1')
    self.assertEqual(x.get_attribute('aCe','w'), '2')
    self.assertEqual(x.get_attribute('acE','w'), '3')
    self.assertEqual(x.is_same_page('Ace', 'acE'), False)

  def test_case_insensitive_and_aka(self):
    d={'bob': {'w': 'guy', 'aka': ['Bobby', 'foo', 'roar']}, 'BOB': {'w': 'abbreviation'}, 
       'bobbY': {'w': 'other guy'}, 'foO': {'w': 'Mr.T'}}
    x = kb.KB(d)
    self.assertEqual(x.is_same_page('bob', 'Bobby'), True)
    self.assertEqual(x.is_same_page('bob', 'ROAR'), True)
    self.assertEqual(x.is_same_page('bob', 'foo'), True)
    self.assertEqual(x.is_same_page('bob', 'foO'), False)
    # 'FOO' could be redirected to either bob or foO, spec doesn't say
    

class TestDocs(unittest.TestCase):
    def test_docs(self):
        doctest.testmod(kb)


if __name__ == '__main__':
    unittest.main()