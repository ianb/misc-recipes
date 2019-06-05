"""
Configuration that evaluates all its arguments
"""

import sys
if sys.version_info < (2, 5):
    raise ImportError('This module is only compatible with Python 2.5+')

from ConfigParser import ConfigParser
from UserDict import DictMixin
from initools.configparser import ConfigParser as INIConfigParser
from tempita import Template

class TempitaConfigParser(ConfigParser):

    def _interpolate(self, section, option, rawval, vars):
        ns = _Namespace(self, section, vars)
        tmpl = Template(rawval, name='%s.%s' % (section, option))
        value = tmpl.substitute(ns)
        return value

class TempitaINIToolsParser(INIConfigParser):
    def get(self, section, option, raw=False, vars=None, _recursion=0):
        value = super(TempitaINIToolsParser, self).get(
            section, option, raw=True, vars=vars, _recursion=_recursion)
        if raw:
            return value
        filename, line_number = self.setting_location(section, option)
        ns = _Namespace(self, section, vars)
        # The -1 is because the first line is line 1, but should have
        # a 0 offset:
        tmpl = Template(value, name=filename, line_offset=line_number-1)
        value = tmpl.substitute(ns)
        return value

class _Namespace(DictMixin):
    def __init__(self, config, section, vars):
        self.config = config
        self.section = section
        self.vars = vars

    def __getitem__(self, key):
        if key == 'section':
            return _Section(self)
        if key == 'namespace':
            return self
        if self.config.has_option(self.section, key):
            return self.config.get(self.section, key)
        if vars and key in self.vars:
            return self.vars[key]
        raise KeyError(key)

    def __getattr__(self, attr):
        if attr.startswith('_'):
            raise AttributeError(attr)
        try:
            return self[attr]
        except KeyError:
            raise AttributeError(attr)

    def __setitem__(self, key, value):
        if self.vars is None:
            self.vars = {key: value}
        else:
            self.vars[key] = value

    def iterkeys(self):
        yield 'section'
        yield 'namespace'
        for key in self.config.options(self.section):
            yield key
        if self.vars:
            for key in self.vars:
                yield key

    def keys(self):
        return list(self.iterkeys())

    def __repr__(self):
        return '<namespace for %s [%s]>' % (self.config, section)

class _Section(object):
    def __init__(self, namespace):
        self._namespace = namespace

    def __getitem__(self, key):
        if not self._namespace.config.has_section(key):
            raise KeyError(key)
        return _Namespace(self._namespace.config, key, self._namespace.vars)

    def __getattr__(self, attr):
        if attr.startswith('_'):
            raise AttributeError(attr)
        try:
            return self[attr]
        except KeyError:
            raise AttributeError(attr)

__test__ = {
    'test_parser': r'''
>>> from StringIO import StringIO
>>> def make_parser(data):
...     cp = TempitaConfigParser()
...     cp.readfp(StringIO(data))
...     return cp
>>> p = make_parser("""\
... [DEFAULT]
... foo = bar
... 
... [server]
... port = 8080
... 
... [app1]
... port_offset = 1
... port = {{int(section.server.port)+int(port_offset)}}
... name = FooBar
... app_id = {{name.lower()}}_{{port}}_{{namespace.get('global_id', 'general')}}
... foo = {{bar}}
... """)
>>> p.get('server', 'port')
'8080'
>>> p.get('app1', 'port')
'8081'
>>> p.get('app1', 'name')
'FooBar'
>>> p.get('app1', 'app_id')
'foobar_8081_general'
>>> p.get('app1', 'foo')
Traceback (most recent call last):
    ...
NameError: name 'bar' is not defined at line 1 column 3 in file app1.foo


''',
    'test_ini_parser': r'''
>>> from StringIO import StringIO
>>> def make_parser(data):
...     cp = TempitaINIToolsParser()
...     cp.readfp(StringIO(data), filename="console")
...     return cp
>>> p = make_parser("""\
... [DEFAULT]
... foo = bar
... 
... [server]
... port = 8080
... 
... [app1]
... port_offset = 1
... port = {{int(section.server.port)+int(port_offset)}}
... name = FooBar
... app_id = {{name.lower()}}_{{port}}_{{namespace.get('global_id', 'general')}}
... foo = {{bar}}
... """)
>>> p.get('server', 'port')
u'8080'
>>> p.get('app1', 'port')
u'8081'
>>> p.get('app1', 'name')
u'FooBar'
>>> p.get('app1', 'app_id')
u'foobar_8081_general'
>>> p.get('app1', 'foo')
Traceback (most recent call last):
    ...
NameError: name 'bar' is not defined at line 12 column 3 in file console

''',
    }

if __name__ == '__main__':
    import doctest
    doctest.testmod()
