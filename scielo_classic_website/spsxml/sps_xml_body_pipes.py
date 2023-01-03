from io import StringIO

import plumber
from lxml import etree as ET


def convert_html_to_xml(document):
    if document.converted_html_body:
        xml = ET.fromstring(document.converted_html_body)
        content_type = xml.find(".").get("content-type")
        if content_type == "step-1":
            return self.convert_html_to_xml_step_2(document)
        if content_type == "step-2":
            return self.convert_html_to_xml_step_3(document)
    else:
        return self.convert_html_to_xml_step_1(document)


def set_step_value(xml):
    step = xml.find(".").get("content-type")
    if step:
        step = int(step.split("-")[-1]) + 1
    else:
        step = "1"
    xml.find(".").set("content-type", f"step-{step}")


def convert_html_to_xml_step_1(document):
    """
    Coloca os textos HTML principal e traduções na estrutura do XML:
    article/body, article/back/ref-list, article/back/sec,
    sub-article/body, sub-article/back,
    e inserindo o conteúdo em CDATA

    Parameters
    ----------
    document: Document
    """
    ppl = plumber.Pipeline(
            SetupPipe(),
            MainHTMLPipe(),
            TranslatedHTMLPipe(),
            EndPipe(),
    )
    transformed_data = ppl.run(document, rewrap=True)
    return next(transformed_data)


def convert_html_to_xml_step_2(document):
    """
    Converte o XML obtido no passo 1,
    remove o conteúdo de CDATA e converte as tags HTML nas XML correspondentes
    sem preocupação em manter a hierarquia exigida no XML

    Parameters
    ----------
    document: Document

    ((address | alternatives | answer | answer-set | array |
    block-alternatives | boxed-text | chem-struct-wrap | code | explanation |
    fig | fig-group | graphic | media | preformat | question | question-wrap |
    question-wrap-group | supplementary-material | table-wrap |
    table-wrap-group | disp-formula | disp-formula-group | def-list | list |
    tex-math | mml:math | p | related-article | related-object | disp-quote |
    speech | statement | verse-group)*, (sec)*, sig-block?)
    """
    ppl = plumber.Pipeline(
            RemoveCDATAPipe(),
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
            EndPipe(),
    )
    transformed_data = ppl.run(document, rewrap=True)
    return next(transformed_data)


def convert_html_to_xml_step_3(document):
    """
    Converte o XML obtido no passo 2.
    Localiza os xref e os graphics e adiciona, respectivamente, ref-type e
    os elementos fig, table-wrap, disp-formula, de acordo como o nome / local.

    Parameters
    ----------
    document: Document

    ((address | alternatives | answer | answer-set | array |
    block-alternatives | boxed-text | chem-struct-wrap | code | explanation |
    fig | fig-group | graphic | media | preformat | question | question-wrap |
    question-wrap-group | supplementary-material | table-wrap |
    table-wrap-group | disp-formula | disp-formula-group | def-list | list |
    tex-math | mml:math | p | related-article | related-object | disp-quote |
    speech | statement | verse-group)*, (sec)*, sig-block?)
    """
    ppl = plumber.Pipeline(
            StartPipe(),
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
            EndPipe(),
    )
    transformed_data = ppl.run(document, rewrap=True)
    return next(transformed_data)


def convert_html_to_xml_step_3(document):
    """
    Converte o XML obtido no passo 2,
    remove o conteúdo de CDATA e converte as tags HTML nas XML correspondentes
    sem preocupação em manter a hierarquia exigida no XML

    Parameters
    ----------
    document: Document

    ((address | alternatives | answer | answer-set | array |
    block-alternatives | boxed-text | chem-struct-wrap | code | explanation |
    fig | fig-group | graphic | media | preformat | question | question-wrap |
    question-wrap-group | supplementary-material | table-wrap |
    table-wrap-group | disp-formula | disp-formula-group | def-list | list |
    tex-math | mml:math | p | related-article | related-object | disp-quote |
    speech | statement | verse-group)*, (sec)*, sig-block?)
    """
    ppl = plumber.Pipeline(
            StartPipe(),
            EndPipe(),
    )
    transformed_data = ppl.run(document, rewrap=True)
    return next(transformed_data)


def _process(xml, tag, func):
    nodes = xml.findall(".//%s" % tag)
    for node in nodes:
        func(node)


class StartPipe(plumber.Pipe):

    def transform(self, data):
        document = data
        xml = ET.fromstring(document.converted_html_body)
        set_step_value(xml)
        return data, xml


class SetupPipe(plumber.Pipe):

    def precond(data):

        raw = data
        if not raw.get_record("p"):
            raise plumber.UnmetPrecondition()

    @plumber.precondition(precond)
    def transform(self, data):

        nsmap = {
            'xml': 'http://www.w3.org/XML/1998/namespace',
            'xlink': 'http://www.w3.org/1999/xlink'
        }

        xml = ET.Element('article', nsmap=nsmap)
        body = ET.Element('body')
        back = ET.Element('back')
        xml.append(body)
        xml.append(back)
        return data, xml


class EndPipe(plumber.Pipe):
    def transform(self, data):
        raw, xml = data

        set_step_value(xml)
        data = ET.tostring(
            xml,
            encoding="utf-8",
            method="xml",
            )
        return data


class MainHTMLPipe(plumber.Pipe):

    def transform(self, data):
        raw, xml = data

        body = xml.find("body")
        for item in raw.main_html_body_paragraphs['before references'] or []:
            # TODO keys: text, index, reference_index, part
            p = ET.Element("p")
            p.text = ET.CDATA(item['text'])
            body.append(p)

        references = ET.Element("ref-list")
        for item in raw.main_html_body_paragraphs['references'] or []:
            # TODO keys: text, index, reference_index, part
            ref = ET.Element("ref")
            ref.set("id", f"B{item['reference_index']}")
            mixed_citation = ET.Element('mixed-citation')
            mixed_citation.text = ET.CDATA(item['text'])
            ref.append(mixed_citation)
            references.append(ref)

        back = xml.find(".//back")
        back.append(references)
        for item in raw.main_html_body_paragraphs['after references'] or []:
            # TODO keys: text, index, reference_index, part

            # (ack | app-group | bio | fn-group | glossary | notes | sec)
            # uso de sec por ser mais genérico
            sec = ET.Element("sec")
            sec.text = ET.CDATA(item['text'])
            back.append(sec)

        return data


class TranslatedHTMLPipe(plumber.Pipe):

    def transform(self, data):
        raw, xml = data

        back = xml.find(".//back")
        for lang, texts in raw.translated_html_body_by_lang.items():
            sub_article = ET.Element("sub-article")
            sub_article.set('article-type', "translation")
            sub_article.set('{http://www.w3.org/XML/1998/namespace}lang', lang)
            back.append(sub_article)

            body = ET.Element('body')
            body.text = ET.CDATA(texts['before references'])
            sub_article.append(body)

            if texts['after references']:
                back = ET.Element('back')
                back.text = ET.CDATA(texts['after references'])
                sub_article.append(back)

        return data

##############################################################################


def html_body_tree(html_text):
    # html_text = "<html><head><title>test<body><h1>page title</h3>"
    parser = ET.HTMLParser()
    h = ET.parse(StringIO(html_text), parser)
    return h.find(".//body")


def remove_CDATA(old):
    new = html_body_tree(old.text)
    new.tag = old.tag
    for name, value in old.attrb.items():
        new.set(name, value)
    parent = old.getparent()
    parent.replace(old, new)


class RemoveCDATAPipe(plumber.Pipe):

    def transform(self, data):
        raw = data
        xml = ET.fromstring(raw.converted_html_body)
        for item in xml.findall(".//*"):
            if not item.getchildren() and item.text:
                remove_CDATA(item)
        return raw, xml


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
