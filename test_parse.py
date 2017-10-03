import doctest
import parse
from parse import Tagged
import unittest

class TestParse(unittest.TestCase):
  "Tests for parse.py."

  def test_no_crash(self):
    x = parse.string('hi')
    y = parse.string('hi `b(world)')
    z = parse.string('hi `b(`i(small) world)')
    z = parse.string('`very(`very `deep(thoughts) `/)')

  def test_backtick_legal_in_tag(self):
    x = parse.string('`big`hello(world)')
    self.assertEqual(len(x.contents), 1)
    self.assertEqual(x.contents[0].tag, 'big`hello')
    self.assertEqual(str(x),'`big`hello(world)')

  def test_strings_together(self):
    x = parse.string('hi')
    self.assertEqual(len(x.contents), 1)
    x = parse.string('hi world')
    self.assertEqual(len(x.contents), 1)
    x = parse.string('hi\nbig\nworld')
    self.assertEqual(len(x.contents), 1)
    x = parse.string('TITLE\n\nsome text\nblabla\nfinal line\n')
    self.assertEqual(len(x.contents), 1)

  def test_first_tag_empty(self):
    x = parse.string('hello\nthere')
    self.assertEqual(x.tag, '')

  def test_paren_tag(self):
    x = parse.string('hello `b(world)')
    self.assertEqual(len(x.contents), 2)
    self.assertEqual(x.contents[0], 'hello ')
    self.assertEqual(x.contents[1].tag, 'b')
    self.assertEqual(x.contents[1].contents[0], 'world')

  def test_block_tag(self):
    for s in [
      'hello `b(world)',
      'hello `b world`/',
      'hello `b world`/ ',
      'hello `b world`/\n',
      'hello `b\nworld`/']:
        x = parse.string(s)
        self.assertEqual(len(x.contents), 2)
        self.assertEqual(x.contents[0], 'hello ')
        self.assertEqual(x.contents[1].tag, 'b')
        self.assertEqual(x.contents[1].contents[0], 'world')

  def test_strings(self):
    ss=['hello', '\b(world)']
    x=parse.strings(ss)
    self.assertEqual(len(x.contents), 2)
    ss=('hello', '\b(world)')
    x=parse.strings(ss)
    self.assertEqual(len(x.contents), 2)
    ss=[x for x in ('hello', '\b(world)')]
    x=parse.strings(ss)
    self.assertEqual(len(x.contents), 2)

class TestDocs(unittest.TestCase):
    def test_docs(self):
        doctest.testmod(parse, globs={'parse':parse})

if __name__ == '__main__':
    unittest.main()