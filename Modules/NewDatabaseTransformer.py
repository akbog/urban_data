import os
import nltk
import gensim
import boto
import unicodedata

from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.pipeline import Pipeline
from gensim.matutils import sparse2full
from gensim.corpora import Dictionary
from gensim.models.tfidfmodel import TfidfModel
from gensim.sklearn_api import lsimodel, ldamodel
from gensim.sklearn_api.ldaseqmodel import LdaSeqTransformer
from datetime import datetime, timedelta

from sqlalchemy.orm import sessionmaker
from .models import *
import sqlalchemy as db

DATABASE_URL = "postgres+psycopg2://bogdanowicz:urbandata@localhost:5432/twitter"

class GensimTfidfVectorizer(BaseEstimator, TransformerMixin):

    def __init__(self, dirpath=".", tofull=False):
        """
        Pass in a directory that holds the lexicon in corpus.dict and the
        TFIDF model in tfidf.model (for now).
        Set tofull = True if the next thing is a Scikit-Learn estimator
        otherwise keep False if the next thing is a Gensim model.
        """
        self._lexicon_path = os.path.join(dirpath, "corpus.dict")
        self._tfidf_path = os.path.join(dirpath, "tfidf.model")

        self.lexicon = None
        self.tfidf = None
        self.tofull = tofull

        self.load()

    def load(self):

        if os.path.exists(self._lexicon_path):
            self.lexicon = Dictionary.load(self._lexicon_path)

        if os.path.exists(self._tfidf_path):
            self.tfidf = TfidfModel().load(self._tfidf_path)

    def save(self):
        self.lexicon.save(self._lexicon_path)
        self.tfidf.save(self._tfidf_path)

    def fit(self, documents, labels=None):
        self.lexicon = Dictionary(documents)
        self.tfidf = TfidfModel([self.lexicon.doc2bow(doc) for doc in documents], id2word=self.lexicon)
        self.save()
        return self

    def transform(self, documents):
        def generator():
            for document in documents:
                vec = self.tfidf[self.lexicon.doc2bow(document)]
                if self.tofull:
                    yield sparse2full(vec)
                else:
                    yield vec
        return list(generator())

class GensimTopicModels(object):

    def __init__(self, corpus, n_topics=50):
        self.corpus = corpus
        self.n_topics = n_topics
        self.model = Pipeline([
            ('vect', GensimTfidfVectorizer()),
            ('model', LdaSeqTransformer(time_slice = self.corpus.time_slices(), num_topics = self.n_topics))
        ])

    def fit(self):
        documents = [tweet for tweet in self.corpus.getTokenText()]
        self.model.fit(documents)
        return self.model
