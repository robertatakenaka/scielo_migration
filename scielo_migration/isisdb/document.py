from scielo_migration.iid2json.meta_record import MetaRecord
from scielo_migration.isisdb.h_record import ArticleRecord


RECORD = dict(
    o=ArticleRecord,
    h=ArticleRecord,
    f=ArticleRecord,
    l=MetaRecord,
    c=ArticleRecord,
)


class Document:
    def __init__(self, _id, records):
        self._id = _id
        self._records = None
        self.records = records

    @property
    def records(self):
        return self._records

    @records.setter
    def records(self, _records):
        self._records = {}
        for _record in _records:
            meta_record = MetaRecord(_record)
            rec_type = meta_record.rec_type
            print(RECORD[rec_type])
            record = RECORD[rec_type](_record)
            self._records[rec_type] = self._records.get(rec_type) or []
            self._records[rec_type].append(record)

    def get_record(self, rec_type):
        return self._records.get(rec_type)

    @property
    def article_meta(self):
        try:
            return self._records.get("f")[0]
        except TypeError:
            return None
