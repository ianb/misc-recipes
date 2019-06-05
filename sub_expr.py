"""
Evaluate strings similar to PHP or other languages.  Do things like:

   name = raw_input('Your name?')
   print 'Hi $name!'
   print 'Your name is spelled like: ${' '.join(list(name))}'

Requires Python 2.4 (or a backport of the Python 2.4 string module)

'}' is *not* allowed inside expressions, so you can't do something
like '${{"a": "A"}[value]}', also expressions cannot span lines.
Otherwise nearly anything is allowed.
"""

import string
import inspect
import re

class ExprEval(object):

    def __init__(self, parent_global, parent_local):
        self.parent_global = parent_global
        self.parent_local = parent_local

    def __getitem__(self, item):
        return eval(item, self.parent_global, self.parent_local)

class LaxTemplate(string.Template):
    # This change of pattern allows for anything in braces, but
    # only identifiers outside of braces:
    pattern = re.compile(r"""
    \$(?:
      (?P<escaped>\$)             |   # Escape sequence of two delimiters
      (?P<named>[_a-z][_a-z0-9]*) |   # delimiter and a Python identifier
      {(?P<braced>.*?)}           |   # delimiter and a braced identifier
      (?P<invalid>)                   # Other ill-formed delimiter exprs
    )
    """, re.VERBOSE | re.IGNORECASE)

def e(s):
    """
    Evaluates the given string in the caller's context, using the
    template syntax like $a, and ${a+b}.

        >>> e('1+1=${1+1}')
        '1+1=2'
        >>> name = 'Bob'
        >>> e('Hi $name')
        'Hi Bob'
        >>> e('Hi ${name.lower()}')
        'Hi bob'
        >>> e('Your name is spelled: ${" ".join(list(name.upper()))}')
        'Your name is spelled: B O B'
    """
    parent_frame = evaler = None
    try:
        parent_frame = inspect.stack(1)[1][0]
        evaler = ExprEval(parent_frame.f_globals, parent_frame.f_locals)
        tmpl = LaxTemplate(s)
        return tmpl.substitute(evaler)
    finally:
        del parent_frame
        del evaler.parent_global
        del evaler.parent_local
        del evaler

if __name__ == '__main__':
    import doctest
    doctest.testmod()
    
