import pickle
import json
import os
import gzip

from nltk.corpus.reader.api import CorpusReader
from nltk.corpus.reader.api import CategorizedCorpusReader
from nltk.corpus.reader.twitter import TwitterCorpusReader

from six import string_types

from nltk.tokenize import TweetTokenizer

from nltk.corpus.reader.util import StreamBackedCorpusView, concat, ZipFilePathPointer

# ROOT = r'Twitter-Data/Data/'
# DOC_PATTERN = r'^Manhattan\w+\.json\.gz$'
PKL_PATTERN = r'^Manhattan.*\.json.pickle$'
CAT_PATTERN = r'.*'

#This will read in Twitter data, according to categorical patterns in regex
#DOC_PATTERN, PKL_PATTERN, CAT_PATTERN

class PickledCorpusReader(CategorizedCorpusReader, CorpusReader):

    def __init__(self, root, fileids=PKL_PATTERN, **kwargs):
        # Add the default category pattern if not passed into the class.
        if not any(key.startswith('cat_') for key in kwargs.keys()):
            kwargs['cat_pattern'] = CAT_PATTERN

        CategorizedCorpusReader.__init__(self, kwargs)
        CorpusReader.__init__(self, root, fileids)

    def _resolve(self, fileids, categories):
        #The purpose is to get fileids from parent object
        if fileids is not None and categories is not None:
            raise ValueError("Specify fileids or categories, not both")

        if categories is not None:
            return self.fileids(categories)
        return fileids

    def docs(self, fileids=None, categories=None):
        """
        Calling this function with categories parameters will only return
        docs within a certain category
        """
        # Resolve the fileids and the categories
        fileids = self._resolve(fileids, categories)

        # Create a generator, loading one document into memory at a time.
        for path, enc, fileid in self.abspaths(fileids, True, True):
            with open(path, 'rb') as f:
                yield pickle.load(f)

    def paras(self, fileids=None, categories=None):
        """
        Returns a generator of paragraphs where each paragraph is a list of
        sentences, which is in turn a list of (token, tag) tuples.
        """
        for doc in self.docs(fileids, categories):
            for paragraph in doc:
                yield paragraph

    def sents(self, fileids=None, categories=None):
        """
        Returns a generator of sentences where each sentence is a list of
        (token, tag) tuples.
        """
        for paragraph in self.paras(fileids, categories):
            for sentence in paragraph:
                yield sentence

    def words(self, fileids=None, categories=None):
        """
        Returns a generator of (token, tag) tuples.
        """
        for sentence in self.sents(fileids, categories):
            for token in sentence:
                yield token

if __name__ == '__main__':
    from collections import Counter

    corpus = PickledCorpusReader('../corpus')
    words  = Counter(corpus.words())

    print("{:,} vocabulary {:,} word count".format(len(words.keys()), sum(words.values())))
