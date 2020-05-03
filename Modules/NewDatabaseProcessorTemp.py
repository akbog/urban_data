import os
import re
import nltk
import gzip
import csv
import logging
from functools import partial
from multiprocessing.pool import Pool
from time import time

from .RedditScore.redditscore.tokenizer import CrazyTokenizer
from sqlalchemy.orm import sessionmaker
from .models import *
from dask import dataframe as dd
from dask.distributed import Client
import dask.bag as bg
import sqlalchemy as db

PATTERNS = [
    ('group1',re.compile(r"(?i)sars-cov|sars-cov-2|sarscov-2|sarscov2|sarscov|sars-cov|covid_19|covidー19|covid-19|covid19|covid19|cov-2|cov2|covid2019|cov2019|cov19|corona-virus|corona virus|covid 19|cov 19|covid|corona"),"coronavirus"),
]

class CSVPreprocessor(object):

    def __init__(self, csv_file, patterns = PATTERNS, dtype = None, **kwargs):
        self.csv_file = csv_file
        self.dtype
        self.tokenizer = CrazyTokenizer(extra_patterns = PATTERNS, lowercase = True, normalize = 3, ignore_quotes = False,
                            ignore_stopwords = True, stem = "lemm", remove_punct = True, remove_numbers = True,
                            remove_breaks = True, decontract = True, hashtags = "split", twitter_handles = '', urls = False)

    def dask_csv(self, csv_file, dtype, names, blocksize):
        dfd = dd.read_csv(csv_file, dtype = dtype, names = names, blocksize = blocksize)

    def partition_csv(self):
        dfd = dd.read_csv(csv_file)

    def tokenize(self, tweets):
        for tw in tweets:
            self.add_tokens(tw, self.tokenizer.tokenize(tw.full_text))

    def transform(self):
        for tweets in self.getStream():
            yield self.tokenize(tweets)

class DatabasePreprocessor(object):

    def __init__(self, database, patterns = PATTERNS, start_date = None, end_date = None, **kwargs):
        """
        Timezone matters here, therefore, once location is further specified by country
        we can consider all tweets falling in the U.S. as being in CST or even specify
        more particular hours of activity (e.g. 5am - 5am)
        """
        if (start_date and not isinstance(start_date, (datetime, date))) or (end_date and not isinstance(end_date, (datetime, date))):
            raise TypeError("Dates: Please specify start and end date as datetime objects")
        self.start = start_date
        self.end = end_date
        self.engine = db.create_engine(database_url)
        make_session = sessionmaker(self.engine)
        self.session = make_session()
        self.tokenizer = CrazyTokenizer(extra_patterns = PATTERNS, lowercase = True, normalize = 3, ignore_quotes = False,
                            ignore_stopwords = True, stem = "lemm", remove_punct = True, remove_numbers = True,
                            remove_breaks = True, decontract = True, hashtags = "split", twitter_handles = '', urls = False)

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
