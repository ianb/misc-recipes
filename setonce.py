import itertools

_setonce_count = itertools.count()

class setonce(object):

    """
    Allows an attribute to be set once (typically in __init__), but
    be read-only afterwards.

    Example::

        >>> class A(object):
        ...     x = setonce()
        >>> a = A()
        >>> a.x
        Traceback (most recent call last):
        ...
        AttributeError: 'A' object has no attribute '_setonce_attr_0'
        >>> a.x = 10
        >>> a.x
        10
        >>> a.x = 20
        Traceback (most recent call last):
        ...
        AttributeError: Attribute already set
        >>> del a.x
        >>> a.x = 20
        >>> a.x
        20

    You can also force a set to occur::

        >>> A.x.set(a, 30)
        >>> a.x
        30
    """

    def __init__(self, doc=None):
        self._count = _setonce_count.next()
        self._name = '_setonce_attr_%s' % self._count
        self.__doc__ = doc

    def __get__(self, obj, type=None):
        if obj is None:
            return self
        return getattr(obj, self._name)

    def __set__(self, obj, value):
        try:
            getattr(obj, self._name)
        except AttributeError:
            setattr(obj, self._name, value)
        else:
            raise AttributeError, "Attribute already set"

    def set(self, obj, value):
        setattr(obj, self._name, value)

    def __delete__(self, obj):
        delattr(obj, self._name)

if __name__ == '__main__':
    import doctest
    doctest.testmod()
    
