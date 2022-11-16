from io import StringIO

import plumber
from lxml import etree as ET

from . import (
    utils,
    xylose_adapters,
)
from scielo_classic_website.utils.html_code_utils import (
    html_decode,
)


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
                                     self.ArticleTitlePipe(),
                                     self.ThesisTitlePipe(),
                                     self.LinkTitlePipe(),
                                     self.SourcePipe(),
                                     self.DatePipe(),
                                     self.StartPagePipe(),
                                     self.EndPagePipe(),
                                     self.IssuePipe(),
                                     self.VolumePipe(),
                                     self.PersonGroupPipe(),
                                     self.CommentPipe())

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

            translate_ptype = {
                'article': 'journal',
                'link': 'webpage',
                'conference': 'confproc',
                'undefined': 'other',
            }

            elementcitation = ET.Element('element-citation')
            elementcitation.set(
                'publication-type',
                translate_ptype.get(raw.publication_type, raw.publication_type)
            )

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

    class ThesisTitlePipe(plumber.Pipe):
        def precond(data):
            raw, xml = data

            if not raw.thesis_title:
                raise plumber.UnmetPrecondition()

        @plumber.precondition(precond)
        def transform(self, data):
            raw, xml = data

            source = ET.Element('source')

            source.text = raw.thesis_title

            xml.find('./element-citation').append(source)

            return data

    class LinkTitlePipe(plumber.Pipe):
        def precond(data):
            raw, xml = data

            if not raw.link_title:
                raise plumber.UnmetPrecondition()

        @plumber.precondition(precond)
        def transform(self, data):
            raw, xml = data

            source = ET.Element('source')

            source.text = raw.link_title

            xml.find('./element-citation').append(source)

            return data

    class CommentPipe(plumber.Pipe):
        def precond(data):
            raw, xml = data

            if not raw.comment:
                raise plumber.UnmetPrecondition()

        @plumber.precondition(precond)
        def transform(self, data):
            raw, xml = data

            comment = ET.Element('comment')

            comment.text = XLINK_REGEX.sub('xlink:href', raw.comment)

            if raw.publication_type == 'link' and raw.link:
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
                if len(value) > 0 and value.isdigit() and int(value) > 0:
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

    class PersonGroupPipe(plumber.Pipe):
        def precond(data):
            raw, xml = data

            if not raw.authors:
                raise plumber.UnmetPrecondition()

        @plumber.precondition(precond)
        def transform(self, data):
            raw, xml = data

            persongroup = ET.Element('person-group')
            persongroup.set('person-group-type', 'author')
            if raw.authors:
                for author in raw.authors:
                    name = ET.Element('name')

                    if "surname" in author:
                        surname = ET.Element('surname')
                        surname.text = author['surname']
                        name.append(surname)

                    if "given_names" in author:
                        givennames = ET.Element('given-names')
                        givennames.text = author['given_names']
                        name.append(givennames)
                    persongroup.append(name)

            xml.find('./element-citation').append(persongroup)

            return data

    def deploy(self, raw):

        transformed_data = self._ppl.run(raw, rewrap=True)

        return next(transformed_data)
