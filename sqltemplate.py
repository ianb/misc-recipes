import re
import sys
import tempita

_var_re = re.compile(r'\{\{(.*?)\}\}')


def sqlsub(tmpl, stacklevel=1, marker='%s', f_globals=None, **args):
    """Return (sql, params), with %s as the param marker

        >>> sqlsub('users.username = {{username.lower()}}', username='bob')
        ('users.username = %s', ['bob'])

    """
    if not args:
        args = {}
        frame = sys._getframe(stacklevel)
        args = frame.f_locals
        f_globals = frame.f_globals
    if f_globals is None:
        f_globals = {}
    params = []
    sql = []
    last_end = 0
    for match in _var_re.finditer(tmpl):
        sql.append(tmpl[last_end:match.start()])
        sql.append(marker)
        params.append(eval(match.group(1), args, f_globals))
        last_end = match.end()
    sql.append(tmpl[last_end:])
    return ''.join(sql), params


class sql(unicode):
    def __sql__(self):
        return self


class sqllist(list):
    def __sqllist__(self):
        return self


def inserts(values):
    values = values.items()
    l = sqllist()
    l.append(sql('(%s) VALUES (' % (', '.join(key for key, value in values))))
    first = True
    for key, value in values:
        if first:
            first = False
        else:
            l.append(sql(', '))
        l.append(value)
    l.append(sql(')'))
    return l


def updates(values):
    values = values.items()
    l = sqllist()
    first = True
    for key, value in values:
        if first:
            first = False
        else:
            l.append(sql(', '))
        l.append(sql('%s=' % key))
        l.append(value)
    return l


class SQLTemplate(tempita.Template):

    default_namespace = tempita.Template.default_namespace.copy()
    default_namespace.update(dict(
        sql=sql,
        inserts=inserts,
        updates=updates,
        ))

    def _repr(self, value, pos):
        if hasattr(value, '__sql__'):
            return tempita.Template._repr(self, value.__sql__(), pos)
        elif hasattr(value, '__sqllist__'):
            return sqllist(self._repr(item, pos) for item in value.__sqllist__())
        else:
            return _SQLValue(value)

    def substitute(self, *args, **kw):
        result = super(SQLTemplate, self).substitute(*args, **kw)
        return SQLExpression.from_sequence(result)

    def _interpret(self, ns):
        __traceback_hide__ = True
        parts = []
        defs = {}
        self._interpret_codes(self._parsed, ns, out=parts, defs=defs)
        if '__inherit__' in defs:
            inherit = defs.pop('__inherit__')
        else:
            inherit = None
        return parts, defs, inherit


class SQLExpression(object):

    def __init__(self, sql_chunks, params):
        self.sql_chunks = sql_chunks
        self.params = params

    def args(self, paramstyle='format'):
        sql = [self.sql_chunks[0]]
        if paramstyle in ['qmark', 'format', 'numeric']:
            params = []
        else:
            params = {}
        for index, (chunk, param) in enumerate(zip(self.sql_chunks[1:], self.params)):
            if paramstyle in ('qmark', 'format'):
                if paramstyle == 'qmark':
                    sql.append('?')
                elif paramstyle == 'format':
                    sql.append('%s')
                else:
                    sql.append(':%s' % index)
                params.append(param)
            else:
                if paramstyle == 'named':
                    sql.append(':n%s' % index)
                elif paramstyle == 'pyformat':
                    sql.append('%%(n%s)' % index)
                params['n%s' % index] = param
            sql.append(chunk)
        return (''.join(sql), params)

    @classmethod
    def from_sequence(cls, seq):
        chunks = ['']
        params = []
        for item in cls._flatten(seq):
            if isinstance(item, _SQLValue):
                params.append(item.value)
                chunks.append('')
            else:
                chunks[-1] += unicode(item)
        return cls(chunks, params)

    @staticmethod
    def _flatten(seq):
        result = []
        for item in seq:
            if hasattr(item, '__sqllist__'):
                result.extend(SQLExpression._flatten(item))
            else:
                result.append(item)
        return result

    def __repr__(self):
        sql = [self.sql_chunks[0]]
        for chunk, item in zip(self.sql_chunks[1:], self.params):
            sql.append('{%r}' % item)
            sql.append(chunk)
        return '<sql %s>' % ''.join(sql)


class _SQLValue(object):

    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return '<SQLValue %r>' % self.value

__test__ = {
    'sqltemplate':
    r"""
    >>> SQLTemplate('SELECT * FROM {{"user" | sql}} WHERE id = {{10}}').substitute()
    <sql SELECT * FROM user WHERE id = {10}>
    >>> SQLTemplate('INSERT INTO test {{inserts(dict(a=1, b=2))}}').substitute()
    <sql INSERT INTO test (a, b) VALUES ({1}, {2})>
    >>> SQLTemplate('UPDATE test SET {{updates(dict(a=1, b=2))}}').substitute()
    <sql UPDATE test SET a={1}, b={2}>

    """}

if __name__ == '__main__':
    import doctest
    doctest.testmod()
