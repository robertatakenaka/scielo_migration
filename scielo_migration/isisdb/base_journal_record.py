# generated by ModelBuilder
from scielo_migration.iid2json.meta_record import MetaRecord


# generated by ModelBuilder
class BaseJournalRecord(MetaRecord):

    def __init__(
            self, record, multi_val_tags=None,
            data_dictionary=None):
        super().__init__(
            record, multi_val_tags, data_dictionary)

    # generated by ModelBuilder
    @property
    def scimago_code(self):
        """
        Scimago Code
        v000
        """
        return self.get_field_content("v000", subfields={}, single=True, simple=True)

    # generated by ModelBuilder
    @property
    def any_issn(self):
        """
        Any Issn
        v000
        """
        return self.get_field_content("v000", subfields={}, single=True, simple=True)

    # generated by ModelBuilder
    @property
    def url(self):
        """
        Url
        v000
        """
        return self.get_field_content("v000", subfields={}, single=True, simple=True)

    # generated by ModelBuilder
    @property
    def fulltitle(self):
        """
        Fulltitle
        v000
        """
        return self.get_field_content("v000", subfields={}, single=True, simple=True)

    # generated by ModelBuilder
    @property
    def cnn_code(self):
        """
        Cnn Code
        v020
        """
        return self.get_field_content("v020", subfields={}, single=True, simple=True)

    # generated by ModelBuilder
    @property
    def secs_code(self):
        """
        Secs Code
        v037
        """
        return self.get_field_content("v037", subfields={}, single=True, simple=True)

    # generated by ModelBuilder
    @property
    def current_status(self):
        """
        Current Status
        v050
        """
        return self.get_field_content("v050", subfields={}, single=True, simple=True)

    # generated by ModelBuilder
    @property
    def status_history(self):
        """
        Status History
        v051 {'a': 'in_date', 'b': 'in_status', 'c': 'out_date', 'd': 'out_status'}
        """
        return self.get_field_content("v051", subfields={'a': 'in_date', 'b': 'in_status', 'c': 'out_date', 'd': 'out_status'}, single=False, simple=False)

    # generated by ModelBuilder
    @property
    def copyrighter(self):
        """
        Copyrighter
        v062
        """
        return self.get_field_content("v062", subfields={}, single=True, simple=True)

    # generated by ModelBuilder
    @property
    def editor_address(self):
        """
        Editor Address
        v063
        """
        return self.get_field_content("v063", subfields={}, single=False, simple=True)

    # generated by ModelBuilder
    @property
    def editor_email(self):
        """
        Editor Email
        v064
        """
        return self.get_field_content("v064", subfields={}, single=True, simple=True)

    # generated by ModelBuilder
    @property
    def acronym(self):
        """
        Acronym
        v068
        """
        return self.get_field_content("v068", subfields={}, single=True, simple=True)

    # generated by ModelBuilder
    @property
    def institutional_url(self):
        """
        Institutional Url
        v069
        """
        return self.get_field_content("v069", subfields={}, single=True, simple=True)

    # generated by ModelBuilder
    @property
    def controlled_vocabulary(self):
        """
        Controlled Vocabulary
        v085
        """
        return self.get_field_content("v085", subfields={}, single=True, simple=True)

    # generated by ModelBuilder
    @property
    def title(self):
        """
        Title
        v100
        """
        return self.get_field_content("v100", subfields={}, single=True, simple=True)

    # generated by ModelBuilder
    @property
    def subtitle(self):
        """
        Subtitle
        v110
        """
        return self.get_field_content("v110", subfields={}, single=True, simple=True)

    # generated by ModelBuilder
    @property
    def editorial_standard(self):
        """
        Editorial Standard
        v117
        """
        return self.get_field_content("v117", subfields={}, single=True, simple=True)

    # generated by ModelBuilder
    @property
    def sponsors(self):
        """
        Sponsors
        v140
        """
        return self.get_field_content("v140", subfields={}, single=False, simple=True)

    # generated by ModelBuilder
    @property
    def abbreviated_title(self):
        """
        Abbreviated Title
        v150
        """
        return self.get_field_content("v150", subfields={}, single=True, simple=True)

    # generated by ModelBuilder
    @property
    def abbreviated_iso_title(self):
        """
        Abbreviated Iso Title
        v151
        """
        return self.get_field_content("v151", subfields={}, single=True, simple=True)

    # generated by ModelBuilder
    @property
    def parallel_titles(self):
        """
        Parallel Titles - official titles in other languages
        v230
        """
        return self.get_field_content("v230", subfields={}, single=False, simple=True)

    # generated by ModelBuilder
    @property
    def other_titles(self):
        """
        Other Titles - alternative titles
        v240
        """
        return self.get_field_content("v240", subfields={}, single=False, simple=True)

    # generated by ModelBuilder
    @property
    def first_year(self):
        """
        First Year
        v301
        """
        return self.get_field_content("v301", subfields={}, single=True, simple=True)

    # generated by ModelBuilder
    @property
    def first_volume(self):
        """
        First Volume
        v302
        """
        return self.get_field_content("v302", subfields={}, single=True, simple=True)

    # generated by ModelBuilder
    @property
    def first_number(self):
        """
        First Number
        v303
        """
        return self.get_field_content("v303", subfields={}, single=True, simple=True)

    # generated by ModelBuilder
    @property
    def last_year(self):
        """
        Last Year
        v304
        """
        return self.get_field_content("v304", subfields={}, single=True, simple=True)

    # generated by ModelBuilder
    @property
    def last_volume(self):
        """
        Last Volume
        v305
        """
        return self.get_field_content("v305", subfields={}, single=True, simple=True)

    # generated by ModelBuilder
    @property
    def last_number(self):
        """
        Last Number
        v306
        """
        return self.get_field_content("v306", subfields={}, single=True, simple=True)

    # generated by ModelBuilder
    @property
    def publisher_country(self):
        """
        Publisher Country
        v310
        """
        return self.get_field_content("v310", subfields={}, single=True, simple=True)

    # generated by ModelBuilder
    @property
    def publisher_state(self):
        """
        Publisher State
        v320
        """
        return self.get_field_content("v320", subfields={}, single=True, simple=True)

    # generated by ModelBuilder
    @property
    def publication_level(self):
        """
        Publication Level
        v330
        """
        return self.get_field_content("v330", subfields={}, single=True, simple=True)

    # generated by ModelBuilder
    @property
    def languages(self):
        """
        Languages
        v350
        """
        return self.get_field_content("v350", subfields={}, single=False, simple=True)

    # generated by ModelBuilder
    @property
    def abstract_languages(self):
        """
        Abstract Languages
        v360
        """
        return self.get_field_content("v360", subfields={}, single=False, simple=True)

    # generated by ModelBuilder
    @property
    def periodicity(self):
        """
        Periodicity
        v380
        """
        return self.get_field_content("v380", subfields={}, single=True, simple=True)

    # generated by ModelBuilder
    @property
    def periodicity_in_months(self):
        """
        Periodicity In Months
        v380
        """
        return self.get_field_content("v380", subfields={}, single=True, simple=True)

    # generated by ModelBuilder
    @property
    def scielo_issn(self):
        """
        Scielo Issn
        v400
        """
        return self.get_field_content("v400", subfields={}, single=True, simple=True)

    # generated by ModelBuilder
    @property
    def title_nlm(self):
        """
        Title Nlm
        v421
        """
        return self.get_field_content("v421", subfields={}, single=True, simple=True)

    # generated by ModelBuilder
    @property
    def _load_issn(self):
        """
         Load Issn
        v435 {'_': 'value', 't': 'type'}
        """
        return self.get_field_content("v435", subfields={'_': 'value', 't': 'type'}, single=False, simple=False)

    # generated by ModelBuilder
    @property
    def subject_descriptors(self):
        """
        Subject Descriptors
        v440
        """
        return self.get_field_content("v440", subfields={}, single=False, simple=True)

    # generated by ModelBuilder
    @property
    def subject_areas(self):
        """
        Subject Areas
        v441
        """
        return self.get_field_content("v441", subfields={}, single=False, simple=True)

    # generated by ModelBuilder
    @property
    def index_coverage(self):
        """
        Index Coverage
        v450
        """
        return self.get_field_content("v450", subfields={}, single=False, simple=True)

    # generated by ModelBuilder
    @property
    def publisher_name(self):
        """
        Publisher Name
        v480
        """
        return self.get_field_content("v480", subfields={}, single=False, simple=True)

    # generated by ModelBuilder
    @property
    def publisher_loc(self):
        """
        Publisher Loc
        v490
        """
        return self.get_field_content("v490", subfields={}, single=True, simple=True)

    # generated by ModelBuilder
    @property
    def publisher_city(self):
        """
        Publisher City
        v490
        """
        return self.get_field_content("v490", subfields={}, single=True, simple=True)

    # generated by ModelBuilder
    @property
    def permissions(self):
        """
        Permissions
        v541
        """
        return self.get_field_content("v541", subfields={}, single=True, simple=True)

    # generated by ModelBuilder
    @property
    def previous_title(self):
        """
        Previous Title
        v610
        """
        return self.get_field_content("v610", subfields={}, single=True, simple=True)

    # generated by ModelBuilder
    @property
    def scielo_domain(self):
        """
        Scielo Domain
        v690
        """
        return self.get_field_content("v690", subfields={}, single=True, simple=True)

    # generated by ModelBuilder
    @property
    def submission_url(self):
        """
        Submission Url
        v692
        """
        return self.get_field_content("v692", subfields={}, single=True, simple=True)

    # generated by ModelBuilder
    @property
    def publishing_model(self):
        """
        Publishing Model
        v699
        """
        return self.get_field_content("v699", subfields={}, single=True, simple=True)

    # generated by ModelBuilder
    @property
    def is_publishing_model_continuous(self):
        """
        Is Publishing Model Continuous
        v699
        """
        return self.get_field_content("v699", subfields={}, single=True, simple=True)

    # generated by ModelBuilder
    @property
    def next_title(self):
        """
        Next Title
        v710
        """
        return self.get_field_content("v710", subfields={}, single=True, simple=True)

    # generated by ModelBuilder
    @property
    def is_indexed_in_scie(self):
        """
        Is Indexed In Scie
        v851
        """
        return self.get_field_content("v851", subfields={}, single=True, simple=True)

    # generated by ModelBuilder
    @property
    def wos_citation_indexes(self):
        """
        Wos Citation Indexes
        v851
        """
        return self.get_field_content("v851", subfields={}, single=False, simple=True)

    # generated by ModelBuilder
    @property
    def is_indexed_in_ssci(self):
        """
        Is Indexed In Ssci
        v852
        """
        return self.get_field_content("v852", subfields={}, single=True, simple=True)

    # generated by ModelBuilder
    @property
    def is_indexed_in_ahci(self):
        """
        Is Indexed In Ahci
        v853
        """
        return self.get_field_content("v853", subfields={}, single=True, simple=True)

    # generated by ModelBuilder
    @property
    def wos_subject_areas(self):
        """
        Wos Subject Areas
        v854
        """
        return self.get_field_content("v854", subfields={}, single=False, simple=True)

    # generated by ModelBuilder
    @property
    def mission(self):
        """
        Mission
        v901 {'_': 'text', 'l': 'language'}
        """
        return self.get_field_content("v901", subfields={'_': 'text', 'l': 'language'}, single=False, simple=False)

    # generated by ModelBuilder
    @property
    def creation_date(self):
        """
        Creation Date
        v940
        """
        return self.get_field_content("v940", subfields={}, single=True, simple=True)

    # generated by ModelBuilder
    @property
    def update_date(self):
        """
        Update Date
        v941
        """
        return self.get_field_content("v941", subfields={}, single=True, simple=True)

    # generated by ModelBuilder
    @property
    def processing_date(self):
        """
        Processing Date
        v941
        """
        return self.get_field_content("v941", subfields={}, single=True, simple=True)

    # generated by ModelBuilder
    @property
    def collection_acronym(self):
        """
        Collection Acronym
        v992
        """
        return self.get_field_content("v992", subfields={}, single=True, simple=True)

