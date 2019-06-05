"""
Implements a fancier property()
"""

__all__ = ['property']

class _property_metaclass(type):

    def __new__(meta, class_name, bases, attrs):
        if '__init__' in attrs:
            # The property class itself
            return type.__new__(meta, class_name, bases, attrs)
        if len(bases) != 1:
            raise TypeError(
                "You may not do multiple inheritance from property")
        base = bases[0]
        if isinstance(base, meta):
            # A subclass
            call_attrs = {}
            set_attrs = {}
            for name, value in attrs.items():
                if name.startswith('_'):
                    set_attrs[name] = value
                else:
                    call_attrs[name] = value
            new_cls = base(**call_attrs)
            for name, value in set_attrs.items():
                setattr(new_cls, name, value)
            return new_cls
        else:
            # subclassing an instance(?)
            assert 0, repr(base)


class property(object):
    """
    Acts like a property, but also can be subclassed and return
    another property instance (with fget/fset/fdel from methods).

    You can use this like a normal property::

        >>> def classname(obj): return obj.__class__.__name__
        >>> class X(object):
        ...     foo = property(classname)
        >>> x = X()
        >>> x.foo
        'X'
        >>> X.foo
        property(<function classname at ...>)

    You can also subclass it::

        >>> class Y(object):
        ...     class foo(property):
        ...         fget = classname
        ...         def fset(self, value):
        ...             self.foo_attr = value
        >>> Y.foo
        property(<function classname at ...>, <function fset at ...>)
        >>> y = Y()
        >>> y.foo
        'Y'
        >>> y.foo = 'bar'
        >>> y.foo
        'Y'
        >>> y.foo_attr
        'bar'

    You can even subclass instances::

        >>> class_prop = property(classname)
        >>> class Z(object):
        ...     class foo(class_prop):
        ...         def fset(self, value):
        ...             self.another_attr = value
        >>> Z.foo
        property(<function classname at ...>, <function fset at ...>)
        >>> z = Z()
        >>> z.foo
        'Z'
        >>> z.foo = 'blah'
        >>> z.foo
        'Z'
        >>> z.another_attr
        'blah'
    """

    __metaclass__ = _property_metaclass
    
    def __new__(cls, fget=None, fset=None, fdel=None, doc=None):
        if isinstance(fset, tuple) and isinstance(fset[0], cls):
            # An instance is being subclassed
            cls_name = fget
            parent_instance = fset[0]
            attrs = fdel
            all_attrs = parent_instance.__dict__.copy()
            all_attrs.update(attrs)
            new_inst = cls.__metaclass__(cls_name, (cls,), all_attrs)
            return new_inst
        else:
            return object.__new__(
                cls, fget=fget, fset=fset, fdel=fdel, doc=doc)

    def __init__(self, fget=None, fset=None, fdel=None, doc=None):
        if isinstance(fset, tuple) and isinstance(fset[0], self.__class__):
            # We have been subclassed (__init__ always is called, even if
            # __new__ tries to take over)
            return
        if doc is None and fget is not None:
            doc = fget.__doc__
        self.fget = fget
        self.fset = fset
        self.fdel = fdel
        self.__doc__ = self.doc = doc

    def __repr__(self):
        args = [self.fget, self.fset, self.fdel, self.doc]
        if self.doc is None or self.doc == self.fget.__doc__:
            args.pop()
            if self.fdel is None:
                args.pop()
                if self.fset is None:
                    args.pop()
        return '%s(%s)' % (self.__class__.__name__,
                           ', '.join([repr(x) for x in args]))

    def __get__(self, obj, type=None):
        if obj is None:
            return self
        if self.fget is None:
            raise AttributeError
        return self.fget(obj)

    def __set__(self, obj, value):
        if self.fset is None:
            raise AttributeError
        self.fset(obj, value)

    def __delete__(self, obj):
        if self.fdel is None:
            raise AttributeError
        self.fdel(obj)

if __name__ == '__main__':
    import doctest
    doctest.testmod(optionflags=doctest.ELLIPSIS)
