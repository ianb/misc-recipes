import re
import os
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

def dictcompare(source, pattern):
    """
    Matches the source dict to the pattern dict.  Returns (matches,
    good_keys, bad_keys), the first is a boolean, the rest are each
    lists of tuples, (source_key, pattern_key), where source_key or
    pattern_key may be MissingKey, which indicates the key was
    missing.

    The pattern dict can contain special special keys for matching.  A
    key ``regex_name`` will match a key ``name`` as a regular
    expression.  (Only string keys are supported in this case) A ``*``
    will match any value in the source.  If the pattern includes a key
    ``_any``, then any extra keys in source will be ignored.  If a key
    exists named ``any_name``, then the source key ``name`` needn't
    exist (but can).
    """

    matching_keys = []
    different_keys = []
    # We do this destructively, hence:
    source = source.copy()
    pattern = pattern.copy()

    if pattern.has_key('_missing'):
        missing = True
        del pattern['_missing']
    else:
        missing = False
    if pattern.has_key('_any'):
        any = True
        del pattern['_any']
    else:
        any = False
        
    for key, value in pattern.items():
        isString = type(key) in (type(""), type(u""))
        if isString and key.startswith('regex_'):
            real = key[len('regex_'):]
            if not source.has_key(real):
                if missing:
                    matching_keys.append((MissingKey, real))
                else:
                    different_keys.append((MissingKey, real))
                continue
            if type(value) in (type(""), type(u"")):
                value = re.compile(value)
            match = value.search(source[real])
            if not match:
                different_keys.append((real, key))
            else:
                matching_keys.append((real, key))
            del source[real]
        if isString and key.startswith('any_'):
            real = key[len('any_'):]
            if source.has_key(real):
                matching_keys.append((real, key))
            else:
                matching_keys.append((MissingKey, key))
        else:
            if not source.has_key(key):
                if missing:
                    matching_keys.append((MissingKey, key))
                else:
                    different_keys.append((MissingKey, key))
            else:
                if value != "*" and source[key] != value:
                    different_keys.append((key, key))
                else:
                    matching_keys.append((key, key))
                del source[key]

    if any:
        for key in source.keys():
            different_keys.append((key, MissingKey))
    else:
        for key in source.keys():
            matching_keys.append((key, MissingKey))
    matching_keys.sort(lambda a, b: cmp(a[0] or a[1], b[0] or b[1]))
    different_keys.sort(lambda a, b: cmp(a[0] or a[1], b[0] or b[1]))
    matches = not different_keys
    return (matches, matching_keys, different_keys)

class _MissingKey:
    def __nonzero__(self):
        return 0
    def repr(self):
        return '(none)'
MissingKey = _MissingKey()

def dictcompareError(source, pattern, width=None):
    matches, matching_keys, different_keys = dictcompare(source, pattern)
    if matches:
        return None
    keylen = 0
    for key in (allKeys(matching_keys) + allKeys(different_keys)):
        if len(keyRepr(key)) > keylen:
            keylen = len(keyRepr(key))
    keylen += 1
    if keylen > 40:
        keylen = 40
    if keylen < 5:
        keylen = 5
    if width is None:
        width = int(os.environ.get('COLUMNS', 80))-1
    sourcelen = int(width/2)-1
    patternlen = int(width/2)-1
    out = StringIO()
    out.write('Key%sSource%sPattern\n'
              % (' '*(keylen-3),
                 ' '*(sourcelen-6)))
    out.write('='*width + '\n')
    #if matching_keys:
    #    writeCentered('matching', width, out)
    #else:
    #    writeCentered('no matching keys', width, out)
    for skey, pkey in matching_keys:
        writeValues(source, pattern, skey, pkey, keylen,
                    sourcelen, patternlen, out)
    if different_keys:
        writeCentered('unmatching keys', width, out)
    for skey, pkey in different_keys:
        writeValues(source, pattern, skey, pkey, keylen,
                    sourcelen, patternlen, out)
    return out.getvalue()
        
def writeValues(source, pattern, skey, pkey, keylen,
                sourcelen, patternlen, out):
    if skey is MissingKey:
        key = keyRepr(pkey)
    else:
        key = keyRepr(skey)
    if skey is MissingKey:
        svalue = '(none)'
    else:
        svalue = valueRepr(source[skey])
    if pkey is MissingKey:
        pvalue = '(none)'
    else:
        pvalue = valueRepr(pattern[pkey])
    if len(key) > keylen:
        out.write(key + '\n')
        if len(pvalue) <= patternlen or len(svalue) <= sourcelen:
            out.write(' '*keylen)
    else:
        out.write(key)
        out.write(' '*(keylen-len(key)))
    if len(pvalue) > patternlen or len(svalue) > sourcelen:
        out.write('\n')
        out.write('  Source : %s\n' % svalue)
        out.write('  Pattern: %s\n' % pvalue)
    else:
        out.write(svalue)
        out.write(' '*(sourcelen-len(svalue)))
        out.write(pvalue)
        out.write('\n')

def writeCentered(text, width, out, sep='-'):
    out.write(' '*int(width/4))
    out.write(sep*(int(width/4)-len(text)/2))
    out.write(text)
    out.write(sep*(int(width/4)-len(text)/2))
    if width%2:
        out.write(sep)
    out.write('\n')

_plainKeyRE = re.compile(r'^[ -~]*$')
def keyRepr(key):
    if type(key) not in (type(""), type(u"")):
        return repr(key)
    if _plainKeyRE.search(key):
        if key.strip() == key:
            return key
        else:
            return repr(key)
    else:
        return repr(key)

def valueRepr(value):
    if type(value) is type({}):
        items = value.items()
        items.sort()
        return '{%s}' % ', '.join(['%s: %s' % v for v in items])
    else:
        return repr(value)

def allKeys(listList):
    result = []
    for v in listList:
        result.extend(v)
    return result
        
if __name__ == '__main__':
    v = [
        ({'a': 1, 'b': 2},
         {'a': 2, 'b': 2}),
        ]
    for source, pattern in v:
        print dictcompareError(source, pattern)
