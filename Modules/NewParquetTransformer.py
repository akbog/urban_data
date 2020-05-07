import os
import nltk
import gensim
import boto
import unicodedata
import re
# import pkg_resources

from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.pipeline import Pipeline
from gensim.matutils import sparse2full
from gensim.corpora import Dictionary
from gensim.models.tfidfmodel import TfidfModel
from gensim.sklearn_api import lsimodel, ldamodel
from gensim.sklearn_api.ldaseqmodel import LdaSeqTransformer
from datetime import datetime, timedelta
from .models import *
# from symspellpy import SymSpell, Verbosity

DATABASE_URL = "postgres+psycopg2://bogdanowicz:urbandata@localhost:5432/twitter"

class TextNormalizer(BaseEstimator, TransformerMixin):

    def __init__(self, language='english'):
        # self.sym_spell = SymSpell(max_dictionary_edit_distance=2, prefix_length=7)
        # self.dictionary_path = pkg_resources.resource_filename("symspellpy", "frequency_dictionary_en_82_765.txt")
        # self.sym_spell.load_dictionary(dictionary_path, term_index=0, count_index=1)
        pass

    def spell_correct(self, token):
        pass

    def is_url(self, token):
        url_pattern = re.compile(r'https?://\S+|www\.\S+')
        return bool(re.match(url_pattern, token))

    def is_emoji(self, token):
        emoji_pattern = re.compile("["
                               u"\U0001F600-\U0001F64F"  # emoticons
                               u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                               u"\U0001F680-\U0001F6FF"  # transport & map symbols
                               u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                               u"\U00002702-\U000027B0"
                               u"\U000024C2-\U0001F251"
                               "]+", flags=re.UNICODE)
        return bool(re.match(emoji_pattern, token))

    def normalize(self, document):
        return [
            token
            for token in document
            if not self.is_url(token) and not self.is_emoji(token)
        ]

    def fit(self, X, y=None):
        return self

    def transform(self, documents):
        return [
            self.normalize(document)
            for document in documents
        ]

class GensimTfidfVectorizer(BaseEstimator, TransformerMixin):

    def __init__(self, dirpath=".", tofull=False):
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

    def __init__(self, corpus, time_slices, n_topics=50):
        self.documents = corpus
        self.n_topics = n_topics
        self.model = Pipeline([
            ('norm', TextNormalizer()),
            ('vect', GensimTfidfVectorizer()),
            ('model', LdaSeqTransformer(time_slice = time_slices, num_topics = self.n_topics, initialize = "gensim"))
        ])

    def fit(self):
        self.model.fit(self.documents)
        return self.model
