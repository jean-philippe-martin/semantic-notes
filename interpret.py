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
        raise NotImplemented()
    @abstractmethod
    def html(self):
        raise NotImplemented()
    @abstractmethod
    def kb(self):
        """fields for this page -> list of values"""
        raise NotImplemented()


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
        kids = [TagsAreWebOK(x) for x in page.contents]
        self._text = ''.join([k.text() for k in kids]).replace('\n', ' ')
        if len(kids)==1:
          # special case, keep the value
          self._value = kids[0]._value
        else:
          self._value = self._text
        self._html = u''.join([k.html() for k in kids]).replace(u'\n', u' ')
        self._kb={k._tag: [k._value] for k in kids if k._tag}
        if self._tag:
          self._text = self._tag + ': ' + self._text
          self._html = Markup(u'<%s>{0}</%s>' % (self._tag, self._tag)).format(soft_unicode(self._html))
    def text(self):
      return self._text
    def html(self):
      return self._html
    def kb(self):
      return self._kb
    def __str__(self):
      return self.text()


def file(filename):
  # type: (str) -> Tuple[Dict[str,TagsAreWebOK], KB]
  pages = {}
  kb = {}
  with codecs.open(filename, encoding='utf-8') as f:
    # disabling mypy for this line because it thinks f isn't iterable (but it is)
    for (title, lines) in split.strings(f):  # type: ignore
      info = TagsAreWebOK(parse.strings(lines))
      pages[title] = info
      kb[title] = info.kb()
  return (pages, KB(kb))


