class Bag(object):

    """
    This represents a bag: a set-like object that also keeps track of
    the *count* of the items in the bag.

    Like a set (or a dictionary) all the keys must be hashable, and
    the identity of what you put in and take out might not be equal.
    No order is preserved.

    Examples::

        >>> b = Bag()
        >>> b.add('a')
        >>> b.add('b')
        >>> b.add('b')
        >>> sorted(list(b))
        ['a', 'b', 'b']
        >>> b
        Bag(['a', 'b', 'b'])
        >>> b.count('b')
        2
        >>> b.remove('b')
        >>> b.count('b')
        1
        >>> b | Bag('a')
        Bag(['a', 'a', 'b'])
        >>> (b | Bag('a')).count('a')
        2
        >>> b.remove('b')
        >>> b.remove('b')
        Traceback (most recent call last):
            ...
        KeyError: 'b'
    """

    def __init__(self, seq=None):
        self._data = {}
        if seq is not None:
            self.update(seq)

    def __repr__(self):
        return '%s(%r)' % (
            self.__class__.__name__,
            list(self))

    def add(self, item):
        if item in self._data:
            self._data[item] += 1
        else:
            self._data[item] = 1

    def remove(self, item):
        try:
            if self._data[item] == 1:
                del self._data[item]
            else:
                self._data[item] -= 1
        except KeyError:
            ## Oddly, this is what Set raises, but list.remove raises
            ## ValueError?
            raise KeyError(item)

    def count(self, item):
        return self._data.get(item, 0)

    def counts(self):
        """
        Returns a list of (count, item) for all items in the sequence.
        """
        return self._data.items()

    def __iter__(self):
        xr = xrange
        for item, count in self._data.iteritems():
            if count == 1:
                yield item
            else:
                for i in xr(count):
                    yield item

    def iterunique(self):
        """
        Iterate over the unique items (regardless of count)
        """
        return self._data.itervalues()

    def __len__(self):
        length = 0
        for item, count in self._data.iteritems():
            length += count
        return length

    def __contains__(self, item):
        return item in self._data

    ## FIXME: not sure this applies?
    def issubset(self, other):
        for item in other:
            if item not in self:
                return False
        return True

    __le__ = issubset

    def issuperset(self, other):
        for item in self:
            if item not in other:
                return False
        return True

    __ge__ = issuperset

    def intersection(self, other):
        return self & other

    def __and__(self, other):
        new = self.copy()
        new &= other
        return new

    def symmetric_difference(self, other):
        return self ^ other

    def __xor__(self, other):
        new = self.copy()
        new ^= other
        return new

    def symmetric_difference_update(self, other):
        for item in other:
            if item in self:
                self.remove(item)
            else:
                self.add(item)

    def __ixor__(self, other):
        self.symmetric_difference_update(other)
        return self

    def intersection_update(self, other):
        for item in self:
            if item not in other:
                self.remove(item)

    def __iand__(self, other):
        self.intersection_update(other)
        return self

    ## All okay:

    def union(self, other):
        return self | other

    def __or__(self, other):
        new = self.copy()
        new |= other
        return new

    def difference(self, other):
        return self - other

    def __sub__(self, other):
        new = self.copy()
        new -= other
        return new

    def copy(self):
        obj = self.__class__()
        obj._data = self._data.copy()
        return obj

    def update(self, other):
        for item in other:
            self.add(item)
        return self

    def __ior__(self, other):
        self.update(other)
        return self

    def difference_update(self, other):
        for item in other:
            if item in self:
                self.remove(item)

    def __isub__(self, other):
        self.difference_update(other)
        return self

    def discard(self, item):
        try:
            self.remove(item)
        except KeyError:
            pass

    def clear(self):
        for item in list(self):
            self.remove(item)

    def mostcommon(self):
        """
        Returns (count, item), sorted for most-counted items first
        """
        return sorted(self.counts(), key=lambda x: -x[0])

if __name__ == '__main__':
    import doctest
    doctest.testmod()
    
