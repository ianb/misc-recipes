from lxml.html import HTML
from contextlib import contextmanager

def to_text(doc):
    if isinstance(doc, basestring):
        doc = HTML(doc)
    context = TextContext()
    p = Parser()
    p.parse(doc, context)
    return unicode(context)

class TextContext(object):

    def __init__(self):
        self.indent = 0
        parts = []
        
    def write(self, text):
        if text is None:
            return
        self.parts.append(text)

    def newline(self):
        self.write(u'\n')
        self.write(u' '*self.indent)

    def __unicode__(self):
        return u''.join(self.parts)

class Parser(object):
    def __init__(self):
        pass

    def parse(self, doc, context):
        tag = doc.tag
        method = getattr(self, 'tag_'+tag, None)
        if method is not None:
            method(doc, context)
            return
        context.write(tag.text)
        for child in tag:
            self.parse(child, context)
        context.write(tag.tail)
        
            
