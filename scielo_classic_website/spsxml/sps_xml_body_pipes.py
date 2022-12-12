
import plumber
from lxml import etree as ET


def get_xml_body(xml_body):
    """
    Obtém XML

    Parameters
    ----------
    xml_body: etree

    ((address | alternatives | answer | answer-set | array |
    block-alternatives | boxed-text | chem-struct-wrap | code | explanation |
    fig | fig-group | graphic | media | preformat | question | question-wrap |
    question-wrap-group | supplementary-material | table-wrap |
    table-wrap-group | disp-formula | disp-formula-group | def-list | list |
    tex-math | mml:math | p | related-article | related-object | disp-quote |
    speech | statement | verse-group)*, (sec)*, sig-block?)
    """
    ppl = plumber.Pipeline(
            RemoveCommentPipe(),
            FontSymbolPipe(),
            RemoveTagsPipe(),
            RenameElementsPipe(),
            StylePipe(),
            OlPipe(),
            UlPipe(),
            TagsHPipe(),
            ASourcePipe(),
            AHrefPipe(),
            ANamePipe(),
            ImgSrcPipe(),
    )
    transformed_data = ppl.run(xml_body, rewrap=True)
    return next(transformed_data)


def _process(xml, tag, func):
    nodes = xml.findall(".//%s" % tag)
    for node in nodes:
        func(node)

##############################################################################
# Remove items

class RemoveCommentPipe(plumber.Pipe):
    def transform(self, data):
        raw, xml = data
        comments = xml.xpath("//comment()")
        for comment in comments:
            parent = comment.getparent()
            if parent is not None:
                # isso evita remover comment.tail
                comment.addnext(etree.Element("REMOVE_COMMENT"))
                parent.remove(comment)
        etree.strip_tags(xml, "REMOVE_COMMENT")
        return data


class RemoveTagsPipe(plumber.Pipe):
    TAGS = ["font", "small", "big", "span", "s", "lixo", "center"]

    def transform(self, data):
        raw, xml = data
        etree.strip_tags(xml, self.TAGS)
        return data


##############################################################################
# Rename

class RenameElementsPipe(plumber.Pipe):
    from_to = (
        ('div', 'sec'),
        ('dir', 'ul'),
        ('dl', 'def-list'),
        ('dd', 'def-item'),
        ('li', 'list-item'),
        ('br', 'break'),
        ("blockquote", "disp-quote"),
    )

    def transform(self, data):
        raw, xml = data

        for old, new in from_to:
            xpath = f".//{old}"
            for node in xml.findall(xpath):
                node.tag = new
        return data


class FontSymbolPipe(plumber.Pipe):

    def transform(self, data):
        raw, xml = data
        xpath = f".//font[@face='symbol']"
        for node in xml.xpath(xpath):
            node.tag = 'font-face-symbol'
        return data


class StylePipe(plumber.Pipe):

    def transform(self, data):
        raw, xml = data
        for style in ("bold", "italic", "sup", "sub", "underline"):
            xpath = f".//span[@name='style_{style}']"
            for node in xml.xpath(xpath):
                node.tag = style
        return data


class OlPipe(plumber.Pipe):
    def parser_node(self, node):
        node.tag = "list"
        node.set("list-type", "order")

    def transform(self, data):
        raw, xml = data
        _process(xml, "ol", self.parser_node)
        return data


class UlPipe(plumber.Pipe):
    def parser_node(self, node):
        node.tag = "list"
        node.set("list-type", "bullet")
        node.attrib.pop("list", None)

    def transform(self, data):
        raw, xml = data
        _process(xml, "ul", self.parser_node)
        return data


class TagsHPipe(plumber.Pipe):
    def parser_node(self, node):
        node.attrib.clear()
        org_tag = node.tag
        node.tag = "title"
        node.set("content-type", org_tag)

    def transform(self, data):
        raw, xml = data
        tags = ["h1", "h2", "h3", "h4", "h5", "h6"]
        for tag in tags:
            _process(xml, tag, self.parser_node)
        return data


class ASourcePipe(plumber.Pipe):
    def _change_src_to_href(self, node):
        href = node.attrib.get("href")
        src = node.attrib.get("src")
        if not href and src:
            node.attrib["href"] = node.attrib.pop("src")

    def transform(self, data):
        raw, xml = data
        _process(xml, "a[@src]", self._change_src_to_href)
        return data


##############################################################################

class AHrefPipe(plumber.Pipe):

    def _create_ext_link(self, node, extlinktype="uri"):
        node.tag = "ext-link"
        href = node.get("href").strip()
        node.attrib.clear()
        node.set("ext-link-type", extlinktype)
        node.set("{http://www.w3.org/1999/xlink}href", href)

    def _create_email(self, node):

        email_from_href = None
        email_from_node_text = None

        node.tag = "email"
        node.attrib.clear()

        href = node.get("href").strip()
        texts = href.replace('mailto:', '')
        for text in texts.split():
            if "@" in text:
                email_from_href = text
                break

        texts = (node.text or "").strip()
        for text in texts.split():
            if "@" in text:
                email_from_node_text = text
                break
        node.text = email_from_href or email_from_node_text

    def _create_internal_link(self, node):
        node.tag = "xref"
        node.set("rid", node.attrib.pop("href")[1:])

    def parser_node(self, node):

        href = node.get("href") or ""
        if href.count('"') == 2:
            node.set("href", href.replace('"', ""))

        node.set('href', (node.get('href') or '').strip())
        href = node.get("href")

        if not href:
            return

        if "mailto" in href or "@" in node.text:
            return self._create_email(node)

        if href[0] == "#":
            return self._create_internal_link(node)

        if href[0] in ["#", "."] or "/img/revistas/" in href or '..' in href:
            return self._create_internal_link(node)

        if ":" in href:
            return self._create_ext_link(node)
        if "www" in href:
            return self._create_ext_link(node)
        if href.startswith("http"):
            return self._create_ext_link(node)
        href = href.split("/")[0]
        if href and href.count(".") and href.replace(".", ""):
            return self._create_ext_link(node)

    def transform(self, data):
        raw, xml = data
        _process(xml, "a[@href]", self.parser_node)
        return data


class ANamePipe(plumber.Pipe):

    def parser_node(self, node):
        node.tag = "div"
        node.set("id", node.attrib.pop('name'))

    def transform(self, data):
        raw, xml = data
        _process(xml, "a[@name]", self.parser_node)
        return data


class ImgSrcPipe(plumber.Pipe):

    def parser_node(self, node):
        node.tag = "graphic"
        href = node.attrib.pop('src')
        node.attrib.clear()
        node.set("{http://www.w3.org/1999/xlink}href", href)

    def transform(self, data):
        raw, xml = data
        _process(xml, "img[@src]", self.parser_node)
        return data
