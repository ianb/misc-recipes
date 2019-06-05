r'''
resolve_js_require handles the js-require attribute, adding
<script> tags to the head of a document.

Annoyingly, serializing as HTML requires a little work with XSLT.
We don't care about that here, so we'll use the function available
in WSGIFilter::

    >>> from wsgifilter.htmlserialize import tostring

We will also use a simple find_library_url function, and a simple
test function::

    >>> def find_library_url(name, type):
    ...     return 'http://localhost/%s.js' % name
    >>> def test(doc):
    ...     doc = resolve_js_require(
    ...         doc, 'http://localhost/test/page.html', 
    ...         find_library_url)
    ...     print tostring(doc, pretty=True).strip()

Now a simple test::

    >>> test('<body><input type="date" js-require="DateTime"></body>')
    <html>
      <head>
        <meta any>
        <script src="http://localhost/DateTime.js" type="text/javascript"></script>
      </head>
      <body>
        <input type="date">
      </body>
    </html>

Note that the html/head/body tags can be added by the HTML parser, and the <meta> tag is added by the HTML serializer.

A more complicated test::

    >>> test("""<body>
    ...   <script src="/TestLibrary.js"></script>
    ...   <input type="date" name="a" js-require="DateTime">
    ...   <input type="text" name="b" js-require="TestLibrary">
    ...   <input type="date" name="c" js-require="DateTime">
    ... </body>""")
    <html>
      <head>
        <meta any>
        <script src="http://localhost/DateTime.js" type="text/javascript"></script>
      </head>
      <body>
        <script src="/TestLibrary.js"></script>
        <input type="date" name="a">
        <input type="text" name="b">
        <input type="date" name="c">
      </body>
    </html>
'''

from lxml import etree
from urlparse import urljoin

def resolve_js_require(doc, doc_url, find_library_url):
    if isinstance(doc, basestring):
        doc = etree.HTML(doc)
    script_hrefs = set()
    for el in doc.xpath('//*[@js-require]'):
        name = el.attrib['js-require']
        del el.attrib['js-require']
        url = find_library_url(name, 'js')
        script_hrefs.add(url)
    # Check that we aren't duplicating any explicit <script> tags:
    for el in doc.xpath('//script[@src]'):
        url = urljoin(doc_url, el.attrib['src'])
        if url in script_hrefs:
            script_hrefs.remove(url)
    try:
        head = doc.xpath('//head')[0]
    except IndexError:
        # No <head>
        head = etree.Element('head')
        doc.insert(0, head)
    # Add in the <script> tags:
    for url in script_hrefs:
        el = etree.Element('script')
        el.attrib['type'] = 'text/javascript'
        el.attrib['src'] = url
        head.append(el)
    return doc

if __name__ == '__main__':
    import doctest
    from wsgifilter import lxmldoctest
    lxmldoctest.install()
    doctest.testmod()
    
