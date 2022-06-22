# generated by ModelBuilder
from scielo_classic_website.isisdb.base_journal_record import BaseJournalRecord


# generated by ModelBuilder
class JournalRecord(BaseJournalRecord):

    def __init__(
            self, record, multi_val_tags=None,
            data_dictionary=None):
        super().__init__(
            record, multi_val_tags, data_dictionary)

    @property
    def print_issn(self):
        if not hasattr(self, '_print_issn'):
            self._print_issn = None
            for issn in self.issns:
                if issn['type'] == 'PRINT':
                    self._print_issn = issn["value"]
                    break
        return self._print_issn

    @property
    def electronic_issn(self):
        if not hasattr(self, '_electronic_issn'):
            self._electronic_issn = None
            for issn in self.issns:
                if issn['type'] == 'ONLIN':
                    self._electronic_issn = issn["value"]
                    break
        return self._electronic_issn