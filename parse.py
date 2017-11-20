"""
A parser. The format is deliberately simple,
there is only one special character: `
every tag starts with the special character.

This way the parser doesn't even need to know what
the tags are, it just tells you what has what.
Then you interpret the tags in whatever way is appropriate.

There are two ways of using the tags:

`bold(I'm guessing this text will show up in bold)

or

`bold Guess what this will look like`/

Note that for the second  syntax there must be a space
or end of line after the tag name. If you put:
`boldThis text`/ then the parser will think that the tag name
is "boldThis". Same after the closing tag.

If you want the inner text to start with a space then add a second
space after the tag-delimiting one.

The output is a Tagged. Each Tagged contains the name of the tag,
and a list of either basestring (with the contents), or Tagged.

For example:

>>> parse.string('Hello world')
Tagged('', ['Hello world'])

and with a tag:

>>> parse.string('Hello `b(world)')
Tagged('', ['Hello ', Tagged('b', ['world'])])

nested tags result in nested Tagged objects, like so:

>>> parse.string('Hello `b(`i(cruel) world)')
Tagged('', ['Hello ', Tagged('b', [Tagged('i', ['cruel']), ' world'])])

Tagged has a str() method that prints the text as it was in the input,
and __repr__() that prints it python-style as above.

So for example:
>>> str(parse.string('hello `b(world)'))
'hello `b(world)'
>>> str(parse.string('`b bold`/ '))
'`b bold`/ '
"""
from abc import abstractmethod
from abc import ABCMeta
import pint
from typing import List, Iterable, Dict, Set, Union, Any
import re

units = pint.UnitRegistry()
units.define('earth_mass = 5.972E24 * kg')

## User interface

# parse.string("hello `b(world)")
def string(s):
    # type: (str) -> Tagged
    """One long string (possibly with line returns) -> a Tagged tree."""
    return _parse(LinesHolder([s]), mytag='', parens=False)

def strings(ss):
    # type: (Iterable[str]) -> Tagged
    """String enumerable (or open file) -> a Tagged tree."""
    return _parse(LinesHolder(ss), mytag='', parens=False)

def file(filename):
    """File name -> a Tagged tree."""
    with open(filename, 'rt') as f:
        return strings(f)

class Tagged:
    """Represents a tag in the document."""
    def __init__(self, tag, contents, paren=True, line=None):
        # type: (str, List[Union[str, Tagged]], bool, int) -> None
        self.tag = tag
        self.contents = contents
        self.line = line
        self.paren = paren

    def __repr__(self):
        return 'Tagged(%s, %s)' % (self.tag.__repr__(), self.contents)

    def __str__(self):
        inner = ''.join(str(x) for x in self.contents)
        if (self.tag==''): return inner
        if self.paren:
            return '`'+self.tag + '(' + inner + ')'
        return '`%s %s`/ ' % (self.tag, inner)


def unit_perhaps(txt):
    # type: (str) -> Any
    """Return a Pint Quantity if we recognize a unit, or pass through unchanged."""
    try:
        txt = units.parse_expression(txt)
    except:
        pass
    return txt


## Internal implementation

def _min_non_negative(a,b):
    # type: (int, int) -> int
    if a<0: return b
    if b<0: return a
    return min(a, b)

def _parse(lh, mytag, parens):
    # type: (LinesHolder, str, bool) -> Tagged
    """Parse the text, one tag at a time, recursively."""
    ret=[]  # type: List[Union[str, Tagged]]
    parenDepth = 1
    while lh.hasNext():
        s = lh.getCurrent()
        i = s.find('`')
        if (parens and i!=0):
            # check if we close first
            tgt=i
            if (tgt<0): tgt=len(s)
            for x in range(tgt):
                if (s[x]==')'):
                    parenDepth-=1
                    if (parenDepth==0):
                        # found the end
                        if x>0: ret.append(unit_perhaps(s[:x]))
                        lh.setCurrent(s[x+1:])
                        return Tagged(mytag, ret, paren=True)
                if (s[x]=='('):
                    parenDepth += 1
        if (i<0):
            ret.append(unit_perhaps(s))
            lh.nextLine()
            continue
        if (i>0):
            txt=unit_perhaps(s[:i])
            ret.append(txt)
            lh.setCurrent(s[i:])
            continue
        # we're sitting just before a tag
        op=s.find('(')
        sp=_min_non_negative(s.find(' '), s.find('\n'))
        parenthese = op>=0 and (sp<0 or op<sp)
        tag=''
        # if both are -1 that means the tag runs against the end of line
        if op<0 and sp<0:
            tag = s[1:]
            parenthese=False
        elif parenthese:
            tag = s[1:op]
        else:
            tag = s[1:sp]
        if tag=='/':
            # closing tag. Let's stop the parsing.
            lh.setCurrent(s[3:])
            break
        lh.setCurrent(s[len(tag)+2:])
        inner = _parse(lh, tag, parenthese)
        ret.append(inner)
    return Tagged(mytag,ret, paren=parens)


class LinesHolder:
    """mutable holder of lines"""
    def __init__(self,lines):
        """expects a list or generator of strings."""
        self.current = None
        # list -> generator
        if isinstance(lines, list) or isinstance(lines, tuple):
            lines=lines.__iter__()
        self.lines = lines
        self.nextLine()
    def getCurrent(self):
        # type: () -> str
        """Returns the current line (or None if past the end)."""
        if not self.hasNext():
            return ''
        return self.current
    def nextLine(self):
        # type: () -> None
        """Move to the next line."""
        try:
            self.current = self.lines.next()
        except StopIteration:
            self.current = None
    def setCurrent(self, line):
        # type: (str) -> None
        """Go to next line if given '', otherwise change the current line."""
        if line == '':
            self.nextLine()
        else:
            self.current = line
    def hasNext(self):
        # type: () -> bool
        return self.current != None