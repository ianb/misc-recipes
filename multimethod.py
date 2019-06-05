"""
A refiguring of the multimethod implementation from this post:
http://www.artima.com/weblogs/viewpost.jsp?thread=101605

::

    >>> half = rational(1, 2)
    >>> half
    1/2
    >>> third = rational(1, 3)
    >>> div(half, third)
    3/2
    >>> div(half, 2)
    1/4
    >>> div(half, 0.5)
    1.0
    >>> div(1, 2)
    0
    >>> div(1, half)
    2/1

"""

class multimethod(object):
    def __init__(self, default):
        self.default = default
        self.name = default.__name__
        self.__doc__ = default.__doc__
        self.typemap = {}
    def __call__(self, *args):
        types = tuple(arg.__class__ for arg in args) # a generator expression!
        function = self.typemap.get(types, self.default)
        return function(*args)
    def types(self, *types):
        def decorator(func):
            if types in self.typemap:
                raise TypeError("duplicate registration")
            self.typemap[types] = func
            if func.__name__ == self.name:
                # to avoid confusion by overwriting the multimethod function
                return self
            else:
                return func
        return decorator

@multimethod
def div(a, b):
    "div a by b"
    return a / b
class rational(object):
    def __init__(self, num, denom):
        self.num, self.denom = num, denom
    def __repr__(self):
        return '%s/%s' % (self.num, self.denom)
@div.types(rational, int)
def div_rat_int(r, i):
    return rational(r.num, r.denom*i)
@div.types(int, rational)
def div_int_rat(i, r):
    return rational(r.denom * i, r.num)
@div.types(rational, float)
def div_rat_float(r, f):
    return r.num / (r.denom*f)
@div.types(float, rational)
def div_float_rat(f, r):
    return f * r.denom / r.num
@div.types(rational, rational)
def div_rat_rat(r1, r2):
    return rational(r1.num * r2.denom, r1.denom * r2.num)

if __name__ == '__main__':
    import doctest
    doctest.testmod()
