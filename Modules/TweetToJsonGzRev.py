from Urban_Research.urban_data.Modules.TwitterReader import NewTwitterCorpusReader
from datetime import datetime
from collections import OrderedDict
from subprocess import check_call
import os
import re
import json
import operator
import timeit
import sys


DOC_PATTERN = r'Tweets/streamed_[0-3][0-9]_[0-1][0-9]_[0-9][0-9][0-9][0-9]_[0-9][0-9]_[0-9][0-9]_[0-9][0-9]\.json\.gz$'
CAT_PATTERN = r'.*Tweets.*'
root = r''

def sort_files(files, reverse_opt):
    regex_str = r'streamed_([0-3][0-9])_([0-1][0-9])_([0-9][0-9][0-9][0-9])_([0-9][0-9])_([0-9][0-9])_([0-9][0-9])\.json\.gz'
    unordered_dict = {}
    for file in files:
        if file == "id_dictionary.pickle":
            continue
        groups = re.match(regex_str, file)
        day, month, year, hour, minute, second = groups.groups()
        file_key = datetime(int(year), int(month), int(day))
        try:
            unordered_dict[file_key].append(file)
        except:
            unordered_dict[file_key] = [file]
    return OrderedDict(sorted(unordered_dict.items(), reverse = reverse_opt, key = operator.itemgetter(0)))

def move_files(sorted_files, corpus, origin, destination):
    for key in sorted_files.keys():
        tic = timeit.default_timer()
        path = os.path.join(destination, "{}_{}_{}".format(key.year, key.month, key.day))
        if not os.path.exists(path):
            os.makedirs(path)
        print("Outputting to: ", path, end = " ")
        for file in sorted_files[key]:
            data = []
            for tweet in corpus.full_text_tweets(fileids = os.path.join(origin, file)):
                data.append(tweet)
            file_out = os.path.join(path, file[:-3])
            with open(file_out, 'w') as outfile:
                json.dump(data, outfile)
            check_call(['gzip', file_out])
        toc = timeit.default_timer()
        print("(", toc - tic, " seconds)")


if __name__ == "__main__":
    raw_files = list(os.listdir("Tweets"))
    sorted_files = sort_files(raw_files, True)
    corpus = NewTwitterCorpusReader(root = root, fileids = DOC_PATTERN, cat_pattern = CAT_PATTERN)
    move_files(sorted_files, corpus, "Tweets", "Tweets_Sorted")
