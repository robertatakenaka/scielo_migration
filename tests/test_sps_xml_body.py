from unittest import TestCase

from lxml import etree

from scielo_classic_website.spsxml.sps_xml_body_pipes import (
    AHrefPipe,
    AlternativesGraphicPipe,
    ANamePipe,
    ASourcePipe,
    DivIdToTableWrap,
    EndPipe,
    FigPipe,
    FontSymbolPipe,
    ImgSrcPipe,
    InlineGraphicPipe,
    InsertCaptionAndTitleInTableWrapPipe,
    InsertGraphicInTableWrapPipe,
    InsertTableWrapFootInTableWrapPipe,
    MainHTMLPipe,
    OlPipe,
    RemoveCDATAPipe,
    RemoveCommentPipe,
    RemoveEmptyPTagPipe,
    RemoveParentPTagOfGraphicPipe,
    RemoveTagsPipe,
    RenameElementsPipe,
    StylePipe,
    TagsHPipe,
    TranslatedHTMLPipe,
    UlPipe,
    XRefTypePipe,
)


def get_tree(xml_str):
    return etree.fromstring(xml_str)


def tree_tostring_decode(_str):
    return etree.tostring(_str, encoding="utf-8").decode("utf-8")


class TestAHrefPipe(TestCase):
    def test_transform(self):
        xml = get_tree(
            (
                "<root>"
                '<a href="http://scielo.org">Example</a>'
                '<a href="mailto:james@scielo.org">James</a>'
                '<a href="#section1">Seção 1</a>'
                '<a href="/img/revistas/logo.jpg">Logo</a>'
                "</root>"
            )
        )
        expected = (
            "<root>"
            '<ext-link xmlns:ns0="http://www.w3.org/1999/xlink" ext-link-type="uri" ns0:href="http://scielo.org">'
            "Example"
            "</ext-link>"
            "<email/>"
            '<xref rid="section1">Seção 1</xref>'
            '<xref rid="img/revistas/logo.jpg">Logo</xref>'
            "</root>"
        )

        data = (None, xml)

        _, transformed_xml = AHrefPipe().transform(data)
        result = tree_tostring_decode(transformed_xml)
        self.assertEqual(expected, result)


class MockMainDocument:
    def __init__(self):
        self.main_html_paragraphs = {
            "before references": [
                {
                    "text": "<DIV ALIGN=right><B>Saskia Sassen*</B></DIV>",
                    "index": "1",
                    "reference_index": "",
                    "part": "before references",
                },
                {
                    "text": "<DIV ALIGN=right><B>Saskia Sassen*</B></DIV>",
                    "index": "2",
                    "reference_index": "",
                    "part": "before references",
                },
            ],
            "references": [
                {
                    "text": (
                        "<!-- ref --><P><B>Abu-Lughod, Janet Lippman</B> (1995):"
                        ' "Comparing Chicago, New York y Los Angeles:'
                        ' testing some world cities hypotheses". In Paul L. Knox y Peter J. Taylor (eds.)'
                        " World Cities in a Worldsystem."
                        " Cambridge, UK: Cambridge University Press, pp.171-191.    <BR>&nbsp;"
                    ),
                    "index": "1",
                    "reference_index": "1",
                    "part": "references",
                },
                {
                    "text": "<!-- ref --><P><B>Abu-Lughod, Janet Lippman</B> (1995)</P>",
                    "index": "2",
                    "reference_index": "2",
                    "part": "references",
                },
            ],
            "after references": [
                {
                    "text": "<p>Depois das referencias 1</p>",
                    "index": "",
                    "reference_index": "",
                    "part": "after references",
                },
                {
                    "text": "<p>Depois das referencias 2</p>",
                    "index": "",
                    "reference_index": "",
                    "part": "after references",
                },
            ],
        }


class TestMainHTMLPipe(TestCase):
    def test_transform(self):
        raw = MockMainDocument()
        expected = (
            "<article>"
            "<body>"
            "<p>"
            "<![CDATA[<DIV ALIGN=right>"
            "<B>Saskia Sassen*</B>"
            "</DIV>]]>"
            "</p>"
            "<p>"
            "<![CDATA[<DIV ALIGN=right>"
            "<B>Saskia Sassen*</B>"
            "</DIV>]]>"
            "</p>"
            "</body>"
            "<back>"
            "<ref-list>"
            '<ref id="B1">'
            "<mixed-citation>"
            "<![CDATA[<!-- ref -->"
            "<P>"
            "<B>Abu-Lughod, Janet Lippman</B> (1995):"
            ' "Comparing Chicago, New York y Los Angeles:'
            ' testing some world cities hypotheses". In Paul L. Knox y Peter J. Taylor (eds.)'
            " World Cities in a Worldsystem."
            " Cambridge, UK: Cambridge University Press, pp.171-191.    <BR>&nbsp;]]>"
            "</mixed-citation>"
            "</ref>"
            '<ref id="B2">'
            "<mixed-citation>"
            "<![CDATA[<!-- ref -->"
            "<P>"
            "<B>Abu-Lughod, Janet Lippman</B> (1995)</P>]]>"
            "</mixed-citation>"
            "</ref>"
            "</ref-list>"
            "<sec>"
            "<![CDATA[<p>Depois das referencias 1</p>]]>"
            "</sec>"
            "<sec>"
            "<![CDATA[<p>Depois das referencias 2</p>]]>"
            "</sec>"
            "</back>"
            "</article>"
        )
        xml = get_tree("<article><body></body><back></back></article>")
        data = (raw, xml)

        _, transformed_xml = MainHTMLPipe().transform(data)
        result = tree_tostring_decode(transformed_xml)
        self.assertEqual(expected, result)


class MockTranslatedDocument:
    def __init__(self):
        self.translated_html_by_lang = {
            "pt": {
                "before references": "<DIV ALIGN=right><B>Saskia Sassen*</B></DIV>",
                "after references": "<p>Depois das referencias 1</p>",
            },
            "en": {
                "before references": "<DIV ALIGN=right><B>Saskia Sassen*</B></DIV>",
                "after references": "<p>After Reference</p>",
            },
        }


class TestTranslatedHTMLPipe(TestCase):
    def test_transform(self):
        raw = MockTranslatedDocument()
        expected = (
            "<article>"
            "<body/>"
            "<back>"
            '<sub-article article-type="translation" xml:lang="pt">'
            "<body><![CDATA[<DIV ALIGN=right>"
            "<B>Saskia Sassen*</B>"
            "</DIV>]]>"
            "</body>"
            "<back>"
            "<![CDATA[<p>Depois das referencias 1</p>]]>"
            '<sub-article article-type="translation" xml:lang="en">'
            "<body>"
            "<![CDATA[<DIV ALIGN=right>"
            "<B>Saskia Sassen*</B>"
            "</DIV>]]>"
            "</body>"
            "<back>"
            "<![CDATA[<p>After Reference</p>]]>"
            "</back>"
            "</sub-article>"
            "</back>"
            "</sub-article>"
            "</back>"
            "</article>"
        )
        xml = get_tree("<article><body></body><back></back></article>")
        data = (raw, xml)

        _, transformed_xml = TranslatedHTMLPipe().transform(data)
        result = tree_tostring_decode(transformed_xml)

        self.assertEqual(expected, result)


class TestEndPipe(TestCase):
    def test_transform_remove_CDATA(self):
        xml = get_tree("<root><body>Texto</body></root>")
        expected = b"<root><body>Texto</body></root>"
        data = (None, xml)

        result = EndPipe().transform(data)
        self.assertEqual(expected, result)


class TestRemoveCDATAPipe(TestCase):
    def test_transform_remove_CDATA(self):
        xml = get_tree("<root><![CDATA[Exemplo CDATA.]]></root>")
        expected = "<root>Exemplo CDATA.</root>"
        data = (None, xml)

        _, transformed_xml = RemoveCDATAPipe().transform(data)
        result = tree_tostring_decode(transformed_xml)
        self.assertEqual(expected, result)


class TestRemoveCommentPipe(TestCase):
    def test_transform_remove_comment(self):
        xml = get_tree("<root><body><!-- comentario --><p>Um</p></body></root>")
        expected = "<root><body><p>Um</p></body></root>"
        data = (None, xml)

        _, transformed_xml = RemoveCommentPipe().transform(data)
        result = tree_tostring_decode(transformed_xml)
        self.assertEqual(expected, result)


class TestRemoveTagsPipe(TestCase):
    def setUp(self):
        self.xml = get_tree(
            (
                "<root>"
                "<body>"
                "<p><span>Texto</span></p>"
                "<center>Texto centralizado</center>"
                "<s>Sublinhado</s>"
                "<lixo>Lixo</lixo>"
                "</body>"
                "</root>"
            )
        )

    def test_transform_remove_tags(self):
        expected = (
            "<root><body><p>Texto</p>Texto centralizadoSublinhadoLixo</body></root>"
        )
        data = (None, self.xml)

        _, transformed_xml = RemoveTagsPipe().transform(data)
        result = tree_tostring_decode(transformed_xml)
        self.assertEqual(expected, result)


class TestRenameElementsPipe(TestCase):
    def test_transform_rename_elements(self):
        xml = get_tree(
            (
                "<root>"
                "<div>Um</div>"
                "<dir>"
                "<li>Item 1</li>"
                "<li>Item 2</li>"
                "</dir>"
                "<dl>"
                "<dt>Termo 1</dt>"
                "<dd>Definição 1</dd>"
                "<dt>Termo 2</dt>"
                "<dd>Definição 2</dd>"
                "</dl>"
                "<br></br>"
                "<blockquote>Quote</blockquote>"
                "<b>Bold</b>"
                "<i>Italic</i>"
                "</root>"
            )
        )
        expected = (
            "<root>"
            "<sec>Um</sec>"
            "<ul>"
            "<list-item>Item 1</list-item>"
            "<list-item>Item 2</list-item>"
            "</ul>"
            "<def-list>"
            "<dt>Termo 1</dt>"
            "<def-item>Definição 1</def-item>"
            "<dt>Termo 2</dt>"
            "<def-item>Definição 2</def-item>"
            "</def-list>"
            "<break/>"
            "<disp-quote>Quote</disp-quote>"
            "<bold>Bold</bold>"
            "<italic>Italic</italic>"
            "</root>"
        )
        data = (None, xml)

        _, transformed_xml = RenameElementsPipe().transform(data)
        result = tree_tostring_decode(transformed_xml)
        self.assertEqual(expected, result)

    def test_transform_rename_elements_empty_xml(self):
        expected = "<root/>"
        data = (None, etree.fromstring("<root/>"))

        _, transformed_xml = RenameElementsPipe().transform(data)
        result = tree_tostring_decode(transformed_xml)
        self.assertEqual(expected, result)


class TestFontSymbolPipe(TestCase):
    def test_transform_font_symbol_pipe(self):
        xml = get_tree('<root><font face="symbol">simbolo</font></root>')
        expected = (
            '<root><font-face-symbol face="symbol">simbolo</font-face-symbol></root>'
        )
        data = (None, xml)

        _, transformed_xml = FontSymbolPipe().transform(data)
        result = tree_tostring_decode(transformed_xml)
        self.assertEqual(expected, result)


class TestStylePipe(TestCase):
    def test_transform_style(self):
        xml = get_tree(
            (
                "<root>"
                "<body>"
                "<p><span name='style_bold'>bold text</span></p>"
                "<p><span name='style_italic'>italic text</span></p>"
                "<p><span name='style_sup'>sup text</span></p>"
                "<p><span name='style_sub'>sub text</span></p>"
                "<p><span name='style_underline'>underline text</span></p>"
                "</body>"
                "</root>"
            )
        )
        expected = (
            "<root>"
            "<body>"
            '<p><bold name="style_bold">bold text</bold></p>'
            '<p><italic name="style_italic">italic text</italic></p>'
            '<p><sup name="style_sup">sup text</sup></p>'
            '<p><sub name="style_sub">sub text</sub></p>'
            '<p><underline name="style_underline">underline text</underline></p>'
            "</body>"
            "</root>"
        )
        data = (None, xml)

        _, transformed_xml = StylePipe().transform(data)
        result = tree_tostring_decode(transformed_xml)
        self.assertEqual(expected, result)


class TestOlPipe(TestCase):
    def test_ol_pipe(self):
        raw = None
        xml = get_tree("<root><body><ol>Um</ol></body></root>")
        expected = (
            "<root>"
            "<body>"
            '<list list-type="order">'
            "Um"
            "</list>"
            "</body>"
            "</root>"
        )
        data = (raw, xml)

        _raw, _xml = OlPipe().transform(data)
        result = tree_tostring_decode(_xml)

        self.assertEqual(1, len(_xml.xpath(".//list[@list-type='order']")))
        self.assertEqual(expected, result)


class TestUlPipe(TestCase):
    def test_ul_pipe(self):
        raw = None
        xml = get_tree("<root><body><ul>Um</ul></body></root>")
        expected = (
            "<root>"
            "<body>"
            '<list list-type="bullet">'
            "Um"
            "</list>"
            "</body>"
            "</root>"
        )
        data = (raw, xml)

        _, _xml = UlPipe().transform(data)
        result = tree_tostring_decode(_xml)

        self.assertEqual(1, len(_xml.xpath(".//list[@list-type='bullet']")))
        self.assertEqual(expected, result)


class TestTagsHPipe(TestCase):
    def test_transform_substitui_tags_de_cabecalho_por_tags_title(self):
        xml = get_tree(
            "<root><body><h1>Título 1</h1><h2>Título 2</h2><h3>Título 3</h3></body></root>"
        )
        expected = (
            "<root>"
            "<body>"
            '<title content-type="h1">Título 1</title>'
            '<title content-type="h2">Título 2</title>'
            '<title content-type="h3">Título 3</title>'
            "</body>"
            "</root>"
        )

        data = (None, xml)

        _, transformed_xml = TagsHPipe().transform(data)
        result = tree_tostring_decode(transformed_xml)
        self.assertEqual(expected, result)


class TestASourcePipe(TestCase):
    def test_transform_muda_src_para_href_em_nos_a(self):
        xml = get_tree('<root><body><a src="foo.jpg">Imagem</a></body></root>')
        expected = '<root><body><a href="foo.jpg">Imagem</a></body></root>'
        data = (None, xml)

        _, transformed_xml = ASourcePipe().transform(data)
        result = tree_tostring_decode(transformed_xml)
        self.assertEqual(expected, result)

    def test_transform_nao_altera_nos_a_sem_src(self):
        xml = get_tree('<root><body><a href="foo.jpg">Imagem</a></body></root>')
        data = (None, xml)

        _, transformed_xml = ASourcePipe().transform(data)

        expected = '<root><body><a href="foo.jpg">Imagem</a></body></root>'
        result = tree_tostring_decode(transformed_xml)

        self.assertEqual(expected, result)


class TestANamePipe(TestCase):
    def test_transform_substitui_nos_a_por_divs_com_id(self):
        xml = get_tree('<root><body><a name="secao1">Seção 1</a></body></root>')
        expected = '<root><body><div id="secao1">Seção 1</div></body></root>'
        data = (None, xml)

        _, transformed_xml = ANamePipe().transform(data)
        result = tree_tostring_decode(transformed_xml)
        self.assertEqual(expected, result)


class TestDivIdToTableWrap(TestCase):
    def setUp(self):
        self.input_xml = (
            "<root><body>"
            '<div id="top"></div>'
            '<div id="t1"></div>'
            '<div id="t2"></div>'
            '<div id="t3"></div>'
            '<div id="f1"></div>'
            '<div id="f2"></div>'
            '<div id="f3"></div>'
            "</body></root>"
        )
        self.expected = (
            "<root><body>"
            '<div id="top"/>'
            '<table-wrap id="t1"/>'
            '<table-wrap id="t2"/>'
            '<table-wrap id="t3"/>'
            '<fig id="f1"/>'
            '<fig id="f2"/>'
            '<fig id="f3"/>'
            "</body></root>"
        )
        self.pipe = DivIdToTableWrap()

    def test_transform(self):
        xml = get_tree(self.input_xml)
        data = (None, xml)

        _, transformed_xml = self.pipe.transform(data)
        result = tree_tostring_decode(transformed_xml)
        self.assertEqual(self.expected, result)

    def test_parser_node_with_id_t(self):
        node = etree.Element("div")
        node.set("id", "t1")
        self.pipe.parser_node(node)
        self.assertEqual(node.tag, "table-wrap")

    def test_parser_node_with_id_f(self):
        node = etree.Element("div")
        node.set("id", "f1")
        self.pipe.parser_node(node)
        self.assertEqual(node.tag, "fig")

    def test_parser_node_with_id_top(self):
        node = etree.Element("div")
        node.set("id", "top")
        self.pipe.parser_node(node)
        self.assertEqual(node.tag, "div")
        self.assertEqual(node.get("id"), "top")


class TestImgSrcPipe(TestCase):
    def test_transform_substitui_tags_img_por_grafico_com_href(self):
        xml = get_tree(
            (
                '<root xmlns:xlink="http://www.w3.org/1999/xlink">'
                "<body>"
                '<img src="foo.jpg"></img>'
                "</body>"
                "</root>"
            )
        )
        expected = (
            '<root xmlns:xlink="http://www.w3.org/1999/xlink">'
            "<body>"
            '<graphic xlink:href="foo.jpg"/>'
            "</body>"
            "</root>"
        )
        data = (None, xml)

        _, transformed_xml = ImgSrcPipe().transform(data)
        result = tree_tostring_decode(transformed_xml)
        self.assertEqual(expected, result)


class TestXRefTypePipe(TestCase):
    def test_transform(self):
        raw = None
        xml = get_tree('<root><body><xref rid="t1">Table 1</xref></body></root>')
        expected = (
            '<root><body><xref rid="t1" ref-type="table">Table 1</xref></body></root>'
        )
        data = (raw, xml)

        _, transformed_xml = XRefTypePipe().transform(data)
        result = tree_tostring_decode(transformed_xml)
        self.assertEqual(expected, result)


class TestFigPipe(TestCase):
    def test_transform(self):
        raw = None
        xml = get_tree(
            (
                '<root xmlns:xlink="http://www.w3.org/1999/xlink">'
                "<body>"
                '<p align="center">'
                '<fig id="f1"/>'
                "</p>"
                '<p align="center"></p>'
                '<p align="center">'
                '<graphic xlink:href="/fbpe/img/bres/v48/53f01.jpg"/>'
                "</p>"
                "</body>"
                "</root>"
            )
        )
        expected = (
            '<root xmlns:xlink="http://www.w3.org/1999/xlink">'
            "<body>"
            '<p align="center">'
            '<fig id="f1">'
            '<graphic xlink:href="/fbpe/img/bres/v48/53f01.jpg"/>'
            "</fig>"
            "</p>"
            '<p align="center"/>'
            "</body>"
            "</root>"
        )
        data = (raw, xml)

        _, transformed_xml = FigPipe().transform(data)
        result = tree_tostring_decode(transformed_xml)
        self.assertEqual(expected, result)

    def test_transform_com_mais_paragrafos_vazios(self):
        raw = None
        xml = get_tree(
            (
                '<root xmlns:xlink="http://www.w3.org/1999/xlink">'
                "<body>"
                '<p align="center">'
                '<fig id="f1"/>'
                "</p>"
                '<p align="center"></p>'
                '<p align="center"></p>'
                '<p align="center"></p>'
                '<p align="center">'
                '<graphic xlink:href="/fbpe/img/bres/v48/53f01.jpg"/>'
                "</p>"
                "</body>"
                "</root>"
            )
        )
        expected = (
            '<root xmlns:xlink="http://www.w3.org/1999/xlink">'
            "<body>"
            '<p align="center">'
            '<fig id="f1">'
            '<graphic xlink:href="/fbpe/img/bres/v48/53f01.jpg"/>'
            "</fig>"
            "</p>"
            '<p align="center"/>'
            '<p align="center"/>'
            '<p align="center"/>'
            "</body>"
            "</root>"
        )
        data = (raw, xml)

        _, transformed_xml = FigPipe().transform(data)
        result = tree_tostring_decode(transformed_xml)
        self.assertEqual(expected, result)


class TestInsertGraphicInTableWrapPipe(TestCase):
    def test_transform(self):
        raw = None
        xml = get_tree(
            (
                '<root xmlns:xlink="http://www.w3.org/1999/xlink">'
                "<body>"
                '<p align="center">'
                '<table-wrap id="t1"/>'
                "</p>"
                '<p align="center">'
                '<graphic xlink:href="t01.jpg"/>'
                "</p>"
                "</body>"
                "</root>"
            )
        )
        expected = (
            '<root xmlns:xlink="http://www.w3.org/1999/xlink">'
            "<body>"
            '<p align="center">'
            '<table-wrap id="t1">'
            '<graphic xlink:href="t01.jpg"/>'
            "</table-wrap>"
            "</p>"
            "</body>"
            "</root>"
        )
        data = (raw, xml)

        _, transformed_xml = InsertGraphicInTableWrapPipe().transform(data)
        result = tree_tostring_decode(transformed_xml)
        self.assertEqual(expected, result)

    def test_transform_with_table(self):
        raw = None
        xml = get_tree(
            (
                '<root xmlns:xlink="http://www.w3.org/1999/xlink">'
                "<body>"
                '<p align="center">'
                '<table-wrap id="t1"/>'
                "</p>"
                '<p align="center">'
                "<table><tbody><tr><td>Um</td></tr></tbody></table>"
                "</p>"
                "</body>"
                "</root>"
            )
        )
        expected = (
            '<root xmlns:xlink="http://www.w3.org/1999/xlink">'
            "<body>"
            '<p align="center">'
            '<table-wrap id="t1">'
            "<table><tbody><tr><td>Um</td></tr></tbody></table>"
            "</table-wrap>"
            "</p>"
            "</body>"
            "</root>"
        )
        data = (raw, xml)

        _, transformed_xml = InsertGraphicInTableWrapPipe().transform(data)
        result = tree_tostring_decode(transformed_xml)
        self.assertEqual(expected, result)


class TestRemoveEmptyPTagPipe(TestCase):
    def test_transform1(self):
        # Testa a remoção de <p></p> vazios.
        raw = None
        xml = get_tree(
            (
                '<root xmlns:xlink="http://www.w3.org/1999/xlink">'
                "<body>"
                '<p align="center">Lorem ipsum</p>'
                '<p align="center"> </p>'
                '<p align="center"> </p>'
                '<p align="center"> </p>'
                '<p align="center">The quick brown fox jumps over the lazy dog.</p>'
                "</body>"
                "</root>"
            )
        )
        expected = (
            '<root xmlns:xlink="http://www.w3.org/1999/xlink">'
            "<body>"
            '<p align="center">Lorem ipsum</p>'
            '<p align="center">The quick brown fox jumps over the lazy dog.</p>'
            "</body>"
            "</root>"
        )
        data = (raw, xml)

        _, transformed_xml = RemoveEmptyPTagPipe().transform(data)
        result = tree_tostring_decode(transformed_xml)

        self.assertEqual(expected, result)

    def test_transform2(self):
        # Testa se o graphic se mantem.
        raw = None
        xml = get_tree(
            (
                '<root xmlns:xlink="http://www.w3.org/1999/xlink">'
                "<body>"
                '<p align="center"><graphic></graphic></p>'
                "</body>"
                "</root>"
            )
        )
        expected = (
            '<root xmlns:xlink="http://www.w3.org/1999/xlink">'
            "<body>"
            '<p align="center"><graphic/></p>'
            "</body>"
            "</root>"
        )
        data = (raw, xml)

        _, transformed_xml = RemoveEmptyPTagPipe().transform(data)
        result = tree_tostring_decode(transformed_xml)

        self.assertEqual(expected, result)

    def test_transform3(self):
        # Testa se um texto formatado dentro de p se mantém, no caso o bold.
        raw = None
        xml = get_tree(
            (
                '<root xmlns:xlink="http://www.w3.org/1999/xlink">'
                "<body>"
                '<p align="center">Lorem ipsum</p>'
                '<p align="center"> </p>'
                '<p align="center"> </p>'
                '<p align="center"> </p>'
                '<p align="center">The quick <b>brown</b> fox jumps over the lazy dog.</p>'
                "</body>"
                "</root>"
            )
        )
        expected = (
            '<root xmlns:xlink="http://www.w3.org/1999/xlink">'
            "<body>"
            '<p align="center">Lorem ipsum</p>'
            '<p align="center">The quick <b>brown</b> fox jumps over the lazy dog.</p>'
            "</body>"
            "</root>"
        )
        data = (raw, xml)

        _, transformed_xml = RemoveEmptyPTagPipe().transform(data)
        result = tree_tostring_decode(transformed_xml)

        self.assertEqual(expected, result)

    def test_transform4(self):
        # testa um p dentro de outro p.
        raw = None
        xml = get_tree(
            (
                '<root xmlns:xlink="http://www.w3.org/1999/xlink">'
                "<body>"
                '<p align="center"><p>Inner</p></p>'
                "</body>"
                "</root>"
            )
        )
        expected = (
            '<root xmlns:xlink="http://www.w3.org/1999/xlink">'
            "<body>"
            '<p align="center"><p>Inner</p></p>'
            "</body>"
            "</root>"
        )
        data = (raw, xml)

        _, transformed_xml = RemoveEmptyPTagPipe().transform(data)
        result = tree_tostring_decode(transformed_xml)

        self.assertEqual(expected, result)

    def test_transform5(self):
        # testa um p dentro de outro p, onde o segundo é vazio.
        raw = None
        xml = get_tree(
            (
                '<root xmlns:xlink="http://www.w3.org/1999/xlink">'
                "<body>"
                '<p align="center"><p> </p></p>'
                "</body>"
                "</root>"
            )
        )
        expected = (
            '<root xmlns:xlink="http://www.w3.org/1999/xlink">'
            "<body>"
            '<p align="center"/>'
            "</body>"
            "</root>"
        )
        data = (raw, xml)

        _, transformed_xml = RemoveEmptyPTagPipe().transform(data)
        result = tree_tostring_decode(transformed_xml)

        self.assertEqual(expected, result)

    def test_transform6(self):
        raw = None
        xml = get_tree(
            (
                '<root xmlns:xlink="http://www.w3.org/1999/xlink">'
                "<body>"
                "<div>"
                "<p> </p> The quick brown fox jumps over the lazy dog."
                "</div>"
                "</body>"
                "</root>"
            )
        )
        expected = (
            '<root xmlns:xlink="http://www.w3.org/1999/xlink">'
            "<body>"
            "<div>"
            " The quick brown fox jumps over the lazy dog."
            "</div>"
            "</body>"
            "</root>"
        )
        data = (raw, xml)

        _, transformed_xml = RemoveEmptyPTagPipe().transform(data)
        result = tree_tostring_decode(transformed_xml)

        self.assertEqual(expected, result)


class TestRemoveParentPTagOfGraphicPipe(TestCase):
    def test_transform1(self):
        raw = None
        xml = get_tree(
            (
                '<root xmlns:xlink="http://www.w3.org/1999/xlink">'
                "<body>"
                '<p align="center">'
                '<graphic xlink:href="t01.jpg"/>'
                "</p>"
                "</body>"
                "</root>"
            )
        )
        expected = (
            '<root xmlns:xlink="http://www.w3.org/1999/xlink">'
            "<body>"
            '<graphic xlink:href="t01.jpg"/>'
            "</body>"
            "</root>"
        )
        data = (raw, xml)

        _, transformed_xml = RemoveParentPTagOfGraphicPipe().transform(data)
        result = tree_tostring_decode(transformed_xml)

        self.assertEqual(expected, result)

    def test_transform2(self):
        raw = None
        xml = get_tree(
            (
                '<root xmlns:xlink="http://www.w3.org/1999/xlink">'
                "<body>"
                "<p>"
                '<p align="center">'
                '<graphic xlink:href="t01.jpg"/>'
                "</p>"
                '<p align="center"> </p>'
                "</p>"
                '<p align="center"> </p>'
                "</body>"
                "</root>"
            )
        )
        expected = (
            '<root xmlns:xlink="http://www.w3.org/1999/xlink">'
            "<body>"
            "<p>"
            '<graphic xlink:href="t01.jpg"/>'
            '<p align="center"> </p>'
            "</p>"
            '<p align="center"> </p>'
            "</body>"
            "</root>"
        )
        data = (raw, xml)

        _, transformed_xml = RemoveParentPTagOfGraphicPipe().transform(data)
        result = tree_tostring_decode(transformed_xml)

        self.assertEqual(expected, result)


class TestInlineGraphicPipe(TestCase):
    def test_transform1(self):
        raw = None
        xml = get_tree(
            '<root xmlns:xlink="http://www.w3.org/1999/xlink"><body><p><graphic/></p></body></root>'
        )
        expected = '<root xmlns:xlink="http://www.w3.org/1999/xlink"><body><p><graphic/></p></body></root>'
        data = (raw, xml)

        _, transformed_xml = InlineGraphicPipe().transform(data)
        result = tree_tostring_decode(transformed_xml)

        self.assertEqual(expected, result)

    def test_transform2(self):
        raw = None
        xml = get_tree(
            '<root xmlns:xlink="http://www.w3.org/1999/xlink"><body><p><graphic id="g1" xlink:href="d1"/>: Rotational</p></body></root>'
        )
        expected = '<root xmlns:xlink="http://www.w3.org/1999/xlink"><body><p><inline-graphic id="g1" xlink:href="d1"/>: Rotational</p></body></root>'
        data = (raw, xml)

        _, transformed_xml = InlineGraphicPipe().transform(data)
        result = tree_tostring_decode(transformed_xml)

        self.assertEqual(expected, result)

    def test_transform3(self):
        raw = None
        xml = get_tree(
            '<root xmlns:xlink="http://www.w3.org/1999/xlink"><body><p>Models to approximate the bound frequencies as waves in X→M (<graphic id="g1" xlink:href="d1"/></p></body></root>'
        )
        expected = '<root xmlns:xlink="http://www.w3.org/1999/xlink"><body><p>Models to approximate the bound frequencies as waves in X→M (<inline-graphic id="g1" xlink:href="d1"/></p></body></root>'
        data = (raw, xml)

        _, transformed_xml = InlineGraphicPipe().transform(data)
        result = tree_tostring_decode(transformed_xml)

        self.assertEqual(expected, result)

    def test_transform4(self):
        raw = None
        xml = get_tree(
            '<root xmlns:xlink="http://www.w3.org/1999/xlink"><body><p><italic>y</italic> direction, <graphic id="g3" xlink:href="d3"/></p></body></root>'
        )
        expected = '<root xmlns:xlink="http://www.w3.org/1999/xlink"><body><p><italic>y</italic> direction, <inline-graphic id="g3" xlink:href="d3"/></p></body></root>'
        data = (raw, xml)

        _, transformed_xml = InlineGraphicPipe().transform(data)
        result = tree_tostring_decode(transformed_xml)

        self.assertEqual(expected, result)

    def test_transform5(self):
        raw = None
        xml = get_tree(
            '<root xmlns:xlink="http://www.w3.org/1999/xlink"><body><p>Models to approximate the bound frequencies as waves in X→M (<graphic id="g1" xlink:href="d1"/>: Rotational, <graphic id="g2" xlink:href="d2"/>: Vibrate in <italic>y</italic> direction, <graphic id="g3" xlink:href="d3"/>: Vibrate in <italic>x</italic> direction, <graphic id="g4" xlink:href="d4"/>: Vibrate mainly in <italic>y</italic> direction including a small portion of vibration in <italic>x</italic> direction, <graphic id="g5" xlink:href="d5"/>: Vibrate mainly in <italic>x</italic> direction including a small portion of vibration in <italic>y</italic> direction).</p></body></root>'
        )
        expected = '<root xmlns:xlink="http://www.w3.org/1999/xlink"><body><p>Models to approximate the bound frequencies as waves in X→M (<inline-graphic id="g1" xlink:href="d1"/>: Rotational, <inline-graphic id="g2" xlink:href="d2"/>: Vibrate in <italic>y</italic> direction, <inline-graphic id="g3" xlink:href="d3"/>: Vibrate in <italic>x</italic> direction, <inline-graphic id="g4" xlink:href="d4"/>: Vibrate mainly in <italic>y</italic> direction including a small portion of vibration in <italic>x</italic> direction, <inline-graphic id="g5" xlink:href="d5"/>: Vibrate mainly in <italic>x</italic> direction including a small portion of vibration in <italic>y</italic> direction).</p></body></root>'
        data = (raw, xml)

        _, transformed_xml = InlineGraphicPipe().transform(data)
        result = tree_tostring_decode(transformed_xml)

        self.assertEqual(expected, result)

    def test_transform6(self):
        raw = None
        xml = get_tree(
            (
                '<root xmlns:xlink="http://www.w3.org/1999/xlink">'
                "<body>"
                "<p><graphic/>... <graphic/><graphic/><graphic/>....</p>"
                "</body>"
                "</root>"
            )
        )
        expected = (
            '<root xmlns:xlink="http://www.w3.org/1999/xlink">'
            "<body>"
            "<p><inline-graphic/>... <inline-graphic/><inline-graphic/><inline-graphic/>....</p>"
            "</body>"
            "</root>"
        )
        data = (raw, xml)

        _, transformed_xml = InlineGraphicPipe().transform(data)
        result = tree_tostring_decode(transformed_xml)

        self.assertEqual(expected, result)


class TestInsertCaptionAndTitleInTableWrapPipe(TestCase):
    # https://scielo.readthedocs.io/projects/scielo-publishing-schema/pt_BR/latest/tagset/elemento-table-wrap.html
    def test_transform_com_label(self):
        raw = None
        xml = get_tree(
            (
                '<root xmlns:xlink="http://www.w3.org/1999/xlink">'
                "<body>"
                '<p>Mixtures for each of the diets were prepared on an industrial mixer at the Molino La Estampa, Chile, using the proportions for each of the ingredients shown in <xref rid="t1" ref-type="table">Table 1</xref> <xref rid="t2" ref-type="table">Table 2</xref>. Food pellets for each of the animal diets were prepared daily by adding the same amount of water to a fraction of each of the powder mixtures.</p>'
                '<p align="center">'
                '<table-wrap id="t1"/>'
                "</p>"
                '<p align="center"><b>Table 1 Composition and energy provide by the experimental diets</b></p>'
                '<p align="center">'
                '<graphic xlink:href="t01.jpg"/>'
                "</p>"
                "</body>"
                "</root>"
            )
        )
        expected = (
            '<root xmlns:xlink="http://www.w3.org/1999/xlink">'
            "<body>"
            '<p>Mixtures for each of the diets were prepared on an industrial mixer at the Molino La Estampa, Chile, using the proportions for each of the ingredients shown in <xref rid="t1" ref-type="table">Table 1</xref> <xref rid="t2" ref-type="table">Table 2</xref>. Food pellets for each of the animal diets were prepared daily by adding the same amount of water to a fraction of each of the powder mixtures.</p>'
            '<p align="center">'
            '<table-wrap id="t1">'
            "<label>"
            "Table 1"
            "</label>"
            "<caption>"
            "<title>"
            "Composition and energy provide by the experimental diets"
            "</title>"
            "</caption>"
            "</table-wrap>"
            "</p>"
            '<p align="center">'
            '<graphic xlink:href="t01.jpg"/>'
            "</p>"
            "</body>"
            "</root>"
        )
        data = (raw, xml)

        _, transformed_xml = InsertCaptionAndTitleInTableWrapPipe().transform(data)
        result = tree_tostring_decode(transformed_xml)
        self.assertEqual(expected, result)

    def test_transform_sem_label(self):
        raw = None
        xml = get_tree(
            (
                '<root xmlns:xlink="http://www.w3.org/1999/xlink">'
                "<body>"
                "<p>Mixtures for each of the diets were prepared on an industrial mixer at the Molino La Estampa, Chile, using the proportions for each of the ingredients shown in. Food pellets for each of the animal diets were prepared daily by adding the same amount of water to a fraction of each of the powder mixtures.</p>"
                '<p align="center">'
                '<table-wrap id="t1"/>'
                "</p>"
                '<p align="center"><b>Table 1 Composition and energy provide by the experimental diets</b></p>'
                '<p align="center">'
                '<graphic xlink:href="t01.jpg"/>'
                "</p>"
                "</body>"
                "</root>"
            )
        )
        expected = (
            '<root xmlns:xlink="http://www.w3.org/1999/xlink">'
            "<body>"
            "<p>Mixtures for each of the diets were prepared on an industrial mixer at the Molino La Estampa, Chile, using the proportions for each of the ingredients shown in. Food pellets for each of the animal diets were prepared daily by adding the same amount of water to a fraction of each of the powder mixtures.</p>"
            '<p align="center">'
            '<table-wrap id="t1">'
            "<caption>"
            "<title>"
            "Composition and energy provide by the experimental diets"
            "</title>"
            "</caption>"
            "</table-wrap>"
            "</p>"
            '<p align="center">'
            '<graphic xlink:href="t01.jpg"/>'
            "</p>"
            "</body>"
            "</root>"
        )
        data = (raw, xml)

        _, transformed_xml = InsertCaptionAndTitleInTableWrapPipe().transform(data)
        result = tree_tostring_decode(transformed_xml)
        self.assertEqual(expected, result)


class TestInsertTableWrapFootInTableWrapPipe(TestCase):
    def test_transform(self):
        raw = None
        xml = get_tree(
            (
                '<root xmlns:xlink="http://www.w3.org/1999/xlink">'
                "<body>"
                '<p align="center">'
                '<table-wrap id="t1">'
                '<graphic xlink:href="t01.jpg"/>'
                "</table-wrap>"
                "</p>"
                "<p>The quick brown fox jumps over the lazy dog.</p>"
                "</body>"
                "</root>"
            )
        )
        expected = (
            '<root xmlns:xlink="http://www.w3.org/1999/xlink">'
            "<body>"
            '<p align="center">'
            '<table-wrap id="t1">'
            '<graphic xlink:href="t01.jpg"/>'
            "<table-wrap-foot>"
            "<p>The quick brown fox jumps over the lazy dog.</p>"
            "</table-wrap-foot>"
            "</table-wrap>"
            "</p>"
            "</body>"
            "</root>"
        )
        data = (raw, xml)

        _, transformed_xml = InsertTableWrapFootInTableWrapPipe().transform(data)
        result = tree_tostring_decode(transformed_xml)

        self.assertEqual(expected, result)


class TestAlternativesGraphicPipe(TestCase):
    def test_transform(self):
        raw = None
        xml = get_tree(
            (
                '<root xmlns:xlink="http://www.w3.org/1999/xlink">'
                "<body>"
                '<p align="center">'
                '<a href="/fbpe/img/bres/v48/53t03.jpg">'
                '<graphic xlink:href="/fbpe/img/bres/v48/53t03thumb.jpg"/>'
                "</a>"
                "</p>"
                "</body>"
                "</root>"
            )
        )
        expected = (
            '<root xmlns:xlink="http://www.w3.org/1999/xlink">'
            "<body>"
            '<p align="center">'
            "<alternatives>"
            '<graphic xlink:href="/fbpe/img/bres/v48/53t03.jpg"/>'
            '<graphic xlink:href="/fbpe/img/bres/v48/53t03.jpg" specific-use="scielo-web"/>'
            '<graphic xlink:href="/fbpe/img/bres/v48/53t03thumb.jpg" specific-use="scielo-web" content-type="scielo-267x140"/>'
            "</alternatives>"
            "</p>"
            "</body>"
            "</root>"
        )
        data = (raw, xml)

        _, transformed_xml = AlternativesGraphicPipe().transform(data)
        result = tree_tostring_decode(transformed_xml)

        self.assertEqual(expected, result)
