"""\
html.py
29 Dec 2002
Ian Bicking <ianb@colorstudy.com>

Kind of like htmlgen, only much simpler.  The only important symbol that
is exported is ``html``.

You create tags with attribute access.  I.e., the "A" anchor tag is
html.a.  The attributes of the HTML tag are done with keyword
arguments.  The contents of the tag are the non-keyword arguments
(concatenated).  You can also use the special "c" keyword, passing a
list, tuple, or single tag, and it will make up the contents (this is
useful because keywords have to come after all non-keyword arguments,
and it's unintuitive to give your content before your attributes).

If the value of an attribute is Exclude, then no attribute will be
inserted.  Think of it as "does not apply".  So::

    >>> html.a(href="http://www.yahoo.com">, name=html.Exclude, c="Click Here")
    '<a href="http://www.yahoo.com">Click Here</a>'

If the value is None, then the empty string is used.  Otherwise str()
is called on the value.

``html`` can also be called, and it will concatenate the quoted string
representations of its arguments.

``html.input`` is special, in that you can use ``html.input.radio()``
to get an ``<input type="radio">`` tag.  You can still use
``html.input(type="radio")`` though, just like normal.

``html.comment`` will generate an HTML comment, like
``html.comment('comment text', 'and some more text')`` -- note that
it cannot take keyword arguments (because they wouldn't mean anything).

``html.javascript`` will wrap its arguments in <script>... tags.

``html.literal`` will allow you to give HTML source without any quoting.

If you cannot define an attribute because it conflicts with a Python
keyword (particularly ``class``), you can append an underscore and
it will be removed (like ``class_='whatever'``).
"""

from cgi import escape
from types import *

class Exclude:
    pass

class UnfinishedTag:

    def __init__(self, tag):
        self._tag = tag

    def __call__(self, *args, **kw):
        return Tag(self._tag, *args, **kw)

    def __str__(self):
        return '<%s />' % self._tag

    def __htmlrepr__(self):
        return str(self)

class UnfinishedInput:

    def __init__(self, tag, type=None):
        self._tag = tag
        self._type = type

    def __call__(self, *args, **kw):
        if self._type:
            kw['type'] = self._type
        return Tag(self._tag, *args, **kw)

    def __getattr__(self, attr):
        return UnfinishedInput(self._tag, type=attr.lower())

    def __htmlrepr__(self):
        if self._type:
            raise UnfinishedTag, '<input type="%s"> unfinished' % self._type
        else:
            raise UnfinishedTag, '<input> unfinished' % self._type

class UnfinishedComment:

    def __call__(self, *args):
        return literal('<!--%s-->' % ''.join(map(str, args)))
        
    def __htmlrepr__(self):
        raise UnfinishedTag

class UnfinishedJavascript:

    def __call__(self, *args):
        return literal('<script type="text/javascript"><!--\n%s\n// --></script>\n' \
               % '\n'.join(args))

class UnfinishedLiteral:

    def __call__(self, *args):
        return literal(*args)

    def __htmlrepr__(self):
        raise UnfinishedTag

class Base:

    Exclude = Exclude

    input = UnfinishedInput('input')
    comment = UnfinishedComment()
    literal = UnfinishedLiteral()
    javascript = UnfinishedJavascript()

    def __getattr__(self, attr):
        if attr.startswith('_'):
            raise AttributeError
        result = self.__dict__[attr] = UnfinishedTag(attr.lower())
        return result

    def __call__(self, *args):
        return ''.join(map(htmlrepr, args))

def attrEncode(v):
    if v.endswith('_'):
        return v[:-1]
    else:
        return v

def Tag(tag, *args, **kw):
    if kw.has_key("c"):
        assert not args, "The special 'c' keyword argument cannot be used in conjunction with non-keyword arguments"
        args = kw.pop("c")
    if type(args) not in (type(()), type([])):
        args = (args,)
    htmlArgs = [' %s="%s"' % (attrEncode(attr), htmlrepr(value))
                for attr, value in kw.items()
                if value is not Exclude]
    if not args and emptyTags.has_key(tag):
        if blockTags.has_key(tag):
            return literal("<%s%s />\n" % (tag, "".join(htmlArgs)))
        else:
            return literal("<%s%s />" % (tag, "".join(htmlArgs)))
    else:
        if blockTags.has_key(tag):
            return literal("<%s%s>\n%s\n</%s>\n" % (
                tag,
                "".join(htmlArgs),
                "".join(map(htmlrepr, args)),
                tag))
        else:
            return literal("<%s%s>%s</%s>" % (
                tag,
                "".join(htmlArgs),
                "".join(map(htmlrepr, args)),
                tag))

class literal:

    def __init__(self, s):
        self._string = s
        
    def __str__(self):
        return self._string
        
    def __repr__(self):
        return repr(self._string)
        
    def __htmlrepr__(self):
        return self._string

def htmlrepr(val):
    if val is None:
        return ''
    elif type(val) is StringType:
        return escape(val, 1)
    elif hasattr(val, '__htmlrepr__'):
        return val.__htmlrepr__()
    else:
        return escape(str(val), 1)

def d(*kw): return kw

emptyTagString = """
area base basefont br col frame hr img input isindex link meta param
"""
emptyTags = {}
for tag in emptyTagString.split():
    emptyTags[tag] = 1

blockTagString = """
applet blockquote body br dd div dl dt fieldset form frameset
head hr html iframe map menu noframes noscript object ol optgroup
p param script select table tbody tfoot thead tr ul var
"""
blockTags = {}
for tag in blockTagString.split():
    blockTags[tag] = 1

html = Base()

__all__ = ["html", "Exclude", "htmlrepr", "literal"]

if __name__ == "__main__":
    print html.html(
        html.head(html.title("Page Title")),
        html.body(
        bgcolor="#000066",
        text="#ffffff",
        c=[html.h1("Page Title"),
           html.p("Hello <world>!")],
        ))
