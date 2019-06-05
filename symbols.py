"""
Symbol object.  You can use it like:

    >>> sym = symbols.foo
    >>> sym
    __main__.foo
    >>> sym2 = symbols.foo
    >>> sym is sym2
    True
    >>> foobar = Symbol('foobar')
    >>> foobar
    foobar
    >>> foobar is symbols.foobar
    False
    >>> symbols.foobar
    __main__.foobar
"""

import sys
from UserDict import DictMixin

__all__ = ['symbols', 'Symbol']

class _Symbols(DictMixin):
    def __init__(self):
        self._symbols = {}
    def __getitem__(self, name):
        if name not in self._symbols:
            sym = Symbol(name)
        return self._symbols[name]
    def __setitem__(self, name, value):
        if name in self._symbols:
            raise KeyError(
                "Cannot overwrite symbols %s" % name)
        self._symbols[name] = value
    def __delitem__(self, name):
        ## Dangerous?
        del self._symbols[name]
    def keys(self):
        return self._symbols.keys()
    def __contains__(self, name):
        return name in self._symbols
    def __call__(self, name, module=None):
        name = make_name(name, module=module)
        return self[name]
    def __getattr__(self, attr):
        return self(attr)

symbols = _Symbols()

def make_name(name, module=None, call_level=1):
    if module is None:
        g = get_globals(call_level+1)
        module = g.get('__name__')
    if module:
        name = '%s.%s' % (module, name)
    return name

class Symbol(object):
    symbols = symbols
    def __init__(self, name):
        if name in symbols:
            raise NameError(
                "A symbol by the name %s already exists"
                % name)
        self.name = name
        self.symbols[name] = self
    def __repr__(self):
        return self.name
    ## FIXME: something with pickling

def get_globals(call_level):
    frame = sys._getframe().f_back
    for i in range(call_level):
        if frame is None:
            return {}
        frame = frame.f_back
    if frame:
        return frame.f_globals
        
if __name__ == '__main__':
    import doctest
    doctest.testmod()
    
