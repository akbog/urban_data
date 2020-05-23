import os
import nltk
import gensim
import boto
import unicodedata
import re

from nltk.corpus import wordnet as wn
from nltk.stem.wordnet import WordNetLemmatizer
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.pipeline import Pipeline
from gensim.matutils import sparse2full
from gensim.corpora import Dictionary
from gensim.models.tfidfmodel import TfidfModel
from gensim.sklearn_api import lsimodel, ldamodel
from sklearn.model_selection import GridSearchCV
from datetime import datetime, timedelta
from gensim.models.wrappers import LdaMallet



class TextNormalizer(BaseEstimator, TransformerMixin):

    def __init__(self, language='english', dirpath = ".", include_bigram = False, bigram_path = "", stopwords = []):
        self.stopwords  = set(nltk.corpus.stopwords.words(language))
        self.stopwords.update(stopwords)
        self.lemmatizer = WordNetLemmatizer()
        self.include_bigram = include_bigram
        self._bigram_model_path = os.path.join(dirpath, bigram_path)
        self.bigram_mod = None
        self.load_bigram()

    def load_bigram(self):
        if os.path.exists(self._bigram_model_path):
            self.bigram_mod = gensim.models.phrases.Phraser.load(self._bigram_model_path)

    def spell_correct(self, token):
        pass

    def is_url(self, token):
        url_pattern = re.compile(r'https?://\S+|www\.\S+')
        return bool(re.match(url_pattern, token))

    def is_emoji(self, token):
        emoji_pattern = re.compile("["
                               u"\U0001F600-\U0001F64F"u"\U0001F300-\U0001F5FF"u"\U0001F680-\U0001F6FF"u"\U0001F1E0-\U0001F1FF"
                               u"\U00002702-\U000027B0"u"\U000024C2-\U0001F251"u"\U0000F923"u"\U000000A9"u"\U000000AE"
                               u"\U0000203C"u"\U00002049"u"\U000020E3"u"\U00002122"u"\U00002139"u"\U00002194-\U00002199"
                               u"\U000021A9-\U000021AA"u"\U0000231A"u"\U0000231B"u"\U00002328"u"\U000023CF"
                               u"\U000023E9-\U000023F3"u"\U000023F8-\U000023FA"u"\U000025AA"u"\U000025AB"
                               u"\U000025B6"u"\U000025C0"u"\U000025FB-\U000025FE"u"\U00002600-\U000027EF"u"\U00002934"
                               u"\U00002935"u"\U00002B00-\U00002BFF"u"\U00003030"u"\U0000303D"u"\U00003297"
                               u"\U00003299"u"\U0001F000-\U0001F02F"u"\U0001F0A0-\U0001F0FF"u"\U0001F100-\U0001F64F"
                               u"\U0001F100-\U0001F64F"u"\U0001F910-\U0001F96B"u"\U0001F980-\U0001F9E0"
                               "]+", flags=re.UNICODE)
        return bool(re.match(emoji_pattern, token))

    def is_punct(self, token):
        return all(
            unicodedata.category(char).startswith('P') for char in token
        )

    def is_stopword(self, token):
        return token.lower() in self.stopwords

    def normalize(self, document):
        return [
            token
            for token in document
            if not self.is_url(token) and not self.is_emoji(token) and not self.is_punct(token) and not self.is_stopword(token) and not token.isnumeric()
        ]

    def fit(self, X, y=None):
        if self.include_bigram:
            if not self.bigram_mod:
                phrases = gensim.models.Phrases(X, threshold = 0.3, scoring = "npmi")
                self.bigram_mod = gensim.models.phrases.Phraser(phrases)
                self.bigram_mod.save("bigram_model.pkl")
        return self

    def get_bigrams(self, document):
        return self.bigram_mod[document]

    def transform(self, documents):
        if self.include_bigram:
            self.load_bigram()
            return [
                self.get_bigrams(self.normalize(document))
                for document in documents
            ]
        return [
            self.normalize(document)
            for document in documents
        ]

class GensimTfidfVectorizer(BaseEstimator, TransformerMixin):

    def __init__(self, dirpath=".", tofull=False):
        self._lexicon_path = os.path.join(dirpath, "corpus_test.dict")
        self._tfidf_path = os.path.join(dirpath, "tfidf_test.model")
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

class GensimVectorizer(BaseEstimator, TransformerMixin):
    def __init__(self, dirpath="id2word.dict", tofull = False):
        self.path = dirpath
        self.tofull = tofull
        self.id2word = None
        self.load()

    def load(self):
        if os.path.exists(self.path):
            self.id2word = Dictionary.load(self.path)

    def save(self):
        self.id2word.save(self.path)

    def fit(self, documents, labels = None):
        self.id2word = Dictionary(documents)
        self.save()
        return self

    def transform(self, documents):
        def generator():
            for document in documents:
                docvec = self.id2word.doc2bow(document)
                if self.tofull:
                    yield sparse2full(docvec, len(self.id2word))
                else:
                    yield docvec
        return list(generator())

class GensimOneHotVectorizer(BaseEstimator, TransformerMixin):
    def __init__(self, dirpath="id2word.dict", tofull = False):
        self.path = dirpath
        self.tofull = tofull
        self.id2word = None
        self.load()

    def load(self):
        if os.path.exists(self.path):
            self.id2word = Dictionary.load(self.path)

    def save(self):
        self.id2word.save(self.path)

    def fit(self, documents, labels = None):
        if not self.id2word:
            self.id2word = Dictionary(documents)
            self.save()
        return self

    def transform(self, documents):
        def generator():
            for document in documents:
                docvec = [(token[0],1) for token in self.id2word.doc2bow(document)]
                if self.tofull:
                    yield sparse2full(docvec, len(self.id2word))
                else:
                    yield docvec
        return list(generator())

class GensimTopicModels(object):

    def __init__(self, n_topics=100, update_every = 0, passes = 1, alpha = "auto", scorer = "perplexity", include_bigram = False, bigram_path = "", stopwords = []):
        self.n_topics = n_topics
        self.model = Pipeline([
            ('norm', TextNormalizer(include_bigram = include_bigram, bigram_path = bigram_path, stopwords = stopwords)),
            ('vect', GensimOneHotVectorizer()),
            ('model', ldamodel.LdaTransformer(num_topics = self.n_topics, update_every=update_every, passes = passes, alpha = alpha, scorer = scorer))
        ])
        self.search = None

    def fit(self, documents):
        self.model.fit(documents)
        return self.model

    def GridSearchFit(self, documents, param_grid, n_jobs = -1):
        self.search = GridSearchCV(self.model, param_grid = param_grid, n_jobs = n_jobs)
        self.search.fit(documents)
        return self.search

class GensimDynamicTopicModels(object):

    def __init__(self, n_topics=100, update_every = 0, passes = 1, alpha = "auto", scorer = "perplexity", include_bigram = False, bigram_path = "", stopwords = []):
        self.n_topics = n_topics
        self.model = Pipeline([
            ('norm', TextNormalizer(include_bigram = include_bigram, bigram_path = bigram_path, stopwords = stopwords)),
            ('vect', GensimOneHotVectorizer()),
            ('model', ldamodel.LdaTransformer(num_topics = self.n_topics, update_every=update_every, passes = passes, alpha = alpha, scorer = scorer))
        ])
        self.search = None

    def fit(self, documents):
        self.model.fit(documents)
        return self.model

    def GridSearchFit(self, documents, param_grid, n_jobs = -1):
        self.search = GridSearchCV(self.model, param_grid = param_grid, n_jobs = n_jobs)
        self.search.fit(documents)
        return self.search
