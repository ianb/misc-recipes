"""
HTMLStream.py
29 Dec 2002
Ian Bicking <ianb@colorstudy.com>
"""

from html import htmlrepr, literal, html
from types import *

def d(**kw):
    for k, v in kw.items():
        if k.endswith('_'):
            kw[k[:-1]] = v
            del kw[k]
    return kw

tagRawInfo = d(
    # special.extra
    object="inline declare? classid/ codebase/ data/ type/t codetype/t archive standby height width usemap/ name tabindex imgalign border hspace vspace",
    param="inline empty only name* value valuetype(data|ref|object) type/t",
    applet="inline codebase archive code object alt name width* height* align hspace vspace",
    img="inline empty src/* alt name longdesc/ height width usemap/ ismap? imgalign border hspace vspace",
    map="inline only i18n events id class style title name",
    area="inline empty focus shape coords href/ nohref? alt target",
    iframe="inline longdesc name src frameborder marginwidth marginheight scrolling imgalign height width",
    # special.basic
    br="inline empty clear",
    span="inline",
    bdo="inline lang xml:lang dir(ltr|rtl)",
    # fontstyle.extra
    big="inline",
    small="inline",
    font="inline size color face",
    basefont="inline empty size* color face",
    # fontstyle.basic
    tt="inline",
    i="inline",
    b="inline",
    u="inline",
    s="inline",
    # phrase.extra
    sub="inline",
    sup="inline",
    # phrase.basic
    em="inline",
    strong="inline",
    dfn="inline",
    code="inline",
    q="inline cite/",
    samp="inline",
    kbd="inline",
    var="inline",
    cite="inline",
    abbr="inline",
    acronym="inline",
    address="inline",
    # inline.forms
    input="inline empty focus type(text|password|checkbox|radio|submit|reset|file|hidden|image|button) name value checked? disabled? readonly? size maxlength src alt usemap/ onselect/j onchange/j accept/t imgalign",
    select="inline name size multiple? disabled? tabindex onfocus/j onblur/j onchange/j",
    optgroup="inline disabled? label*",
    option="inline selected? disabled? label value",
    textarea="name rows cols disabled? readonly? onselect/j onchange/j",
    label="inline for accesskey onfocus/j onblur/j",
    fieldset="block",
    legend="inline accesskey align",
    button="inline fucus name value type(button|submit|reset) displayed?",
    # misc.inline
    ins="inline cite/ datetime",
    del_="inline cite/ datetime",
    # misc
    noscript="block",
    # inline
    a="inline focus charset/c type/t name href/ hreflang rel rev shape coords target",
    # block level
    h1="block align",
    h2="block align",
    h3="block align",
    h4="block align",
    h5="block align",
    h6="block align",
    ul="block type compact?",
    ol="block type compact? start",
    li="block compact?",
    menu="block compact?",
    dir="block compact?",
    dl="block compact?",
    dt="block",
    dd="block",
    pre="block width",
    hr="block align(left|center|right) noshade? size width",
    blockquote="block cite/",
    center="block",
    noframes="block",
    # block
    p="block align",
    div="block align",
    # flow
    form="block action/* method(get|post) name enctype/t onsubmit/j onreset/j accept/t accept-charset/c target",
    # document structure
    html="head only i18n id xmlns/",
    head="head only i18n id profile/",
    title="head only i18n id",
    base="head empty only href/ target",
    meta="head empty only i18n id http-equiv name content* scheme",
    link="head empty charset/c href/ hreflang type/t rel rev media target",
    style="head type/t media title xml:space(preserve)",
    script="inline id charset/c type/t* src/ defer? xml:space(preserve)",
    body="head onload onunload background bgcolor text link vlink alink",
    # tables
    table="block summary width border frame rules cellspacing cellpadding align bgcolor",
    caption="block align",
    colgroup="block span width cellhalign cellvalign",
    col="block empty span width cellhalign cellvalign",
    thead="block cellhalign cellvalign",
    tfoot="block cellvalign cellvalign",
    tbody="block cellhalign cellvalign",
    tr="block cellhalign cellvalign bgcolor",
    th="block abbr axis headers scope rowspan colspan cellhalign cellvalign nowrap? bgcolor width height",
    td="block abbr axis headers scope rowspan colspan align valign nowrap? bgcolor width height",
)

extraAttrs = d(
    all="id class title style",
    i18n="lang xml:lang dir",
    events="onclick ondblclick onmousedown onmouseup onmouseover onmousemove onmouseout onkeypress onkeydown onkeyup",
    focus="accesskey tabindex onfocus onblur",
    attrs="coreattrs i18n events",
    cellhalign="align(left|center|right|justify|char) char charoff",
    cellvalign="valign(top|middle|bottom|baseline)",
    imgalign="align(top|middle|bottom|left|right)",
    shape="shape(rect|circle|poly|default)",
    )

# * required
# ? boolean
# / URL
# /t content type
# /c character set
# /j script

def addAttr(attrDict, attr):
    info = {}
    info['required'] = False
    while 1:
        if attr.endswith('*'):
            info['required'] = True
            attr = attr[:-1]
            continue
        if attr.endswith('?'):
            info['type'] = 'boolean'
            attr = attr[:-1]
            continue
        if attr.endswith('/t'):
            info['type'] = 'content-type'
            attr = attr[:-2]
            continue
        if attr.endswith('/c'):
            info['type'] = 'character-set'
            attr = attr[:-2]
            continue
        if attr.endswith('/j'):
            info['type'] = 'script'
            attr = attr[:-2]
            continue
        if attr.endswith(')'):
            info['type'] = 'option'
            i = attr.rfind('(')
            info['options'] = attr[i+1:-1].split('|')
            attr = attr[:i]
            continue
        break
    info['name'] = attr
    attrDict[attr] = info

tagInfo = {}

for tag, data in tagRawInfo.items():
    info = {}
    info['attributes'] = {}
    tagInfo[tag] = info
    pieces = data.split()
    addAll = True
    for piece in pieces:
        if piece in ('block', 'head', 'inline'):
            info['position'] = piece
            continue
        if piece == 'empty':
            info['empty'] = 1
            continue
        if piece == 'only':
            addAll = False
            continue
        if extraAttrs.has_key(piece):
            subPieces = extraAttrs[piece].split()
            for subPiece in subPieces:
                addAttr(info['attributes'], subPiece)
            continue
        addAttr(info['attributes'], piece)
    if addAll:
        for extra in extraAttrs['all'].split():
            addAttr(info['attributes'], extra)
    
class HTMLStream:
    
    tags = None
    get = html
    
    def __init__(self):
        self._items = []
        self._stack = []
        for tag in tagInfo.keys():
            if tag == 'input':
                cls = TagToWriteInput
            else:
                cls = TagToWrite
            setattr(self, tag, cls(tag, self))
    
    def comment(self, *args):
        self._items.append(literal('<!-- %s -->' % '\n'.join(args)))
        
    def script(self, *args):
        self._items.append(literal('<script type="text/javascript"><!--\n%s\n//--></script' % '\n'.join(args)))
    
    def write(self, *args):
        self._items.extend(args)
        
    def finish(self):
        assert not self._stack, "Tags still need to be closed (%s)" \
               % self._stack
        return ''.join(map(htmlrepr, self._items))

class TagToWrite(object):

    def __init__(self, tag, stream):
        self._tag = tag
        self._stream = stream

    def __call__(self, *args, **kw):
        val = tag(self._tag, *args, **kw)
        self._stream.write(val)
        
    def start(self, **kw):
        kw['_onlyStart'] = True
        self._stream._stack.append(self._tag)
        self._stream.write(tag(self._tag, **kw))
        
    def end(self):
        if not self._stream._stack:
            raise TypeError, "There are no tags waiting to be closed."
        if not self._stream._stack[-1] == self._tag:
            raise TypeError, "There are other open tags that still need " \
                  "to be closed (<%s> is next)" % self._stream._stack[-1]
        self._stream.write(literal('</%s>' % self._tag))
        self._stream._stack.pop()
        
class TagToWriteInput(TagToWrite):

    types = ['text', 'password', 'checkbox', 'radio',
             'submit', 'reset', 'file', 'hidden',
             'image', 'button']

    def __init__(self, tag, stream, type=None):
        self.type = type
        if not type:
            for t in self.types:
                setattr(self, t, TagToWriteInput(tag, stream, t))
        TagToWrite.__init__(self, tag, stream)
        
    def __call__(self, *args, **kw):
        if self.type:
            kw['type'] = self.type
        return TagToWrite.__call__(self, *args, **kw)
        
def tag(tag, *args, **kw):
    if kw.has_key('_onlyStart'):
        onlyStart = True
        del kw['_onlyStart']
    else:
        onlyStart = False
    if kw.has_key('c'):
        if not args:
            raise TypeError, "You must *either* provide a 'c' keyword " \
                  "argument, or positional arguments"
        args = kw.pop('c')
    if not isinstance(args, (list, tuple)):
        args = (args,)
    content = ''.join(map(htmlrepr, args))
    info = tagInfo[tag]
    attrInfo = info['attributes']
    if info.get('empty'):
        if onlyStart:
            raise TypeError, "<%s /> is an empty tag -- you cannot just start it" % tag
        if content:
            raise TypeError, "<%s /> cannot contain any content" % tag
        ending = ' />'
    else:
        if onlyStart:
            if content:
                raise TypeError, "For <%s> -- if you just start a tag, you " \
                      "cannot include content" % tag
            ending = '>'
        else:
            ending = '>%s</%s>' % (content, tag)
    attrs = {}
    for name, value in kw.items():
        if value is Exclude:
            continue
        value = str(value)
        name = name.lower()
        if not attrInfo.has_key(name):
            raise TypeError, '<%s> has no attribute %s (only %s)' \
                  % (tag, name, ', '.join(attrInfo.keys()))
        if attrInfo['type'] == 'options':
            value = value.lower()
            if not value in attrInfo['options']:
                raise TypeError, 'In <%s %s="%s"> -- value of attribute ' \
                      '%s must be one of %s' % (tag, name,
                      htmlEncode(attr), name, ', '.join(attrInfo['options']))
        attrs[name] = value
    for name, singleAttrInfo in attrInfo.items():
        if (singleAttrInfo['required']
            and not attrs.has_key(name)):
            raise TypeError, '<%s> requires a value for the %s attribute ' \
                  '(only given attributes %s)' \
                  % (tag, name, ', '.join(attrs.keys()))
    attrText = ' '.join(['%s="%s"' % (name, htmlEncode(value)) 
                         for name, value in attrs.items()])
    if attrText:
        return literal('<%s %s%s' % (tag, attrText, ending))
    else:
        return literal('<%s%s' % (tag, ending))

if __name__ == '__main__':
    s = HTMLStream()
    s.html.start()
    s.head.start()
    s.title('Hello world!')
    s.head.end()
    s.body.start()
    s.h1('Hello world!')
    s.p('So how is it going?  <>!')
    s.body.end()
    s.html.end()
    print s.finish()
