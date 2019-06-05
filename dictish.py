"""dictish: Lets you use classes like dicts:

    >>> class foo(dictish):
    ...     a = 1
    ...     b = 2
    >>> sorted(foo.keys())
    ['a', 'b']
    >>> foo['a']
    1
    >>> class bar(foo):
    ...     c = 3
    >>> sorted(bar.keys())
    ['a', 'b', 'c']
    >>> foo['a'] = 5
    >>> bar['a']
    5

"""

from UserDict import DictMixin


class _DictishMeta(type, DictMixin):

    def __getitem__(self, item):
        try:
            return getattr(self, item)
        except AttributeError:
            raise KeyError(item)

    def __setitem__(self, item, value):
        setattr(self, item, value)

    def __delitem__(self, item):
        try:
            delattr(self, item)
        except AttributeError:
            raise KeyError(item)

    def keys(self):
        keys = set()
        for cls in (self,) + self.__mro__:
            for name in cls.__dict__:
                if not name.startswith('_'):
                    keys.add(name)
        return list(keys)


class dictish(object):

    __metaclass__ = _DictishMeta


if __name__ == '__main__':
    import doctest
    doctest.testmod()
