"""splits a long text file into a series of sections,
delimited by [titles]. 

Example:

>>> list(split.strings('[title]\\nbody'.split()))
[('title', ['body'])]

"""

from typing import List, Iterable, Dict, Set, Union, Tuple

def strings(lines):
    # type: (Iterable[str]) -> Iterable[Tuple[str, List[str]]]
    """splits the lines into (title, lines) sections."""
    ret=[]  # type: List[str]
    title=''
    ready=False
    for l in lines:
        if len(l)>2 and l[0]=='[' and l[-1]==']':
            if ready:
                yield (title, ret)
            title=l[1:-1]
            ret=[]
            ready=True
        else:
            ret.append(l)
    if ready:
        yield (title, ret)