from collections import defaultdict
from kb import KB
from typing import List, Iterable, Dict, Set, Union, Any

# The graph functions take a KB and interpret the "page" as being
# a node in a graph and each "attribute" as being an edge with a name
# and list of destinations. Thus the KB describes a graph and we
# can do graph queries on it.
#
# A bit of terminology:
# Root has only outgoing edges. Leaf has only incoming edges.
# The successors of a node are all the ones it points to.
# The predecessors are the reverse direction.
# The descendants of a node are the successors, recursively.
# The ancestors of a node are its predecessors, recursively.

# Check the type annotations like this:
# mypy --py2 graph.py

def ensure_list(value_or_list):
  # type: (Union[str, Iterable[Any]]) -> Iterable[Any]
  """takes a value or list or set, returns a list or set.

  Examples:
  >>> ensure_list('hi')
  ['hi']
  >>> ensure_list(set([1,2,3]))
  set([1, 2, 3])
  """
  if isinstance(value_or_list,list) or isinstance(value_or_list,set):
    return value_or_list
  return [value_or_list]

def predecessors(kb, edge, node):
  # type: (KB, str, str) -> List
  """all predecessors of 'node' via edge type 'edge'"""
  return [kb.normalize_page(k) for (k,v) in kb.items() if kb.normalize_page(node) in v.get(edge,[])]

def references_to(kb, node):
  # type: (KB, str) -> Dict[str, List[str]]
  """all links to 'node'. Returned as a dict with edge type -> list of nodes"""
  ret=defaultdict(lambda:[])  # type: Dict[str, List[str]]
  for page,links in kb.items():
    for e,w in links.items():
      if w==node: ret[e].append(kb.normalize_page(page))
      if hasattr(w,'__iter__'):
        for x in w:
          if x==node: ret[e].append(kb.normalize_page(page))
  return ret

def field_count(kb, nodes):
  # type: (KB, Iterable[str]) -> Dict[str, int]
  """for each field, how many of the nodes have it."""
  ret=defaultdict(lambda:0)  # type: Dict[str, int]
  for n in nodes:
    for e in kb[n]:
      ret[e]+=1
  return ret

def ancestors(kb, edge, node_or_list):
  # type: (KB, str, Union[str, Iterable[str]]) -> Set[str]
  """the set of all node names that have an edge <edge> that points to
    either <node> or someone who points to it."""
  return ancestors_orequal(kb, edge, node_or_list).difference(_normalize_set(kb, ensure_list(node_or_list)))

def ancestors_orequal(kb, edge, node_or_list):
  # type: (KB, str, Union[str, Iterable[str]]) -> Set[str]
  """ancestors(kb, edge, node) + node itself"""
  target = set([kb.normalize_page(k) for k in ensure_list(node_or_list)])  # type: Set[str]
  olen = 0
  while olen!=len(target):
    olen = len(target)
    target = target.union(
      [kb.normalize_page(k) for (k,v) in kb.items()
       if not _normalize_set(kb, v.get(edge, [])).isdisjoint(target)])
  return target

def roots_among(kb, edge, candidates):
  # type: (KB, str, Set[str]) -> Set[str]
  """given a set of names, returns only those that do not have a predecessor in the set."""
  children = set()  # type: Set[str]
  for kids in [ _normalize_set(kb, kb.get_attribute(k,edge,[])) for k in candidates if k in kb]:
    children = children.union(kids)
  return candidates.difference(children)

def leaves_among(kb, edge, candidates):
  # type: (KB, str, Iterable[str]) -> List[str]
  """given a set of names, returns only those that do not have a successor in the set."""
  cands_without_succ = [k for k in candidates if all(x not in candidates for x in kb.get(edge))]
  return [kb.normalize_page(k) for k in cands_without_succ]

def roots(kb, edge, node):
  # type: (KB, str, str) -> Set[str]
  """the set of all node names that have an edge <edge> that points to
    either <node> or someone who points to it, and that have no <edge> pointing to them.
    Edge is assumed to be single-valued."""
  return roots_among(kb, edge, ancestors(kb, edge, node))

def descendants(kb, edge, node_or_list):
  # type: (KB, str, Union[str, Iterable[str]]) -> Set[str]
  accepted=set([])  # type: Set[str]
  toadd=set(ensure_list(node_or_list))  # type: Set[str]
  def grow(seed):
    ret=set([])  # type: Set[str]
    for k in seed:
      nxt = [kb.normalize_page(k) for k in kb.get_attribute(k,edge, [])]
      if not nxt: continue
      ret=ret.union(nxt)
    return ret.difference(seed)
  while len(toadd)>0:
    accepted = accepted.union(toadd)
    toadd = grow(accepted)
  return accepted

def descendants_orequal(kb,edge,node_or_list):
  # type: (KB, str, Union[str, Iterable[str]]) -> Set[str]
  nodes = ensure_list(node_or_list)
  return descendants(kb,edge,nodes).union(set(nodes))

def neighbors(kb, edge, node_or_list):
  # type: (KB, str, Union[str, Iterable[str]]) -> Set[str]
  """ignore edge direction, return the initial set and any node reachable
  by following "edge" links."""
  return descendants_orequal(kb, edge, ancestors_orequal(kb, edge, node_or_list))

def all_sources(kb, edge):
  # type: (KB, str) -> Set[str]
  return set([kb.normalize_page(k) for (k,v) in kb.items() if v.get(edge)!=None])

def all_destinations(kb, edge):
  # type: (KB, str) -> Set[str]
  return set([kb.normalize_page(_get_one(v,edge)) for (k,v) in kb.items() if v.get(edge)!=None])

def _get_one(kb, key):
  # type: (Dict[str, Any], str) -> Any
  """return kb[key], and if that's a list then the first element."""
  x = kb.get(key)
  if isinstance(x, basestring): # Python 3: isinstance(arg, str)
    return x
  try:
    return x[0]
  except TypeError: 
    return x # not a list so just return it

def _normalize_set(kb, lst):
  return set([kb.normalize_page(k) for k in lst])

