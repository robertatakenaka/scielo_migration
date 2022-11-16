import warnings


def warn_future_deprecation(old, new, details=''):
    msg = '"{}" will be deprecated in future version. '.format(old) + \
        'Use "{}" instead. {}'.format(new, details)
    warnings.warn(msg, PendingDeprecationWarning)


class ReferenceXyloseAdapter:

    def __init__(self, fix_function, record=None, reference_record=None):
        if record:
            self._reference_record = ReferenceRecord(_record, fix_function)
        elif reference_record:
            self._reference_record = reference_record
            self._reference_record.fix_function = fix_function

    def __getattr__(self, name):
        # desta forma Reference não precisa herdar de ReferenceRecord
        # fica menos acoplado
        if hasattr(self._reference_record, name):
            return getattr(self._reference_record, name)
        raise AttributeError(
            f"xylose_adapters.Reference has no attribute {name}")

    @property
    def conference_name(self):
        """
        If it is a conference citation, this method retrieves the conference name, if it exists.
        """
        titles = []
        for item in self._reference_record.conferences:
            try:
                name = f"{item.get('number') or ''} {item['name']}".strip()
                titles.append(name)
            except KeyError:
                continue

        return '; '.join(titles)

    def title(self):
        """
        This method returns the first title independent of citation type
        """
        type_titles = ['article_title', 'thesis_title', 'conference_title', 'link_title']

        titles = []

        for title in type_titles:
            if getattr(self, title):
                titles.append(getattr(self, title))

        return ', '.join(titles)

    @property
    def conference_sponsor(self):
        """
        If it is a conference citation, this method retrieves the conference sponsor, if it exists.
        The conference sponsor is presented like it is in the citation. (v52)
        """
        if self.publication_type == 'confproc':
            org = [
                self._reference_record.conference_organization.get("name"),
                self._reference_record.conference_organization.get('division'),
            ]
            return ", ".join([item for item in org if item])

    @property
    def conference_location(self):
        """
        If it is a conference citation, this method retrieves the conference location, if it exists.
        The conference location is presented like it is in the citation. (v56)
        """
        items = [
            self._reference_record.conference_location.get("city"),
            self._reference_record.conference_location.get("state"),
            self._reference_record.conference_country,
        ]
        return ", ".join([c for c in items if c])

    @property
    def link(self):
        """
        This method retrieves a link, if it is exists.
        """
        return self._reference_record.ext_link

    @property
    def first_page(self):
        return self._reference_record.start_page

    @property
    def last_page(self):
        return self._reference_record.end_page

    @property
    def institutions(self):
        """
        This method retrieves the institutions in the given citation without
        care about the citation type (article, book, thesis, conference, etc).
        """
        institutions = []
        institutions.extend(
            self._reference_record.analytic_corporative_authors or []
        )
        institutions.extend(
            self._reference_record.monographic_corporative_authors or []
        )
        institutions.extend(
            self._reference_record.serial_corporative_authors or []
        )
        institutions.extend(
            self._reference_record.thesis_organization or []
        )
        institutions.extend(
            self._reference_record.conference_organization or []
        )
        for inst in institutions:
            items = [
                inst['name'],
                inst.get("division")
            ]
            yield ", ".join([c for c in items if c])

    @property
    def analytic_institution_authors(self):
        """
        It retrieves the analytic institution authors of a reference,
        no matter the publication type of the reference.
        It is not desirable to return conditioned to the publication type,
        because not only articles or books have institution authors.
        IT REPLACES analytic_institution
        """
        for inst in self._reference_record.analytic_corporative_authors:
            items = [
                inst['name'],
                inst.get("division")
            ]
            yield ", ".join([c for c in items if c])

    @property
    def monographic_institution_authors(self):
        """
        It retrieves the monographic institution authors of a reference,
        no matter the publication type of the reference.
        It is not desirable to return conditioned to the publication type,
        because not only books have institution authors.
        IT REPLACES monographic_institution
        """
        for inst in self._reference_record.monographic_corporative_authors:
            items = [
                inst['name'],
                inst.get("division")
            ]
            yield ", ".join([c for c in items if c])

    @property
    def monographic_institution(self):
        """
        This method retrieves the institutions in the given citation. The
        citation must be a book citation, if it exists.
        IT WILL BE DEPRECATED. Use monographic_institution_authors instead.
        """
        return self.monographic_institution_authors

    @property
    def sponsor(self):
        """
        This method retrieves the sponsors in the given citation, if it exists.
        """
        if self._reference_record.project_sponsor:
            items = [
                self._reference_record.project_sponsor['name'],
                self._reference_record.project_sponsor.get("division")
            ]
            yield ", ".join([c for c in items if c])

    @property
    def editor(self):
        """
        This method retrieves the editors in the given citation, if it exists.
        """
        for inst in self._reference_record.serial_corporative_authors:
            items = [
                inst['name'],
                inst.get("division")
            ]
            yield ", ".join([c for c in items if c])

    @property
    def thesis_institution(self):
        """
        This method retrieves the thesis institutions in the given citation, if
        it exists.
        """
        if self._reference_record.thesis_organization:
            items = [
                self._reference_record.thesis_organization['name'],
                self._reference_record.thesis_organization.get("division")
            ]
            yield ", ".join([c for c in items if c])

    @property
    def comment(self):
        """
        This method retrieves the citation comment, mainly used in link citation
        if exists (v61).
        """
        if self.publication_type == 'webpage':
            for item in self._reference_record.notes:
                return 'Available at: <ext-link ext-link-type="uri" ns0:href="{0}">{1}</ext-link>'.format(self.link, self.link)
        return " | ".join(self._reference_record.notes)

    @property
    def mixed_citation(self):
        return self._reference_record.paragraph_text

    @property
    def link_access_date(self):
        """
        This method retrieves the citation access date, mainly used in link citation
        if exists (v109).
        """
        return self._reference_record.access_date

    @property
    def issue(self):
        """
        This method retrieves the journal issue number, if it exists. The
        citation must be an article citation.
        """
        return self._reference_record.issue.get("number")

    @property
    def supplement(self):
        """
        This method retrieves the journal issue number, if it exists. The
        citation must be an article citation.
        """
        return self._reference_record.issue.get("suppl")

    @property
    def authors_groups(self):
        """
        It retrieves all the authors (person and institution) and
        identifies their type (analytic or monographic).
        IT REPLACES authors which returns only person authors
        """
        authors = {}
        if self.analytic_authors_group:
            authors['analytic'] = self.analytic_authors_group
        if self.monographic_authors_group:
            authors['monographic'] = self.monographic_authors_group
        if len(authors) > 0:
            return authors

    @property
    def authors(self):
        """
        This method retrieves the analytic and monographic person authors
        of a citation.
        IT WILL BE DEPRECATED.
        Use authors_groups to retrieve all the authors (person and institution)
        and (analytic and monographic)
        """
        warn_future_deprecation(
            'authors',
            'author_groups',
            'The attribute "author_groups" returns all the authors '
            '(person and institution) '
            'identified by their type (analytic or monographic). '
            'The attribute "authors" returns only person authors and do not '
            'differs analytic from monographic'
        )
        return (self.analytic_authors or []) + (self.monographic_authors or [])

    @property
    def analytic_authors_group(self):
        """
        It retrieves all the analytic authors (person and institution).
        IT REPLACES analytic_authors which returns only person authors
        """
        analytic = {
            'person': list(
                self._reference_record.analytic_person_authors),
            'institution': list(
                self._reference_record.analytic_corporative_authors),
        }
        if not analytic['person']:
            analytic.pop('person')
        if not analytic['institution']:
            analytic.pop('institution')
        if len(analytic) > 0:
            return analytic

    @property
    def analytic_authors(self):
        """
        Analytic Author
        v010 {'_': 'anonymous', 'n': 'given_names', 'p': 'prefix', 'r': 'role', 's': 'surname'}
        """
        return list(self._reference_record.analytic_person_authors)

    @property
    def monographic_authors_group(self):
        """
        It retrieves all the monographic authors (person and institution).
        IT REPLACES monographic_authors
        """
        monographic = {
            'person': list(
                self._reference_record.monographic_person_authors),
            'institution': list(
                self._reference_record.monographic_corporative_authors),
        }
        if not monographic['person']:
            monographic.pop('person')
        if not monographic['institution']:
            monographic.pop('institution')
        if len(monographic) > 0:
            return monographic

    @property
    def monographic_authors(self):
        """
        It retrieves only monographic person authors of a reference.
        IT WILL BE DEPRECATED.
        To retrieve only monographic person authors,
        use monographic_person_authors instead.
        To retrieve all monographic authors (person and institution),
        use monographic_authors_group instead.
        """
        warn_future_deprecation(
            'monographic_authors',
            'monographic_person_authors or monographic_authors_group',
            'The attribute "monographic_authors" returns only person authors. '
            'To retrieve all the monographic authors (person and institution),'
            ' use monographic_authors_group. '
            'To retrieve only the monographic person authors,'
            ' use monographic_person_authors. '
        )
        return list(self._reference_record.monographic_person_authors)

    @property
    def first_author_info(self):
        """
        It retrieves the info of the first author:
        (analytic or monographic), (person or institution), author data,
        of a citation, independent of citation type.
        :returns: (analytic or monographic, person or institution, author data)
        IT REPLACES first_author
        """
        types = [('analytic', 'person'),
                 ('analytic', 'institution'),
                 ('monographic', 'person'),
                 ('monographic', 'institution'),
                 ]
        authors = [self.analytic_person_authors,
                   self.analytic_institution_authors,
                   self.monographic_person_authors,
                   self.monographic_institution_authors,
                   ]
        for a, a_type in zip(authors, types):
            if a is not None:
                return a_type[0], a_type[1], a[0]

    @property
    def first_author(self):
        """
        It retrieves the first person author of the given citation,
        independent of citation type.
        :returns: dict with keys ``given_names`` and ``surname``
        IT WILL BE DEPRECATED. Use first_author_info instead.
        """
        warn_future_deprecation(
            'first_author',
            'first_author_info',
            'The attribute "first_author" returns only a person author. '
            'The attribute "first_author_info" returns info of the '
            'first author independing if it is person or institution. '
        )
        try:
            return self.authors[0]
        except IndexError:
            pass
        try:
            return self.monographic_authors[0]
        except IndexError:
            pass

    @property
    def serie(self):
        """
        This method retrieves the series title. The serie title must be in a book, article or
        conference citation.
        """
        return self._reference_record.coltitle

    @property
    def publisher(self):
        """
        This method retrieves the publisher name, if it exists.
        """
        return self._reference_record.publisher_name

    @property
    def publisher_address(self):
        """
        This method retrieves the publisher address, if it exists.
        """
        items = [
            self._reference_record.publisher_location.get("city"),
            self._reference_record.publisher_location.get("state"),
            self._reference_record.publisher_country,
        ]
        return ", ".join([c for c in items if c])
