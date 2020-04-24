import os
import re
import nltk

from .RedditScore.redditscore.tokenizer import CrazyTokenizer
from sqlalchemy.orm import sessionmaker
from .models import *
import sqlalchemy as db

PATTERNS = [
    ('group1',re.compile(r"(?i)sars-cov|sars-cov-2|sarscov-2|sarscov2|sarscov|sars-cov|covid_19|covidー19|covid-19|covid19|covid19|cov-2|cov2|covid2019|cov2019|cov19|corona-virus|corona virus|covid 19|cov 19|covid|corona"),"coronavirus"),
]

class DatabasePreprocessor(object):

    def __init__(self, database_url, patterns = PATTERNS, dates = None, **kwargs):
        """
        Timezone matters here, therefore, once location is further specified by country
        we can consider all tweets falling in the U.S. as being in CST or even specify
        more particular hours of activity (e.g. 5am - 5am)
        """
        if dates and not isinstance(dates, list):
            raise TypeError("Dates: Please specify a list of dates")
        self.engine = db.create_engine(database_url)
        make_session = sessionmaker(self.engine)
        self.session = make_session()
        self.tokenizer = CrazyTokenizer(extra_patterns = PATTERNS, lowercase = True, normalize = 3, ignore_quotes = False,
                            ignore_stopwords = True, stem = "lemm", remove_punct = True, remove_numbers = True,
                            remove_breaks = True, decontract = True, hashtags = "split", twitter_handles = '', urls = False)

    def getStream(self):
        with self.engine.connect() as conn:
            """
                Requires code for date specification
            """
            stream = conn.execution_options(stream_results=True).execute(
                # Tweet.__table__.selectAll()
                "SELECT * FROM tweet"
            )
            while True:
                chunk = stream.fetchmany(1000)
                if not chunk:
                    break
                yield chunk

    def add_tokens(self, tweet, tokens):
        tw = self.session.query(Tweet).filter_by(id = tweet.id).first()
        tw.tokenized = tokens
        self.session.commit()

    def tokenize(self, tweets):
        for tw in tweets:
            self.add_tokens(tw, self.tokenizer.tokenize(tw.full_text))

    def transform(self):
        for tweets in self.getStream():
            yield self.tokenize(tweets)

    # def add_tokens(self, tweet, tokens):
    #     new_token = TokenizedTweet(
    #         tweet_id = tweet.id,
    #         tokenized = tokens
    #     )
    #     self.session.add(new_token)
    #     self.session.commit()
