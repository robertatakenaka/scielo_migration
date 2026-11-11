from unittest import TestCase

from scielo_classic_website.isisdb.h_record import DocumentRecord
from scielo_classic_website.models.document import Document


def _record(rec_type, v702, pid="S0034-89102004000200002"):
    return {
        "v706": [{"_": rec_type}],
        "v880": [{"_": pid}],
        "v702": [{"_": v702}],
    }


class TestDocumentRecordFilename(TestCase):
    def _make(self, v702):
        return DocumentRecord(_record("h", v702))

    def test_unix_path(self):
        rec = self._make("/scielo/serial/rsp/v38n2/markup/19773.htm")
        self.assertEqual(rec.file_code, "/scielo/serial/rsp/v38n2/markup/19773.htm")
        self.assertEqual(rec.filename, "19773.htm")
        self.assertEqual(rec.filename_without_extension, "19773")
        self.assertEqual(rec.file_type, "html")

    def test_windows_path(self):
        rec = self._make(r"C:\SciELO\Serial\rsp\v38n2\markup\19773.htm")
        self.assertEqual(rec.file_code, "C:/SciELO/Serial/rsp/v38n2/markup/19773.htm")
        self.assertEqual(rec.filename, "19773.htm")
        self.assertEqual(rec.filename_without_extension, "19773")
        self.assertEqual(rec.file_type, "html")

    def test_windows_path_with_digits_after_backslash(self):
        # "\1", "\7"... não podem virar caracteres de controle
        rec = self._make(r"C:\SciELO\Serial\MIOC\v92n2\Markup\3116.htm")
        self.assertEqual(rec.filename_without_extension, "3116")
        self.assertEqual(rec.file_code, "C:/SciELO/Serial/MIOC/v92n2/Markup/3116.htm")

    def test_uppercase_extension(self):
        rec = self._make(r"C:\SciELO\Serial\MIOC\v92n2\Markup\3116.HTM")
        self.assertEqual(rec.filename, "3116.HTM")
        self.assertEqual(rec.filename_without_extension, "3116")
        self.assertEqual(rec.file_type, "html")

    def test_html_extension(self):
        rec = self._make("/scielo/serial/mioc/v99n1/markup/a01v99n1.html")
        self.assertEqual(rec.filename_without_extension, "a01v99n1")
        self.assertEqual(rec.file_type, "html")

    def test_xml_extension(self):
        rec = self._make("/scielo/serial/mioc/v115/markup_xml/scielo_package/1678-8060-mioc-115-e190001.xml")
        self.assertEqual(rec.filename, "1678-8060-mioc-115-e190001.xml")
        self.assertEqual(rec.filename_without_extension, "1678-8060-mioc-115-e190001")
        self.assertEqual(rec.file_type, "xml")

    def test_only_last_extension_is_removed(self):
        rec = self._make("/scielo/serial/mioc/v82s1/markup/vol82(fsup1)_48-82.pdf.htm")
        self.assertEqual(rec.filename_without_extension, "vol82(fsup1)_48-82.pdf")


class TestDocumentFilename(TestCase):
    def test_document_with_o_h_f_records_uses_f_record(self):
        doc = Document({"article": [
            _record("o", "/serial/rsp/v38n2/markup/o_record.htm"),
            _record("h", "/serial/rsp/v38n2/markup/h_record.htm"),
            _record("f", "/serial/rsp/v38n2/markup/f_record.xml"),
        ]})
        # Document delega para h_record (registro "f")
        self.assertEqual(doc.filename_without_extension, doc.h_record.filename_without_extension)
        self.assertEqual(doc.filename_without_extension, "f_record")
        self.assertEqual(doc.filename, "f_record.xml")
        self.assertEqual(doc.file_type, "xml")
        self.assertEqual(doc.file_code, "/serial/rsp/v38n2/markup/f_record.xml")

    def test_document_with_windows_path(self):
        doc = Document({"article": [
            _record("o", r"C:\SciELO\Serial\MIOC\v92n2\Markup\3116.HTM", "S0074-02761997000200008"),
            _record("h", r"C:\SciELO\Serial\MIOC\v92n2\Markup\3116.HTM", "S0074-02761997000200008"),
            _record("f", r"C:\SciELO\Serial\MIOC\v92n2\Markup\3116.HTM", "S0074-02761997000200008"),
        ]})
        self.assertEqual(doc.filename_without_extension, "3116")
        self.assertEqual(doc.filename, "3116.HTM")
        self.assertEqual(doc.file_type, "html")
