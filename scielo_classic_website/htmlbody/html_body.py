import logging
import os
import sys
from difflib import unified_diff
from functools import lru_cache
from datetime import datetime

from lxml import etree
from lxml.etree import ParseError, register_namespace
from lxml.html import fromstring, html_to_xhtml, iterlinks, rewrite_links, tostring

from scielo_classic_website.htmlbody.html_code_utils import html_safe_decode


class UnableToGetHTMLTreeError(Exception):
    ...


class Checker:

    def __init__(self, original):
        self.original = original

    def validate(self, converted):
        original_ = Checker.get_words(self.original)
        converted_ = Checker.get_words(converted)

        if len(list(original_)) == len(list(converted_)):
            return True

        original_ = Checker.get_words(self.original)
        converted_ = Checker.get_words(converted)
        name = datetime.now().isoformat()[:19]
        with open(f"{name}.a.txt", "w") as fp:
            fp.writelines("\n".join(original_))
        with open(f"{name}.b.txt", "w") as fp:
            fp.writelines("\n".join(converted_))
        return False

    @staticmethod
    def get_words(content):
        content = (content or "").strip()
        content = content.replace("&nbsp;", "").replace("&#160;", "")
        for word in Checker.remove_tags(content):
            yield from word.split()

    @staticmethod
    def remove_tags(content):
        x = content.replace("<", "MARK-TAG<")
        x = x.replace(">", ">MARK-TAG")

        for item in x.split("MARK-TAG"):
            if not item.strip():
                continue
            if item[0] == "<" and item[-1] == ">":
                continue
            yield item


class NS:
    def __init__(self, content):
        self.content = content

    def remove_namespaces(self):
        return "".join(self._remove_ns_tags())

    def _remove_ns_tags(self):
        x = self.content.replace("<", "MARK-TAG<")
        x = x.replace(">", ">MARK-TAG")
        for item in x.split("MARK-TAG"):
            if not NS._has_ns(item):
                yield item

    @staticmethod
    def _has_ns(item):
        if not item.strip():
            return False

        if item[0] != "<":
            return False

        if item[-1] != ">":
            return False

        if ":" not in item:
            return False

        for part in item.split():
            if ":" in part.split("=")[0]:
                return True
        return False


class Wrapper:
    HTML_WORD_NAMESPACES = {
        'o': 'urn:schemas-microsoft-com:office:office',
        'w': 'urn:schemas-microsoft-com:office:word',
        'v': 'urn:schemas-microsoft-com:vml',
        'm': 'http://schemas.microsoft.com/office/2004/12/omml',
        'st1': 'urn:schemas-microsoft-com:office:smarttags'
    }

    def __init__(self, content):
        self.content = content

    @property
    def wrapped(self):
        namespace_declarations = self.get_namespace_declarations()
        if self.content.strip().startswith(f"<html{namespace_declarations}"):
            return self.content
        return f"<html{namespace_declarations}><body>{self.content}</body></html>"

    def get_namespace_declarations(self):
        if 'xmlns:' not in self.content:
            return " " + ' '.join([
                f'xmlns:{prefix}="{uri}"' 
                for prefix, uri in Wrapper.HTML_WORD_NAMESPACES.items()
            ])
        return ""


def html2xml(tree):
    body = tree.find(".//body")
    try:
        content = tostring(body, method="xml", encoding="utf-8").decode("utf-8")
        content = content[content.find(">")+1:]
        content = content[:content.rfind("</body>")]
    except Exception as e:
        logging.exception(e)
        raise
    return content


class HTMLContent:
    """
    >>> from scielo_classic_website.htmlbody.html_body import HTMLContent
    >>> hc = HTMLContent("<root><p>&nbsp;&ntilde;&#985;<br><hr><img src='x.gif'></root>")
    >>> hc.content
    >>> '<root><p>\xa0ñϙ<br/></p><hr/><img src="x.gif"/></root>'
    """

    def __init__(self, content):
        # for prefix, uri in HTML_WORD_NAMESPACES.items():
        #     register_namespace(prefix, uri)
        self.tree = content

    @staticmethod
    def create(file_path):
        try:
            with open(file_path, encoding="utf-8") as f:
                text = f.read()
        except Exception as e:
            with open(file_path, encoding="iso-8859-1") as f:
                text = f.read()
        return HTMLContent(text)

    @property
    def content(self):
        if self.tree is None:
            return self._original
        try:
            self.fix_asset_paths()
            return html2xml(self.tree)
        except Exception as e:
            return self._original

    @property
    def tree(self):
        return self._tree

    @tree.setter
    def tree(self, content):
        self.load_content(content)

    def load_content(self, content):
        self._tree = None
        self._original = content
        try:
            tree = fromstring(Wrapper(self.normalized_content).wrapped)
            self.evaluate_content(html2xml(tree), 0.8)
        except Exception as e:
            logging.exception(e)
            try:
                tree = fromstring(Wrapper(self._original).wrapped)
            except Exception as e:
                d = {
                    "class": "HTMLContent",
                    "method": "load_content",
                    "error": str(e),
                    "type": str(type(e)),
                }
                raise UnableToGetHTMLTreeError(str(d))
        
        self._tree = tree

    @property
    def normalized_content(self):
        content = self._original
        # Fix para namespaces
        # Converte tags de estilo para spans padronizados
        # Evita tags de estilos mescladas
        # ex.: <b><i>conteúdo</b></i> =>
        # <span name="style_bold"><span name="style_italic">conteúdo</span></span>
        content = NS(content).remove_namespaces()
        content = avoid_mismatched_styles(content)
        return avoid_mismatched_p(content)

    def evaluate_content(self, text_converted, expected_ratio):
        try:
            valid = Checker(self.normalized_content).validate(text_converted)
        except Exception as e:
            logging.info("Error evaluate_content inesperado")
            logging.exception(e)
        else:
            if not valid:
                logging.info("Error evaluate_content")
                raise ValueError(f"Loss data converting: {self.normalized_content[:50]}")

    @property
    def asset_path_fixes(self):
        return {item["old_link"]: item["new_link"] for item in self.old_and_new_links}

    @property
    def old_and_new_links(self):
        if self.tree is None:
            return []

        for elem, attr in (("img", "src"), ("a", "href")):
            for node in self.tree.xpath(f"//{elem}[@{attr}]"):
                old_link = node.get(attr)
                if not old_link:
                    continue
                if ":" in old_link:
                    continue
                new_link = os.path.realpath(old_link)
                if not os.path.isfile(new_link):
                    continue

                for folder in ("htdocs", "bases"):
                    if folder not in new_link:
                        continue
                    new_link = new_link[
                        new_link.find(folder) + len(folder) :
                    ]
                    logging.info({"old_link": old_link, "new_link": new_link})
                    yield {"old_link": old_link, "new_link": new_link}
                    break

    def fix_asset_paths(self):
        if self.tree is None:
            return
        for change in self.old_and_new_links:
            old_link = change.get("old_link")
            new_link = change.get("new_link")
            for node in self.tree.xpath(f".//a[@href={old_link}]|.//img[@src={old_link}]"):
                if node.get("href"):
                    attr = "href"
                elif node.get("src"):
                    attr = "src"
                logging.info(f"old {old_link} => new {new_link}")
                node.set("data-old-link", old_link)
                node.set(attr, new_link)


class BodyFromISIS:
    """
    Interface amigável para obter os dados da base isis
    que estão no formato JSON
    """

    def __init__(self, p_records):
        self.first_reference = None
        self.last_reference = None
        self.p_records = p_records or []
        self._identify_references_range()

    @property
    @lru_cache(maxsize=1)
    def before_references_paragraphs(self):
        if self.p_records and self.first_reference:
            return self.p_records[: self.first_reference]
        return self.p_records

    @property
    @lru_cache(maxsize=1)
    def references_paragraphs(self):
        if self.p_records and self.first_reference and self.last_reference:
            return self.p_records[self.first_reference : self.last_reference + 1]
        return []

    @property
    @lru_cache(maxsize=1)
    def after_references_paragraphs(self):
        if self.p_records and self.last_reference:
            return self.p_records[self.last_reference + 1 :]
        return []

    def _identify_references_range(self):
        for i, item in enumerate(self.p_records):
            if not self.first_reference and item.reference_index:
                self.first_reference = i
            if item.reference_index:
                self.last_reference = i
        logging.info(f"first_reference: {self.first_reference}")
        logging.info(f"last_reference: {self.last_reference}")

    @property
    def parts(self):
        parts = {}
        try:
            parts["before references"] = build_text(self.before_references_paragraphs)
        except Exception as e:
            # logging.exception(e)
            parts["before references"] = get_text(
                get_paragraphs_data(self.before_references_paragraphs)
            )
        try:
            parts["references"] = list(fix_references(self.references_paragraphs))
        except Exception as e:
            # logging.exception(e)
            parts["references"] = list(get_paragraphs_data(self.references_paragraphs))

        try:
            parts["after references"] = build_text(self.after_references_paragraphs)
        except Exception as e:
            # logging.exception(e)
            parts["after references"] = get_text(
                get_paragraphs_data(self.after_references_paragraphs)
            )
        return parts


def get_paragraphs_data(p_records, part_name=None):
    for item in p_records:
        # item.data (dict which keys: text, index, reference_index)
        if item.data["text"]:
            # logging.info("Antes:")
            # logging.info(item.data)

            hc = HTMLContent(item.data["text"])
            root = hc.tree.find(".//body/*")
            if part_name:
                root.set("data-part", part_name)

            ref_idx = item.data.get("reference_index")
            if ref_idx:
                root.set("data-ref-index", ref_idx)

            item.data["text"] = hc.content

            # logging.info("Depois:")
            # logging.info(item.data["text"])
            yield item.data


def get_text(items):
    return "".join([item["text"] for item in items or []])


def build_text(p_records):
    document = "".join(fix_paragraphs(p_records))
    if not document:
        return
    hc = HTMLContent(document)    
    hc.fix_asset_paths()
    return hc.content


def fix_paragraphs(p_records):
    for item in p_records:
        # item.data (dict which keys: text, index, reference_index)
        if item.data["text"]:
            yield avoid_mismatched_p(item.data["text"])


def fix_references(p_records):
    for item in p_records:
        # item.data (dict which keys: text, index, reference_index)
        if item.data["text"]:
            item.data["text"] = avoid_mismatched_p(item.data["text"])               
            yield item.data


def avoid_mismatched_p(row):
    row = row.replace("<P>", "<p>")
    row = row.replace("</P>", "</p>")
    tag_names = ("p", )
    for tag_name in tag_names:
        tag_open = f"<{tag_name}>"
        tag_close = f"</{tag_name}>"

        if tag_open not in row and tag_close not in row:
            continue
        if tag_open in row and tag_close in row:
            continue
        if tag_open in row:
            row = row.replace(tag_open, f'<p type="open"/>')
            continue
        if tag_close in row:
            row = row.replace(tag_open, f'<p type="close"/>')
    return row


def avoid_mismatched_styles(content):
    style_mappings = {
        "b": "bold",
        "i": "italic", 
        "u": "underline",
        "sup": "sup",
        "sub": "sub"
    }        
    for tag, style in style_mappings.items():
        # Tags minúsculas
        content = content.replace(f"<{tag}>", f'<span name="style_{style}">')
        content = content.replace(f"</{tag}>", '</span>')
        
        # Tags maiúsculas
        tag_upper = tag.upper()
        content = content.replace(f"<{tag_upper}>", f'<span name="style_{style}">')
        content = content.replace(f"</{tag_upper}>", '</span>')
    return content
