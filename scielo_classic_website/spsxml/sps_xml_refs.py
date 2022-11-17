from io import StringIO
from datetime import datetime

import plumber
from lxml import etree as ET

from . import (
    utils,
    xylose_adapters,
)
from scielo_classic_website.utils.html_code_utils import (
    html_decode,
)


def parse_yyyymmdd(yyyymmdd):
    """
    Get year, month and day from date format which MM and DD can be 00
    """
    year, month, day = None, None, None
    try:
        _year = int(yyyymmdd[:4])
        d = datetime(_year, 1, 1)
        year = _year

        _month = int(yyyymmdd[4:6])
        d = datetime(year, _month, 1)
        month = _month

        _day = int(yyyymmdd[6:])
        d = datetime(year, month, _day)
        day = _day

    except:
        pass

    return year, month, day


def iso_8601_date(yyyymmdd):
    parsed_yyyymmdd = parse_yyyymmdd(yyyymmdd)
    return "-".join([item for item in list(parsed_yyyymmdd) if item])


class XMLArticleMetaCitationsPipe(plumber.Pipe):

    def precond(data):
        raw, xml = data
        if not list(raw.citations):
            raise plumber.UnmetPrecondition()

    @plumber.precondition(precond)
    def transform(self, data):
        raw, xml = data

        article = xml.find('.')
        article.append(ET.Element('back'))

        back = article.find('back')
        back.append(ET.Element('ref-list'))

        reflist = xml.find('./back/ref-list')

        cit = XMLCitation()
        for citation in raw.citations:
            # citation (scielo_classic_website.models.reference.Reference)
            reflist.append(
                cit.deploy(
                    xylose_adapters.ReferenceXyloseAdapter(
                        citation, html_decode))[1])

        return data


class XMLCitation(object):

    def __init__(self):
        self._ppl = plumber.Pipeline(self.SetupCitationPipe(),
                                     self.RefIdPipe(),
                                     self.MixedCitationPipe(),
                                     self.ElementCitationPipe(),
                                     self.PersonGroupPipe(),
                                     self.CollabPipe(),

                                     self.ArticleTitlePipe(),
                                     self.ChapterTitlePipe(),
                                     self.DataTitlePipe(),

                                     self.SourcePipe(),

                                     self.ConferencePipe(),
                                     # self.ThesisPipe(),
                                     self.PatentPipe(),

                                     # self.VolumePipe(),
                                     self.IssuePipe(),
                                     # self.SupplementPipe(),
                                     self.IssuePartPipe(),
                                     self.IssueTitlePipe(),

                                     self.ElocationIdPipe(),
                                     self.PageRangePipe(),
                                     # self.SizePipe(),
                                     self.StartPagePipe(),
                                     self.EndPagePipe(),
                                     self.IssnPipe(),
                                     # self.PubIdPipe(),

                                     self.DatePipe(),
                                     # self.PublisherNamePipe(),
                                     # self.PublisherLocPipe(),

                                     self.EditionPipe(),
                                     self.IsbnPipe(),

                                     # self.VersionPipe(),

                                     # self.SeriesPipe(),
                                     self.DateInCitatioPipe(),
                                     self.LinkPipe(),

                                     # self.CommentPipe(),
                                     )

    # gov
    # institution
    # institution-wrap
    # issn-l
    # object-id
    # part-title

    # patent
    # person-group
    # pub-id
    # publisher-loc
    # publisher-name
    # role
    # season
    # series
    # size
    # source
    # std
    # string-date
    # string-name
    # supplement
    # trans-source
    # trans-title
    # uri
    # version
    # volume
    # volume-id
    # volume-series
    # year
    class SetupCitationPipe(plumber.Pipe):

        def transform(self, data):
            xml = ET.Element('ref')
            return data, xml

    class RefIdPipe(plumber.Pipe):
        def transform(self, data):
            raw, xml = data

            ref = xml.find('.')

            ref.set('id', 'B{0}'.format(str(raw.index_number)))

            return data

    class MixedCitationPipe(plumber.Pipe):
        def precond(data):
            raw, xml = data

            if not raw.mixed_citation:
                raise plumber.UnmetPrecondition()

        @plumber.precondition(precond)
        def transform(self, data):
            raw, xml = data

            parser = ET.HTMLParser()

            mc = ET.parse(StringIO(raw.mixed_citation), parser)
            mixed_citation = mc.find('body/p/.')
            if mixed_citation is None:
                mixed_citation = mc.find('body/.')
            mixed_citation.tag = 'mixed-citation'

            xml.append(utils.convert_all_html_tags_to_jats(mixed_citation))

            return data

    class ElementCitationPipe(plumber.Pipe):
        def transform(self, data):
            raw, xml = data

            elementcitation = ET.Element('element-citation')
            elementcitation.set(
                'publication-type', raw.publication_type or 'other')

            xml.find('.').append(elementcitation)

            return data

    class ArticleTitlePipe(plumber.Pipe):
        def precond(data):
            raw, xml = data

            if not raw.article_title:
                raise plumber.UnmetPrecondition()

        @plumber.precondition(precond)
        def transform(self, data):
            raw, xml = data

            articletitle = ET.Element('article-title')

            articletitle.text = raw.article_title

            xml.find('./element-citation').append(articletitle)

            return data

    class ChapterTitlePipe(plumber.Pipe):
        def precond(data):
            raw, xml = data

            if not raw.chapter_title:
                raise plumber.UnmetPrecondition()

        @plumber.precondition(precond)
        def transform(self, data):
            raw, xml = data

            articletitle = ET.Element('chapter-title')

            articletitle.text = raw.chapter_title

            xml.find('./element-citation').append(articletitle)

            return data

    class DataTitlePipe(plumber.Pipe):
        """
        https://jats.nlm.nih.gov/publishing/tag-library/1.3/element/data-title.html
        """
        def precond(data):
            raw, xml = data

            if not raw.data_title:
                raise plumber.UnmetPrecondition()

        @plumber.precondition(precond)
        def transform(self, data):
            raw, xml = data

            articletitle = ET.Element('data-title')

            articletitle.text = raw.data_title

            xml.find('./element-citation').append(articletitle)

            return data

    class SourcePipe(plumber.Pipe):
        def precond(data):
            raw, xml = data

            if not raw.source:
                raise plumber.UnmetPrecondition()

        @plumber.precondition(precond)
        def transform(self, data):
            raw, xml = data

            source = ET.Element('source')

            source.text = raw.source

            xml.find('./element-citation').append(source)

            return data

    class CommentPipe(plumber.Pipe):
        def precond(data):
            raw, xml = data

            if not raw.comment and not raw.link:
                raise plumber.UnmetPrecondition()

        @plumber.precondition(precond)
        def transform(self, data):
            raw, xml = data

            comment = ET.Element('comment')

            comment.text = raw.comment

            if raw.link:
                comment.text = 'Available at:'
                link = ET.Element('ext-link')
                link.set('ext-link-type', 'uri')
                link.set('{http://www.w3.org/1999/xlink}href', 'http://%s' % raw.link)
                link.text = 'link'
                comment.append(link)

            xml.find('./element-citation').append(comment)

            return data

    class DatePipe(plumber.Pipe):
        def precond(data):
            raw, xml = data

            if not raw.publication_date:
                raise plumber.UnmetPrecondition()

        @plumber.precondition(precond)
        def transform(self, data):
            raw, xml = data

            pdate = ET.Element("date")

            date = {
                "year": raw.publication_date[0:4],
                "month": raw.publication_date[5:7],
                "day": raw.publication_date[8:10],
            }

            for name, value in date.items():
                if value and value.isdigit() and int(value) > 0:
                    date_element = ET.Element(name)
                    date_element.text = value
                    pdate.append(date_element)

            xml.find("./element-citation").append(pdate)

            return data

    class StartPagePipe(plumber.Pipe):
        def precond(data):
            raw, xml = data

            if not raw.start_page:
                raise plumber.UnmetPrecondition()

        @plumber.precondition(precond)
        def transform(self, data):
            raw, xml = data

            fpage = ET.Element('fpage')
            fpage.text = raw.start_page
            xml.find('./element-citation').append(fpage)

            return data

    class EndPagePipe(plumber.Pipe):
        def precond(data):
            raw, xml = data

            if not raw.end_page:
                raise plumber.UnmetPrecondition()

        @plumber.precondition(precond)
        def transform(self, data):
            raw, xml = data

            lpage = ET.Element('lpage')
            lpage.text = raw.end_page
            xml.find('./element-citation').append(lpage)

            return data

    class PageRangePipe(plumber.Pipe):
        def precond(data):
            raw, xml = data

            if not raw.pages_range:
                raise plumber.UnmetPrecondition()

        @plumber.precondition(precond)
        def transform(self, data):
            raw, xml = data

            elem = ET.Element('page-range')
            elem.text = raw.pages_range
            xml.find('./element-citation').append(elem)

            return data

    class IssuePipe(plumber.Pipe):
        def precond(data):
            raw, xml = data

            if not raw.issue:
                raise plumber.UnmetPrecondition()

        @plumber.precondition(precond)
        def transform(self, data):
            raw, xml = data

            issue = ET.Element('issue')
            issue.text = raw.issue
            xml.find('./element-citation').append(issue)

            return data

    class IssuePartPipe(plumber.Pipe):
        def precond(data):
            raw, xml = data

            if not raw.issue_part:
                raise plumber.UnmetPrecondition()

        @plumber.precondition(precond)
        def transform(self, data):
            raw, xml = data

            issue_part = ET.Element('issue-part')
            issue_part.text = raw.issue_part
            xml.find('./element-citation').append(issue_part)

            return data

    class IssueTitlePipe(plumber.Pipe):
        def precond(data):
            raw, xml = data

            if not raw.issue_title:
                raise plumber.UnmetPrecondition()

        @plumber.precondition(precond)
        def transform(self, data):
            raw, xml = data

            issue_title = ET.Element('issue-title')
            issue_title.text = raw.issue_title
            xml.find('./element-citation').append(issue_title)

            return data

    class SupplementPipe(plumber.Pipe):
        def precond(data):
            raw, xml = data

            if not raw.supplement:
                raise plumber.UnmetPrecondition()

        @plumber.precondition(precond)
        def transform(self, data):
            raw, xml = data

            supplement = ET.Element('supplement')
            supplement.text = raw.supplement
            xml.find('./element-citation').append(supplement)

            return data

    class VolumePipe(plumber.Pipe):
        def precond(data):
            raw, xml = data

            if not raw.volume:
                raise plumber.UnmetPrecondition()

        @plumber.precondition(precond)
        def transform(self, data):
            raw, xml = data

            volume = ET.Element('volume')
            volume.text = raw.volume
            xml.find('./element-citation').append(volume)

            return data

    class EditionPipe(plumber.Pipe):
        def precond(data):
            raw, xml = data

            if not raw.edition:
                raise plumber.UnmetPrecondition()

        @plumber.precondition(precond)
        def transform(self, data):
            raw, xml = data

            edition = ET.Element('edition')
            edition.text = raw.edition
            xml.find('./element-citation').append(edition)

            return data

    class ElocationIdPipe(plumber.Pipe):
        def precond(data):
            raw, xml = data

            if not raw.elocation:
                raise plumber.UnmetPrecondition()

        @plumber.precondition(precond)
        def transform(self, data):
            raw, xml = data

            elocation = ET.Element('elocation-id')
            elocation.text = raw.elocation
            xml.find('./element-citation').append(elocation)

            return data

    class VersionPipe(plumber.Pipe):
        def precond(data):
            raw, xml = data

            if not raw.version:
                raise plumber.UnmetPrecondition()

        @plumber.precondition(precond)
        def transform(self, data):
            raw, xml = data

            version = ET.Element('version')
            version.text = raw.version
            xml.find('./element-citation').append(version)

            return data

    class IsbnPipe(plumber.Pipe):
        def precond(data):
            raw, xml = data

            if not raw.isbn:
                raise plumber.UnmetPrecondition()

        @plumber.precondition(precond)
        def transform(self, data):
            raw, xml = data

            isbn = ET.Element('isbn')
            isbn.text = raw.isbn
            xml.find('./element-citation').append(isbn)

            return data

    class IssnPipe(plumber.Pipe):
        def precond(data):
            raw, xml = data

            if not raw.issn:
                raise plumber.UnmetPrecondition()

        @plumber.precondition(precond)
        def transform(self, data):
            raw, xml = data

            issn = ET.Element('issn')
            issn.text = raw.issn
            xml.find('./element-citation').append(issn)

            return data

    class PatentPipe(plumber.Pipe):
        """
        <patent country="US">United States patent US 6,980,855</patent>
        """
        def precond(data):
            raw, xml = data

            if not raw.patent:
                raise plumber.UnmetPrecondition()

        @plumber.precondition(precond)
        def transform(self, data):
            raw, xml = data

            patent = ET.Element('patent')
            patent.set("country", raw.patent_country)
            patent.text = raw.patent
            xml.find('./element-citation').append(patent)

            return data

    class PersonGroupPipe(plumber.Pipe):
        def precond(data):
            raw, xml = data

            if (not list(raw.analytic_person_authors) and
                    not list(raw.monographic_person_authors)):
                raise plumber.UnmetPrecondition()

        @plumber.precondition(precond)
        def transform(self, data):
            raw, xml = data

            persongroup = ET.Element('person-group')
            persongroup.set('person-group-type', 'author')
            for author in raw.analytic_person_authors:
                name = ET.Element('name')
                items = (
                    ("surname", author.get("surname")),
                    ("given-names", author.get("given_names")),
                )
                for key, value in items:
                    if value:
                        elem = ET.Element(key)
                        elem.text = value
                        name.append(elem)
                persongroup.append(name)
            if raw.etal:
                elem = ET.Element("etal")
                elem.text = raw.etal
                persongroup.append(elem)

            if persongroup.find("name") is not None:
                # add persongroup
                xml.find('./element-citation').append(persongroup)

                # cria novo persongroup
                persongroup = ET.Element('person-group')

            for author in raw.monographic_person_authors:
                name = ET.Element('name')

                items = (
                    ("surname", author.get("surname")),
                    ("given-names", author.get("given_names")),
                )
                for key, value in items:
                    if value:
                        elem = ET.Element(key)
                        elem.text = value
                        name.append(elem)
                persongroup.append(name)

            if persongroup.find("name") is not None:
                # add persongroup
                persongroup.set(
                    'person-group-type',
                    author.get("role") or 'editor')
                xml.find('./element-citation').append(persongroup)

            return data

    class CollabPipe(plumber.Pipe):

        def transform(self, data):
            raw, xml = data

            for author in raw.analytic_institution_authors:
                collab = ET.Element('collab')
                collab.set('collab-type', 'author')
                collab.text = author
                xml.find('./element-citation').append(collab)

            for author in raw.monographic_institution_authors:
                collab = ET.Element('collab')
                collab.set('collab-type', 'author')
                collab.text = author
                xml.find('./element-citation').append(collab)

            return data

    class ConferencePipe(plumber.Pipe):

        def precond(data):
            raw, xml = data

            if raw.publication_type != 'confproc':
                raise plumber.UnmetPrecondition()

        @plumber.precondition(precond)
        def transform(self, data):
            raw, xml = data

            elementcitation = xml.find('./element-citation')

            if raw.conference_name:
                elem = ET.Element('conf-name')
                elem.text = raw.conference_name
                elementcitation.append(elem)

            if raw.conference_date_iso:
                elem = ET.Element('conf-date')
                elem.set('iso-8601-date', iso_8601_date(raw.conference_date_iso))
                elem.text = raw.conference_date or ''
                elementcitation.append(elem)

            conf_loc = ET.Element('conf-loc')
            if raw.conference_location:
                for name in ('city', 'state'):
                    data = raw.conference_location.get(name)
                    if data:
                        elem = ET.Element(name)
                        elem.text = data
                        conf_loc.append(elem)

            if raw.conference_country:
                elem = ET.Element('country')
                elem.text = raw.conference_country
                conf_loc.append(elem)
            if conf_loc.find("*") is not None:
                elementcitation.append(conf_loc)

            if raw.conference_sponsor:
                elem = ET.Element('conf-sponsor')
                elem.text = raw.conference_sponsor
                elementcitation.append(elem)

            return data

    class ThesisPipe(plumber.Pipe):

        def precond(data):
            raw, xml = data

            if raw.publication_type != 'thesis':
                raise plumber.UnmetPrecondition()

        @plumber.precondition(precond)
        def transform(self, data):
            raw, xml = data

            elementcitation = xml.find('./element-citation')

            if raw.thesis_institution:
                elem = ET.Element('publisher-name')
                elem.text = raw.thesis_institution
                elementcitation.append(elem)

            publisher_loc = ET.Element('publisher-loc')
            if raw.thesis_location:
                for name in ('city', 'state'):
                    data = raw.thesis_location.get(name)
                    if data:
                        elem = ET.Element(name)
                        elem.text = data
                        publisher_loc.append(elem)

            if raw.thesis_country:
                elem = ET.Element('country')
                elem.text = raw.thesis_country
                publisher_loc.append(elem)

            if publisher_loc.find("*") is not None:
                elementcitation.append(publisher_loc)

            if raw.thesis_degree:
                elem = ET.Element("comment")
                elem.set("content-type", "degree")
                elem.text = raw.thesis_degree
                elementcitation.append(elem)
            return data

    class LinkPipe(plumber.Pipe):

        def precond(data):
            raw, xml = data

            if not raw.ext_link:
                raise plumber.UnmetPrecondition()

        @plumber.precondition(precond)
        def transform(self, data):
            raw, xml = data

            elementcitation = xml.find('./element-citation')

            if raw.link:
                link = ET.Element('ext-link')
                link.set('ext-link-type', 'uri')
                link.set('{http://www.w3.org/1999/xlink}href', 'http://%s' % raw.link)
                link.text = raw.link
                elementcitation.append(link)
            return data

    class DateInCitatioPipe(plumber.Pipe):
        """
        A <date-in-citation> element SHOULD NOT be used to record the 
        publication date; instead use the specific date elements such as 
        <year> and <month> or the combination publishing date element <date>.
        The <date-in-citation> element SHOULD BE used to record
        non-publication dates such as ACCESS DATES, copyright dates, 
        patent application dates, or time stamps indicating the exact
        time the work was published for a continuously or frequently updated source.
        """

        def precond(data):
            raw, xml = data

            if not raw.access_date and not raw.access_date_iso:
                raise plumber.UnmetPrecondition()

            if not raw.patent_application_date and not raw.patent_application_date_iso:
                raise plumber.UnmetPrecondition()

        @plumber.precondition(precond)
        def transform(self, data):
            raw, xml = data

            elementcitation = xml.find('./element-citation')

            content_type = (
                ((raw.access_date or raw.access_date_iso) and 'access-date') or
                ((raw.patent_application_date or raw.patent_application_date_iso) and 'patent-application-date')
            )
            elem = ET.Element("date-in-citation")
            elem.set("content-type", content_type)
            elem.set(
                "iso-8601-date",
                iso_8601_date(
                    raw.access_date_iso or raw.patent_application_date_iso)
            )
            elem.text = raw.access_date or raw.patent_application_date
            elementcitation.append(elem)
            return data

    def deploy(self, raw):

        transformed_data = self._ppl.run(raw, rewrap=True)

        return next(transformed_data)
