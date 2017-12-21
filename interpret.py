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
from kb import KBDict
import kb
from markupsafe import Markup
from markupsafe import soft_unicode
from typing import List, Iterable, Dict, Set, Union, Tuple, Any
from collections import defaultdict


def file(filename):
  # type: (str) -> Tuple[Dict[str,InfoToken], KB]
  """interpret.file(fname) -> parses it into pages and a KB."""
  pages = {}
  big_kb = {}  # type: kb.KBDict
  with codecs.open(filename, encoding='utf-8') as f:
    # disabling mypy for this line because it thinks f isn't iterable (but it is)
    for (title, lines) in split.strings(f):  # type: ignore
      nfo = info(parse.strings(lines), page=title)
      pages[title] = nfo
      nkb = nfo.kb()
      if '' in nkb:
        nkb[title] = nkb['']
        del nkb['']
        if '' in nkb[title]:
          del nkb[title]['']
      big_kb = kb.merge([big_kb, nkb])
  return (pages, KB(big_kb))


class InfoToken(object):
    __metaclass__ = ABCMeta
    @abstractmethod
    def text(self):
        # type: () -> str
        """Textual representation, eg for reading out loud."""
        raise NotImplemented()
    @abstractmethod
    def html(self):
        """html representation, eg. for putting on a web page."""
        raise NotImplemented()
    @abstractmethod
    def value(self):
        """Python value, eg. for using in a program."""
        raise NotImplemented()
    @abstractmethod
    def kb(self):
        # type: () -> KBDict
        """fields for this page -> list of values"""
        raise NotImplemented()


def info(token, page=''):
  # type: (Any, str) -> InfoToken
  """token or string -> InfoToken"""
  if not isinstance(token, Tagged):
    return StringToken(token)
  tag = token.tag.lower()
  if tag=='table':
    return Table(token)
  if tag=='instance-table':
    return InstanceTable(token, page)
  return TagsAreWebOK(token, page)


def split_contents(contents, substring='\n'):
  # type: (List[Any], str) -> Tuple[List[Any], List[Any]]
  """Cut the array in two: elements before, and elements after the substring.

  after = [] only if we didn't find it. Otherwise it contains at least ''
  """
  before = []
  after = []
  for i, x in enumerate(contents):
    if isinstance(x, str) or isinstance(x, unicode):
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
  # type: (List[Any], str) -> List[List[Any]]
  ret=[]  # type: List[List[Any]]
  current = []  # type: List[Any]
  for x in contents:
    if isinstance(x, str) or isinstance(x, unicode):      
      idx = x.find(substring)
      if idx<0:
        current.append(x)
        continue
      # found!
      split = x.split(substring)
      for notlast in split[:-1]:
        current.append(notlast)
        ret.append(current)
        current=[]
      current.append(split[-1])
    else:
      current.append(x)
  if current: ret.append(current)
  return ret


class StringToken(InfoToken):
  def __init__(self, txt):
    self._text = str(txt)
    self._tag = ''
    self._value = parse.unit_perhaps(txt)
  def text(self):
    return self._text
  def html(self):
    return self._text
  def value(self):
    return self._value
  def kb(self):
    return {}


class Table(InfoToken):
  """The info, represented as a table.

  Sample:

  `table title of my table
  name, age
  Bob, 25
  Charlie, 22
  """
  def __init__(self, thetagged, page=''): # the tagged that holds the table, that is
    # page that we're interpreting
    self._page = page
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
    header_line = ''.join([info(x).text() for x in self._header_contents])
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


class InstanceTable(Table):
  """When the current page is a category, use this to add instances quickly.

  The first row is the headers, and the first column must be the page name.
  So in the sample below we end up with a page for "earth", and it has properties
  "color" (blue) and "isa" (planet). 

  You can still describe those pages normally somewhere else, the information
  will get merged.

  Sample:

  [planet]
  `table data about planets
  name, color
  earth, blue
  mars, red
  """
  def kb(self):
    ret = {}
    header_components = split_all(self._header_contents, ',')
    headers = [''.join(h).strip() for h in header_components]
    for row_contents in self._rows_contents:
      row_components = split_all(row_contents, ',')
      row = [''.join([info(x).text() for x in cl]).strip() for cl in row_components]
      row_name = ''
      for i, col in enumerate(row):
        if i==0:
          row_name = col
          if not row_name:
            # ignore the row if it has no name.
            break
          ret[row_name]={'isa': [self._page]}
          continue
        if not headers[i] in ret[row_name]:
          ret[row_name][headers[i]] = []
        ret[row_name][headers[i]] += [info(col).value()]
    return ret
    

class TagsAreWebOK(InfoToken):
    """Here we're transforming any tag into an html tag.

    So for example `b(planet) becomes <b>planet</b>. Clearly this isn't always
    the best choice, but we have to start somewhere."""
    __metaclass__ = ABCMeta
    def __init__(self, page, pagename=''):
      self._page = pagename
      self._kb={}
      if not isinstance(page, Tagged):
        self._tag=''
        self._text=str(page)
        self._html=str(page)
        self._value=page
      else:
        self._tag = page.tag
        kids = [info(x, self._page) for x in page.contents]
        self._text = ''.join([k.text() for k in kids])
        if len(kids)==1:
          # special case, keep the value
          self._value = kids[0].value()
        else:
          self._value = [k.value() for k in kids]
        self._html = u''.join([k.html() for k in kids])
        self._kb=kb.merge([x.kb() for x in kids if x.kb()])
        # page '' means "current page"
        # our tag is the attribute, and we store the value there.
        if not '' in self._kb:
          self._kb[''] = defaultdict(list)
        self._kb[''][self._tag].append(self._value)
        if self._tag:
          self._text = self._tag + ': ' + self._text
          if self._tag == 'img':
            # image, special case.
            # static content is held in "static/"
            # (as opposed to "data" which holds data we don't serve)
            self._html = Markup(u'<%s width="100%%" src="/static/{0}">' % (self._tag)).format(soft_unicode(self._html))
          else:
            # normal case
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




