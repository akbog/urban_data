import os
import nltk
import shutil
import pickle
import multiprocessing as mp

from tqdm import tqdm
from .java_tweet_tokenizer import *

ROOT = r'Twitter-Data'
DOC_PATTERN = r'Manhattan.*\.json\.gz$'
CAT_PATTERN = r'[0-2][0-9][0-9][0-9].*'


class Preprocessor(object):
    def __init__(self, corpus, target=None, **kwargs):
        self.corpus = corpus
        self.target = target

    @property
    def target(self):
        return self._target

    @target.setter
    def target(self, path):
        if path is not None:
            # Normalize the path and make it absolute
            path = os.path.expanduser(path)
            path = os.path.expandvars(path)
            path = os.path.abspath(path)

            if os.path.exists(path):
                if not os.path.isdir(path):
                    raise ValueError(
                        "Please supply a directory to write preprocessed data to."
                    )

        self._target = path

    def fileids(self, fileids=None, categories=None):
        fileids = self.corpus._resolve(fileids, categories)
        if fileids:
            return fileids
        return self.corpus.fileids()

    def abspath(self, fileid):
        # Find the directory, relative from the corpus root.
        parent = os.path.relpath(
            os.path.dirname(self.corpus.abspath(fileid)), self.corpus.root
        )

        # Compute the name parts to reconstruct
        basename  = os.path.basename(fileid)
        name, ext = os.path.splitext(basename)

        # Create the pickle file extension
        basename  = name[0:-5] + '.pickle'

        # Return the path to the file relative to the target.
        return os.path.normpath(os.path.join(self.target, parent, basename))

    def replicate(self, source):
        names = [
            name for name in os.listdir(source)
            if not name.startswith('.')
        ]

        # Filter out directories and copy files
        for name in names:
            src = os.path.abspath(os.path.join(source, name))
            dst = os.path.abspath(os.path.join(self.target, name))

            if os.path.isfile(src):
                shutil.copy(src, dst)

    def tokenize(self, fileid):
        for tweet in self.corpus.full_text_tweets(fileids=fileid):
            # yield runtagger_parse([tweet])
            if tweet['truncated']:
                tweet['tokens'] = nltk.pos_tag(nltk.wordpunct_tokenize(tweet['extended_tweet']['full_text']))
                yield tweet
            else:
                tweet['tokens'] = nltk.pos_tag(nltk.wordpunct_tokenize(tweet['text']))
                yield tweet
            # yield nltk.pos_tag(nltk.wordpunct_tokenize(tweet))

    def process(self, fileid):
        # Compute the outpath to write the file to.
        target = self.abspath(fileid)
        parent = os.path.dirname(target)

        # Make sure the directory exists
        if not os.path.exists(parent):
            os.makedirs(parent)

        # Make sure that the parent is a directory and not a file
        if not os.path.isdir(parent):
            raise ValueError(
                "Please supply a directory to write preprocessed data to."
            )


        # Create a data structure for the pickle
        document = list(self.tokenize(fileid))

        # Open and serialize the pickle to disk
        with open(target, 'wb') as f:
            pickle.dump(document, f, pickle.HIGHEST_PROTOCOL)

        # Clean up the document
        del document

        # Return the target fileid
        return target

    def transform(self, fileids=None, categories=None):
        # Make the target directory if it doesn't already exist
        if not os.path.exists(self.target):
            os.makedirs(self.target)

        # First shutil.copy anything in the root directory.
        self.replicate(self.corpus.root)

        # Resolve the fileids to start processing
        for fileid in self.fileids(fileids, categories):
            print("Preprocessing: ", fileid)
            yield self.process(fileid)
