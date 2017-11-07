"""Basic code to parse a file into html pages and a KB.

Examples:

>>> pages, kb = interpret.file('planets.txt')
>>> pages['Neptune']
u'Neptune is great, blablabla'
>>> kb['neptune']
{'isa': ['planet'], 'diameter': ['49500 km']}
"""

from abc import abstractmethod
from abc import ABCMeta
import codecs
from parse import Tagged
import split
import parse
from kb import KB
from markupsafe import Markup
from markupsafe import soft_unicode
from typing import List, Iterable, Dict, Set, Union, Tuple, Any


class InfoToken(object):
    __metaclass__ = ABCMeta
    @abstractmethod
    def text(self):
        """Textual representation, eg for reading out loud."""
        raise NotImplemented()
    @abstractmethod
    def html(self):
        """html respresentation, eg. for putting on a web page."""
        raise NotImplemented()
    @abstractmethod
    def value(self):
        """Python value, eg. for using in a program."""
        raise NotImplemented()
    @abstractmethod
    def kb(self):
        """fields for this page -> list of values"""
        raise NotImplemented()


def split_contents(contents, substring='\n'):
  """Cut the array in two: elements before, and elements after the substring.

  after = [] only if we didn't find it. Otherwise it contains at least ''
  """
  before = []
  after = []
  for i, x in enumerate(contents):
    if isinstance(x, basestring):
      idx = x.find(substring)
      if idx<0:
        before.append(x)
        continue
      # found!
      upto = x[:idx]
      before.append(upto)
      after.append(x[idx+len(substring):])
      after += contents[i+1:]
      break
    else:
      before.append(x)
  return before, after


def split_all(contents, substring='\n'):
  ret=[]  # type: List[List[Any]]
  current = []  # type: List[Any]
  for x in contents:
    if isinstance(x, basestring):
      idx = x.find(substring)
      if idx<0:
        current.append(x)
        continue
      # found!
      upto = x[:idx]
      if upto: current.append(upto)
      ret.append(current)
      current=[]
      current.append(x[idx+len(substring):])
    else:
      current.append(x)
  if current: ret.append(current)
  return ret


def info(token):
  """token or string -> InfoToken"""
  if not isinstance(token, Tagged):
    return StringToken(token)
  tag = token.tag.lower()
  if tag=='table':
    return Table(token)
  return TagsAreWebOK(token)


class StringToken(InfoToken):
  def __init__(self, txt):
    self._text = str(txt)
    self._tag = ''
    self._value = txt
  def text(self):
    return self._text
  def html(self):
    return self._text
  def value(self):
    return self._value
  def kb(self):
    return {}


class Table(InfoToken):
  """The info, represented as a table."""
  def __init__(self, thetagged): # the tagged that holds the table, that is
    self._tag = ''
    self._value = None
    title, rest = split_contents(thetagged.contents)
    self._title_contents = title
    header, rest = split_contents(rest)
    self._header_contents = header
    self._rows_contents = []
    while rest:
      row, rest = split_contents(rest)
      self._rows_contents.append(row)
  def value(self):
    return None
  def text(self):
    title_line = ''.join([info(x).text() for x in self._title_contents])
    header_line = ''.join([info(x).text() for x in self._title_contents])
    ret = title_line + '\n' + header_line
    for row_contents in self._rows_contents:
      ret = ret + '\n' + ''.join([info(x).text() for x in row_contents])
    return ret
  def html(self):
    title_line = ''.join([info(x).html() for x in self._title_contents])
    ret = title_line
    ret += Markup('\n<table border="1" style="border-collapse: collapse;">')
    ret += Markup('\n  <tr>')
    header = split_all(self._header_contents, ',')
    for h in header:
      # h is a content list
      h_html = ''.join(info(x).html() for x in h) 
      ret += Markup('<th>{0}</th>').format(h_html)
    ret += Markup('</tr>')
    for row_contents in self._rows_contents:
      row = split_all(row_contents, ',')
      ret += Markup('\n  <tr>')
      for r in row:
        r_html = ''.join(info(x).html() for x in r) 
        ret += Markup('<td>{0}</td>').format(r_html)
      ret += Markup('</tr>')
    ret += Markup('\n</table>')
    return ret
  def kb(self):
    return {}
    

class TagsAreWebOK(InfoToken):
    """Here we're transforming any tag into an html tag.

    So for example `b(planet) becomes <b>planet</b>. Clearly this isn't always
    the best choice, but we have to start somewhere."""
    __metaclass__ = ABCMeta
    def __init__(self, page):
      self._kb={}
      if not isinstance(page, Tagged):
        self._tag=''
        self._text=str(page)
        self._html=str(page)
        self._value=page
      else:
        self._tag = page.tag
        kids = [info(x) for x in page.contents]
        self._text = ''.join([k.text() for k in kids])
        if len(kids)==1:
          # special case, keep the value
          self._value = kids[0].value()
        else:
          self._value = [k.value() for k in kids]
        self._html = u''.join([k.html() for k in kids])
        self._kb={k._tag: [k.value()] for k in kids if k._tag}
        if self._tag:
          self._text = self._tag + ': ' + self._text
          self._html = Markup(u'<%s>{0}</%s>' % (self._tag, self._tag)).format(soft_unicode(self._html))
    def text(self):
      return self._text
    def html(self):
      return self._html
    def kb(self):
      return self._kb
    def value(self):
      return self._value
    def __str__(self):
      return self.text()


def file(filename):
  # type: (str) -> Tuple[Dict[str,TagsAreWebOK], KB]
  pages = {}
  kb = {}
  with codecs.open(filename, encoding='utf-8') as f:
    # disabling mypy for this line because it thinks f isn't iterable (but it is)
    for (title, lines) in split.strings(f):  # type: ignore
      nfo = info(parse.strings(lines))
      pages[title] = nfo
      kb[title] = nfo.kb()
  return (pages, KB(kb))


