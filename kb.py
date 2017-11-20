# "Knowledge Base"
from typing import List, Iterable, Dict, Set, Union, Any
from collections import defaultdict

# Check the type annotations like this:
# mypy --py2 graph.py

# The type that goes into a KB, and what a KB
# still mostly feels like (modulo the few added features).
KBDict = Dict[str, Dict[str, List[Any]]]


class KB(dict):
  """A very simple "knowledge base".

  It's organized in pages. Each page has a name and a set of key/value pairs.
  The keys are called "attributes" of the page.
  Each value is a list (possibly with a single element).

  The KB can be used like a normal dict, but it offers a few convenience
  features and includes the idea that pages may have multiple names.
  To set an alternate name for a page, set its 'aka' property (see tests).
  Page lookup is also case-insensitive:
  if you have pages 'aaa' and 'AAA' then a lookup for 'AAA' will return
  the latter, but a lookup for 'aAA' will return the former.
  Two names refer to the same page if and only if normalize_page returns
  the same value for both.

  Examples:

  >>> ppl={'John':{'eye_color': ['blue']}}
  >>> k=KB(ppl)
  >>> k['john']['eye_color']
  ['blue']

  >>> ppl['Bob']={'aka': ['Bobby tables'], 'eye_color': ['brown']}
  >>> k=KB(ppl)
  >>> k['bobby tables']['eye_color']
  ['brown']
  >>> k.get_attribute('bobby tables', 'eye_color')
  ['brown']
  """

  def __init__(self, dict_of_dict):
    # type: (KBDict) -> None
    self.aka = {}  # type: Dict[str, str]
    self.update(dict_of_dict)
    self._fill_aka()

  def __getitem__(self, key):
    # type: (str) -> Dict[str, List[Any]]
    return dict.__getitem__(self,self.normalize_page(key))

  def get(self, key, default=None):
    # type: (str, Any) -> Dict[str, List[Any]]
    return dict.get(self,self.normalize_page(key), default)

  def has_key(self, page):
    # type: (str) -> bool
    return dict.has_key(self, self.normalize_page(page))

  def normalize_page(self, key):
    # type: (str) -> str
    """page name or alias -> page name"""
    if self.aka.has_key(key):
      return self.aka[key]
    if dict.has_key(self, key):
      return key
    # If the page name has capitals, and we do too but in different places,
    # should still find the page name.
    # If the page doesn't exist, return the name unmodified.
    return self.aka.get(key.lower(), key)

  def is_same_page(self, a, b):
    # type: (str, str) -> bool
    """true if a,b are names of the same page, even if aliases."""
    return self.normalize_page(a) == self.normalize_page(b)

  def get_attribute(self, key, attribute, default=None):
    # type: (str, str, List[Any]) -> List[Any]
    """kb[key][attribute], or None if either's missing."""
    page = self.get(key, None)
    if not page: return default
    return page.get(attribute, default)
  
  def get_unique_attribute(self, key, attribute, default=None):
    # type: (str, str, List[Any]) -> Any
    """kb[key][attribute][0], or None if either's missing."""
    return unique(self.get_attribute(key,attribute,default))

  def _fill_aka(self):
    # type: () -> None
    for k,v in dict.items(self):
      a = v.get("aka", [])
      for b in a:
        if self.aka.get(b)!=None:
          print(str(b)+" is defined twice: as "+self.aka[b] + " and "+k)
          continue
        self.aka[b]=k
    # put in 'baby' as an aka for the 'Baby' page, *unless* 'baby' is already
    # a registered aka for something else.
    for k in dict.keys(self):
      if not self.aka.has_key(k.lower()): 
        self.aka[k.lower()] = k
      a = self.get(k).get("aka", [])
      for b in a:
        if not self.aka.has_key(b.lower()):
          self.aka[b.lower()] = k


KB_or_Dict = Union[KB, KBDict]


def merge(kblist):
  # type: (List[KBDict]) -> KBDict
  """Merges the dicts together into a single one by appending all the keys.

  Example:
  >>> a = {'mars': {'isa': ['planet']}}
  >>> b = {'mars': {'color': ['red']}}
  >>> sorted(merge([a,b])['mars'].keys())
  ['color', 'isa']

  """
  ret = {}  # type: KBDict
  for kb in kblist:
    for k, v in kb.items():
      if k not in ret:
        ret[k] = defaultdict(list)
      for attrib, values in v.items():
        ret[k][attrib] += values
  return ret


def unique(value):
  """Check that there is only one value in the list, and return it.

  >>> kb = KB({'John':{'eye_color': ['blue']}})
  >>> unique(kb.get_attribute('John', 'eye_color'))
  'blue'

  This is handy in the context of KB, where everything's a list but
  it's common to expect that there's only one value. 
  """
  if not value: return None
  if len(value)!=1:
    raise ValueError('Expected a single value, got multiple (%s)' % len(value))
  return value[0]
 