import itertools

class stricttype(object):

    counter = itertools.count()

    def __init__(self, required_type, doc=None, real_attr=None):
        self.required_type = required_type
        if not real_attr:
            n = self.counter.next()
            real_attr = '_stricttype_attr_%i' % n
        self.real_attr = real_attr
        self.doc = doc

    def __set__(self, obj, value):
        if not isinstance(value, self.required_type):
            raise TypeError, 'must be of type %r' % self.required_type
        setattr(obj, self.real_attr, value)

    def __get__(self, obj, cls):
        return getattr(obj, self.real_attr)

    def __del__(self, obj):
        delattr(obj, self.real_attr)

    def __doc__(self, obj):
        return self.doc


if __name__ == '__main__':
    class IntPoint(object):

        def __init__(self, x, y):
            self.x = x
            self.y = y

        def __str__(self):
            return 'Point: (%i, %i)' % (self.x, self.y)

        x = stricttype(int)
        y = stricttype(int)

    p = IntPoint(1, 1)
    print p
    p.x = 2
    print p
    p.x = 2.2
