import os
import json
import nltk
import shutil
import pickle
import multiprocessing as mp
import struct
import io
import re
import gzip
from nltk.corpus.reader.api import CorpusReader
from .categorized_reader import CategorizedCorpusReader
from nltk.corpus.reader.twitter import TwitterCorpusReader
from six import string_types, text_type
from nltk.tokenize import wordpunct_tokenize
from nltk.internals import slice_bounds
from nltk.data import PathPointer, FileSystemPathPointer, ZipFilePathPointer, GzipFileSystemPathPointer
from nltk.data import SeekableUnicodeStreamReader
from nltk.util import AbstractLazySequence, LazySubsequence, LazyConcatenation, py25
from tqdm import tqdm
from six import string_types

from nltk.tokenize import TweetTokenizer

from nltk.corpus.reader.util import StreamBackedCorpusView, concat, ZipFilePathPointer

from .NewPickleCorpusView import PickleCorpusView

ROOT = r'Twitter-Data'
DOC_PATTERN = r'[0-2][0-9][0-9][0-9]-[0-3][0-9]-[0-1][0-9]/Manhattan.*\.json\.gz$'
CAT_PATTERN = r'[0-2][0-9][0-9][0-9]-[0-3][0-9]-[0-1][0-9]'
PKL_PATTERN = r'[0-2][0-9][0-9][0-9]-[0-3][0-9]-[0-1][0-9]/Manhattan.*\.pickle$'


class GzipStreamBackedCorpusView(StreamBackedCorpusView):
    def __init__(self, fileid, block_reader = None, startpos = 0, encoding = 'utf8'):
        StreamBackedCorpusView.__init__(self, fileid, block_reader=block_reader, startpos=0, encoding='utf8')
        try:
            if isinstance(self._fileid, GzipFileSystemPathPointer):
                if re.match(r'.*\.gz$',str(self._fileid)):
                    self._eofpos = self.getuncompressedsize(self._fileid)
                else:
                    self._eofpos = self._fileid.file_size()
            else:
                self._eofpos = os.stat(self._fileid).st_size
        except Exception as exc:
            raise ValueError('Unable to open or access %r -- %s' % (fileid, exc))

    def _open(self):
        if isinstance(self._fileid, PathPointer):
            if re.match(r'.*\.gz$',str(self._fileid)):
                self._stream = gzip.open(str(self._fileid), 'rb')
            else:
                self._stream = self._fileid.open(self._encoding)
        elif self._encoding:
            self._stream = SeekableUnicodeStreamReader(
                open(self._fileid, 'rb'), self._encoding
            )
        else:
            self._stream = open(self._fileid, 'rb')

    def getuncompressedsize(self, filename):
        with gzip.GzipFile(filename, 'r') as fin:
            fin.seek(-4,2)
            val = fin.seek(0, io.SEEK_END)
            return val

    def getLength(self):
        return self._len


class NewTwitterCorpusReader(CategorizedCorpusReader, CorpusReader):

    CorpusView = GzipStreamBackedCorpusView

    def __init__(
        self, root, fileids=DOC_PATTERN, word_tokenizer=TweetTokenizer(), encoding='utf8', **kwargs
    ):
        if not any(key.startswith('cat_') for key in kwargs.keys()):
            kwargs['cat_pattern'] = CAT_PATTERN

        CategorizedCorpusReader.__init__(self, kwargs)

        TwitterCorpusReader.__init__(self, root, fileids, encoding)

        if isinstance(root, string_types) and not isinstance(root, PathPointer):
            m = re.match('(.*\.gz)/?(.*\.zip)/?(.*)$|', root) #'(.*\.zip)/?(.*\.gz)/?(.*)$|'
            gzipfile, zipfile, zipentry = m.groups()
            if zipfile:
                root = ZipFilePathPointer(zipfile, zipentry)
            elif gzipfile:
                root = ZipFilePathPointer(gzipfile, zipentry)
            else:
                root = FileSystemPathPointer(root)
        elif not isinstance(root, PathPointer):
            raise TypeError('CorpusReader: expected a string or a PathPointer')

        self._root = root

    def _resolve(self, fileids, categories):
        if fileids is not None and categories is not None:
            raise ValueError("Only Specify fileids OR Categories")

        if categories is not None:
            # print(categories)
            return self.fileids(categories)
        return fileids

    def docs(self, fileids = None, categories = None):
        fileids = self._resolve(fileids, categories)
        return concat(
            [
                self.CorpusView(path, block_reader = self._read_tweets, encoding=enc)
                for (path, enc, fileid) in self.abspaths(fileids, True, True)
            ]
        )

    def abspaths(self, fileids=None, include_encoding=False, include_fileid=False):
        if fileids is None:
            fileids = self._fileids
        elif isinstance(fileids, string_types):
            fileids = [fileids]

        paths = [GzipFileSystemPathPointer(self._root.join(f)) for f in fileids]

        if include_encoding and include_fileid:
            return list(zip(paths, [self.encoding(f) for f in fileids], fileids))
        elif include_fileid:
            return list(zip(paths, fileids))
        elif include_encoding:
            return list(zip(paths, [self.encoding(f) for f in fileids]))
        else:
            return paths

    def full_text_tweets(self, fileids = None, categories = None):
        for tweet in self.docs(fileids, categories):
            #Entire tweet object is available here
            # if tweet['truncated']:
            #     yield tweet['extended_tweet']['full_text']
            # else:
            #     yield tweet['text']
            """
            Here, we can add utility for cleaning the tweets
            of useless data, so as to clear up and better utilize
            size and imports
            """
            yield tweet

    def _read_tweets(self, stream):
        tweets = []
        for i in range(10):
            line = stream.readline()
            if not line:
                return tweets
            tweet = json.loads(line)
            tweets.append(tweet)
        # print("HERE \n")
        # print(tweets[0])
        # print(type(tweets[0]))
        # print("HERE \n")
        return tweets

class NewTwitterPickledCorpusReader(CategorizedCorpusReader, CorpusReader):

    CorpusView = PickleCorpusView

    def __init__(
        self, root, fileids=PKL_PATTERN, word_tokenizer=TweetTokenizer(), encoding='utf8', **kwargs
    ):
        # Add the default category pattern if not passed into the class.
        if not any(key.startswith('cat_') for key in kwargs.keys()):
            kwargs['cat_pattern'] = CAT_PATTERN

        CategorizedCorpusReader.__init__(self, kwargs)
        TwitterCorpusReader.__init__(self, root, fileids, encoding)

    def _resolve(self, fileids, categories):
        if fileids is not None and categories is not None:
            raise ValueError("Only Specify fileids OR Categories")

        if categories is not None:
            # print(categories)
            return self.fileids(categories)
        return fileids

    # def docs(self, fileids=None, categories=None):
    #     fileids = self._resolve(fileids, categories)
    #     # Create a generator, loading one document into memory at a time.
    #     for path, enc, fileid in self.abspaths(fileids, True, True):
    #         with open(path, 'rb') as f:
    #             yield pickle.load(f)

    def docs(self, fileids = None, categories = None):
        fileids = self._resolve(fileids, categories)
        return concat(
            [
                # self.CorpusView(path, block_reader = self._read_tweets, encoding=enc)
                self.CorpusView(path)
                for (path) in self.abspaths(fileids, False, False)
            ]
        )

    def tweets(self, fileids=None, categories=None):
        for bundle in self.docs(fileids, categories):
            for tweet in bundle:
                yield tweet["tokens"]


    def abspaths(self, fileids=None, include_encoding=False, include_fileid=False):
        if fileids is None:
            fileids = self._fileids
        elif isinstance(fileids, string_types):
            fileids = [fileids]

        paths = [FileSystemPathPointer(self._root.join(f)) for f in fileids]

        if include_encoding and include_fileid:
            return list(zip(paths, [self.encoding(f) for f in fileids], fileids))
        elif include_fileid:
            return list(zip(paths, fileids))
        elif include_encoding:
            return list(zip(paths, [self.encoding(f) for f in fileids]))
        else:
            return paths

    def _read_tweets(self, stream):
        tweets = []
        for i in range(10):
            line = stream.readline()
            if not line:
                return tweets
            tweet = json.loads(line)
            tweets.append(tweet)
        return tweets
