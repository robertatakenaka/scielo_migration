from lxml import etree as ET
from io import StringIO


def get_html_tree(html_str):
    parser = ET.HTMLParser()
    return ET.parse(StringIO(html_str), parser)


def get_mixed_citation_node(reference_html_paragraph):
    html_tree = get_html_tree(reference_html_paragraph)
    p = html_tree.find(".//body/p")
    if p is not None:
        p.tag = 'mixed-citation'
    return p
