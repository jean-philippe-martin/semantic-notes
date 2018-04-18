"""Transform rules for people."""

from transform import *

def fixup(kb):
  # type: (KB_or_Dict) -> None
  """Add relations that can be inferred from what's there.

  We expect the input data to contain a possibly incomplete
  set of parental relations. For example, it may say that X is the son of Y,
  but missing the information that Y is their father. This fixup
  puts in everything that can be logically deduced from what's there.

  The tags we expect are:
  son, daughter, father, mother, parent, married_to, child, aunt, uncle
  The categories:
  man, woman, parent

  So for example:
  [bob]
  `isa(man)
  `son(joe)
  means: Bob is in the "man" category, and his son is Joe.
  This code will add that Bob is Joe's father (if not already stated).

  There is of course a lot more we could do (granddaughter, etc.)
  but at some point it's better if those are computed on the fly
  instead of all added to the graph.
  """
  rules = []
  # dads are men, moms are women. Both are parents.
  rules.append( Rule(the('father'), [isa('man'), isalsomy('parent')]) )
  rules.append( Rule(the('mother'), [isa('woman'), isalsomy('parent')]) )
  # sisters are women, brothers are men. Similarly, aunts and uncles.
  rules.append( Rule(the('sister'), [isa('woman')]) )
  rules.append( Rule(the('brother'), [isa('man')]) )
  rules.append( Rule(the('aunt'), [isa('woman')]) )
  rules.append( Rule(the('uncle'), [isa('man')]) )
  # have a son? You're their parent. Same for daughter.
  rules.append( Rule(the('son'), [imtheir('parent')]))
  rules.append( Rule(the('daughter'), [imtheir('parent')]))
  # male parents are fathers, etc. This is in case the data only has 'parent'
  rules.append( Rule(the('parent', whoisa('man')), [isalsomy('father')]) )
  rules.append( Rule(the('parent', whoisa('woman')), [isalsomy('mother')]) )
  # sons are men, etc.
  rules.append( Rule(the('son'), [isa('man')]) )
  rules.append( Rule(the('daughter'), [isa('woman')]) )
  # create married_to relation.
  rules.append( Rule(the('husband'), [isalsomy('married_to')]) )
  rules.append( Rule(the('wife'), [isalsomy('married_to')]) )
  # add the reverse direction if it's not already there.
  rules.append( Rule(the('married_to'), [imtheir('married_to')]) )
  # married_to also means husband or wife once we know the gender.
  rules.append( Rule(the('married_to', ofa('man')), [imtheir('husband')]) )
  rules.append( Rule(the('married_to', ofa('woman')), [imtheir('wife')]) )
  # if you're the parent of someone, then you are categorized as a parent.
  rules.append( Rule(the('parent'), [isa('parent')]))
  # reverse-parent is called "child"
  rules.append( Rule(the('parent'), [imtheir('child')]))
  # add backedge for siblings
  rules.append( Rule(the('sister', ofa('woman')), [imtheir('sister')]))
  rules.append( Rule(the('brother', ofa('woman')), [imtheir('sister')]))
  rules.append( Rule(the('sister', ofa('man')), [imtheir('brother')]))
  rules.append( Rule(the('brother', ofa('man')), [imtheir('brother')]))
  # The sisters of my parents are my aunts
  rules.append( Rule(chain(['parent', 'sister']), [isalsomy('aunt')]))
  rules.append( Rule(chain(['parent', 'brother']), [isalsomy('uncle')]))

  apply_rules(kb, rules)
