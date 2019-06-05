"""
Packs integers into more compact forms.

Kind of a reaction to:
  http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/410672
"""

import struct

def pack_int(i):
    """
    Usage:

        >>> pack_int(100)
        'ZAAAAA'
        >>> unpack_int(_)
        100
        >>> pack_int(1000000000)
        'AMqaOw'
        >>> unpack_int(_)
        1000000000
    """
    return struct.pack('i', i).encode('base64').replace('\n', '').strip('=')

def unpack_int(s):
    s += '=' * (8 % len(s))
    return struct.unpack('i', s.decode('base64'))[0]

if __name__ == '__main__':
    import doctest
    doctest.testmod()
    
