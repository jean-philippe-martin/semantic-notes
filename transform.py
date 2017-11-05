"""Transform offers way to add relations to the KB.

The idea is that some attributes have page names as their values,
representing relations: for example, pages may represent people
and the relations may indicate who is related to whom.

Sometimes one relation implies another (child<->parent, for example).
It may be painful to include all implied information in the original
data file, so instead we can use transforms to add them in later.
"""

from collections import namedtuple
from kb import KB
from typing import List, Iterable, Dict, Set, Union, Any, Tuple, Callable, NamedTuple

KB_or_Dict = Union[KB, Dict[str, Dict[str, List[Any]]]]

def addvalue(kb, page, attribute, newvalue):
  # type: (KB_or_Dict, str, str, Any) -> None
  if not kb.has_key(page): kb[page]={}
  if not kb[page].has_key(attribute): kb[page][attribute]=[]
  if not newvalue in kb[page][attribute]:
    kb[page][attribute] += [newvalue]

def addsymmetricalrelation(kb, page1, page2, attribute):
  # type: (KB_or_Dict, str, str, str) -> None
  addvalue(kb, page1, attribute, page2)
  addvalue(kb, page2, attribute, page1)

def getvalues(kb, page, attribute):
  # type: (KB_or_Dict, str, str) -> List[Any]
  if not kb.has_key(page): return []
  if not kb[page].has_key(attribute): return []
  return kb[page][attribute]


## Page selectors: given the kb and a source and target pages,
## return True or False.
PageSelector = Callable[[KB_or_Dict, str, str], bool]

def ofa(whatitmustbe):
  # type: (Any) -> PageSelector 
  """Page selector that picks sources that 'isa' the argument."""
  return lambda kb, src, tgt: whatitmustbe in getvalues(kb, src, 'isa')

def whoisa(whatitmustbe):
  # type: (Any) -> PageSelector
  """Page selector that picks targets that 'isa' the argument."""
  return lambda kb, src, tgt: whatitmustbe in getvalues(kb, tgt, 'isa')

## Page rules: given the kb and a page.
## Return the list of matching pages.
PageRule = Callable[[KB_or_Dict, str], List[Any]]

def the(attribute, pageselector=lambda kb, src, tgt: True):
  # type: (str, PageSelector) -> PageRule
  """a rule that returns the value of that attribute, if any.

  if pageselector is set then only return values for pages that match it."""
  return lambda kb, k: [p for p in kb[k].get(attribute, []) if pageselector(kb, k, p)]

def hasa(attribute):
  # type: (str) -> PageRule
  """A rule that picks everyone who has that attribute."""
  return lambda kb, k: [k] if getvalues(kb, k, attribute) else []

## Page actions: given the kb, a source page and the page being acted on.
## Returns nothing, but updates the kb.
PageAction = Callable[[KB_or_Dict, str, str], None]

def isa(whatitbecomes):
  # type: (Any) -> PageAction
  """an action that adds an (isa,whatitbecomes) relationship."""
  return lambda kb, src, tgt: addvalue(kb, tgt, 'isa', whatitbecomes)

def imtheir(relation):
  # type: (str) -> PageAction
  """an action that adds relation(src) to the target."""
  return lambda kb, src, tgt: addvalue(kb, tgt, relation, src)

def isalsomy(relation):
  # type: (str) -> PageAction
  """an action that adds relation(tgt) to the source."""
  return lambda kb, src, tgt: addvalue(kb, src, relation, tgt)


Rule = namedtuple('Rule', ['pagerule', 'pageactions'])  # type: Tuple[PageRule, List[PageAction]]

def apply_rules(kb, rules):
  # type: (KB_or_Dict, List[Rule]) -> None
  """Modify the kb by applying all the provided rules."""
  for src in kb.keys():
    for rule in rules:
      targets = rule.pagerule(kb, src)
      if not targets: continue
      for action in rule.pageactions:
        for tgt in targets:
          action(kb, src, str(tgt))

