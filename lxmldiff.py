from lxml.html.diff import htmldiff
from lxml.html import parse, tostring, open_in_browser, fromstring

def get_page(url):
    doc = parse(url).getroot()
    doc.make_links_absolute()
    return tostring(doc)

def compare_pages(url1, url2, selector='body div'):
    basis = parse(url1).getroot()
    basis.make_links_absolute()
    other = parse(url2).getroot()
    other.make_links_absolute()
    el1 = basis.cssselect(selector)[0]
    el2 = other.cssselect(selector)[0]
    diff_content = htmldiff(tostring(el1), tostring(el2))
    diff_el = fromstring(diff_content)
    el1.getparent().insert(el1.getparent().index(el1), diff_el)
    el1.getparent().remove(el1)
    return basis

if __name__ == '__main__':
    import sys
    doc = compare_pages(sys.argv[1], sys.argv[2], sys.argv[3])
    open_in_browser(doc)
