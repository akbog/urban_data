from datetime import datetime, date
from sqlalchemy.orm import sessionmaker
from .models import *
import sqlalchemy as db


class DatabaseReader(object):

    def __init__(self, database_url, start_date = None, end_date = None, slices = None, languages = None, locations = None, **kwargs):
        if (start_date and not isinstance(start_date, (datetime, date))) or (end_date and not isinstance(end_date, (datetime, date))):
            raise TypeError("Dates: Please specify start and end date as datetime objects")
        if languages and not isinstance(languages, list):
            raise TypeError("Languages: Please specify a list of languages or None")
        self.start = start_date
        self.end = end_date
        self.slices = slices
        self.engine = db.create_engine(database_url)
        self.languages = languages
        make_session = sessionmaker(self.engine)
        self.session = make_session()

    def getQuery(self):
        if self.start and self.end and self.languages:
            return Tweet.__table__.select().where(Tweet.created.between(self.start, self.end)).where(Tweet.language.in_(self.languages))
        elif self.start and self.end:
            return Tweet.__table__.select().where(Tweet.created.between(self.start, self.end))
        elif self.languages:
            return Tweet.__table__.select().where(Tweet.language.in_(self.languages))
        else:
            return Tweet.__table__.select().order_by(Tweet.created)


    def getStream(self):
        query = self.getQuery()
        with self.engine.connect() as conn:
            stream = conn.execution_options(stream_results=True).execute(query)
            while True:
                chunk = stream.fetchmany(1000)
                if not chunk:
                    break
                yield chunk

    def getFullText(self):
        for tweets in self.getStream():
            for tw in tweets:
                yield tw.full_text

    def getTokenText(self):
        for tweets in self.getStream():
            for tw in tweets:
                yield tw.tokenized

    def getDateRanges(self):
        ranges = []
        diff = (self.end  - self.start) / self.slices
        last = self.start
        for i in range(1, self.slices):
            next = (self.start + diff * i)
            ranges.append((last, next))
            last = next
        ranges.append((last, self.end))
        return ranges

    def time_slices(self):
        ranges = self.getDateRanges()
        time_slices = []
        for start, stop in ranges:
            count = self.session.query(db.func.count(Tweet.id)).filter(Tweet.created.between(start, stop)).first()[0]
            time_slices.append(count)
        return time_slices
