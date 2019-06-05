"""Permissive module loading.

Example::

    >>> from cStringIO import StringIO
    >>> mod = load_permissive_module('testy', StringIO('''
    ... foo = bar
    ... assert foo is None
    ... '''))
    >>> print mod.foo
    None

"""

import new

def load_permissive_module(name, filename):
    if hasattr(filename, 'read'):
        fp = filename
    else:
        fp = open(filename, 'r')
    mod = new.module(name)
    ns = PermissiveDict()
    exec fp.read() in ns
    mod.__dict__.update(ns)
    return mod

class PermissiveDict(dict):
    default = None

    def __getitem__(self, item):
        try:
            return dict.__getitem__(self, item)
        except KeyError:
            return self.default

if __name__ == '__main__':
    import doctest
    doctest.testmod()
