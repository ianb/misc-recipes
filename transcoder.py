"""
Example:

    >>> data = u'Hi\u1000there'
    >>> data.encode('ascii', 'unicode_name')
    'HiMYANMAR_LETTER_KA_there'
"""
import unicodedata
import codecs

def unicode_name_transcoder(exc):
    data = exc.object[exc.start:exc.end]
    name = unicodedata.name(data).replace(' ', '_')+'_'
    return (unicode(name), exc.end)

codecs.register_error('unicode_name', unicode_name_transcoder)

if __name__ == '__main__':
    import doctest
    doctest.testmod()
    
