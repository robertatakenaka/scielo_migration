import logging

from scielo_classic_website.isisdb.c_record import ReferenceRecord


def html_decode(text):
    # TODO https://github.com/scieloorg/xylose/blob/262126e37e55bb7df2ebc585472f260daddedce9/xylose/scielodocument.py#L124
    return text


class Reference:
    def __init__(self, record=None, fix_function=None):
        self._reference_record = ReferenceRecord(record)
        self._reference_record.fix_function = fix_function

    def __getattr__(self, name):
        # desta forma Reference não precisa herdar de ReferenceRecord
        # fica menos acoplado
        if hasattr(self._reference_record, name):
            return getattr(self._reference_record, name)
        raise AttributeError(
            f"classic_website.Reference has no attribute {name}")

    @property
    def record(self):
        return self._reference_record.record

    @property
    def publication_type(self):
        """
        This method retrieves the publication type of the citation.
        """
        if self._reference_record.publication_type:
            return self._reference_record.publication_type

        if self.reference_record.patent:
            return 'patent'

        if self.reference_record.conference:
            return 'confproc'

        if self._reference_record.thesis_degree:
            return 'thesis'

        if self._reference_record.monographic_title:
            return 'book'

        if self._reference_record.article_title:
            return 'journal'

        if self._reference_record.ext_link:
            return 'webpage'

    def _get_pages(self):
        for page in self._reference_record.pages:
            self._start_page = page.get("first")
            self._end_page = page.get("last")
            self._elocation = page.get("elocation")
            self._pages_range = page.get("range")
            return

        pages_range = self._reference_record.pages_range
        self._elocation = pages_range.get("elocation")
        self._pages_range = pages_range.get("range")
        if self._pages_range:
            self._start_page = self._pages_range.split('-')[0]
            self._end_page = self._pages_range.split('-')[-1]
        else:
            self._start_page = None
            self._end_page = None

    @property
    def start_page(self):
        """
        This method retrieves the start page of the citation.
        This method deals with the legacy fields (514 and 14).
        """
        if not hasattr(self, '_start_page'):
            self._get_pages()
        return self._start_page

    @property
    def end_page(self):
        """
        This method retrieves the end page of the citation.
        This method deals with the legacy fields (514 and 14).
        """
        if not hasattr(self, '_end_page'):
            self._get_pages()
        return self._end_page

    @property
    def elocation(self):
        """
        This method retrieves the e-location of the citation.
        This method deals with the legacy fields (514 and 14).
        """
        if not hasattr(self, '_elocation'):
            self._get_pages()
        return self._elocation

    @property
    def pages(self):
        """
        This method retrieves the start and end page of the citation
        separeted by hipen.
        This method deals with the legacy fields (514 and 14).
        """
        if not hasattr(self, '_pages_range'):
            self._get_pages()
        return self._pages_range

    @property
    def source(self):
        """
        This method retrieves the citation source title. Ex:
        Journal: Journal of Microbiology
        Book: Alice's Adventures in Wonderland
        """
        return (
            self._reference_record.monographic_title['text'] or
            self._reference_record.source
        )

    @property
    def chapter_title(self):
        """
        If it is a book citation, this method retrieves a chapter title, if it exists.
        """
        if self.publication_type == 'book':
            return self._reference_record.article_title['text']

    @property
    def article_title(self):
        """
        If it is an article citation, this method retrieves the article title, if it exists.
        """
        if self.publication_type == 'journal':
            return self._reference_record.article_title['text']

    @property
    def thesis_title(self):
        """
        If it is a thesis citation, this method retrieves the thesis title, if it exists.
        """
        if self.publication_type == 'thesis':
            return self._reference_record.monographic_title['text']

    @property
    def conference_title(self):
        if self.publication_type == 'confproc':
            return self._reference_record.article_title['text']

    @property
    def link_title(self):
        """
        If it is a link citation, this method retrieves the link title, if it exists.
        """
        if self.publication_type == 'webpage':
            if self._reference_record.article_title:
                return self._reference_record.article_title['text']
            if self._reference_record.monographic_title:
                return self._reference_record.monographic_title['text']

    @property
    def date(self):
        """
        This method retrieves the date, if it is exists, according to the
        reference type
        Se é desejável obter a data de publicação, usar: self.publication_date
        """
        if self.publication_type == 'confproc':
            return self._reference_record.conference_date_iso
        if self.publication_type == 'thesis':
            return self._reference_record.thesis_date_iso
        if self.publication_type == 'webpage':
            return self._reference_record.access_date_iso
        return self._reference_record.conference_date_iso

    @property
    def publication_date(self):
        """
        This method retrieves the publication date, if it is exists.
        """
        return (
            self._reference_record.publication_date_iso or
            self._reference_record.access_date_iso or
            self._reference_record.conference_date_iso or
            self._reference_record.thesis_date_iso
        )
