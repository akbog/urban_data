#So, I think I should build the database, without location built in
#Then, cycle through and build the database with locations
from TwitterReader import NewTwitterCorpusReader
from TwitterDatabase import ParallelTwitterDatabase
from TwitterDatabaseUpdate import TwitterDatabase
from TwitterDatabaseMemory import MemTwitterDatabase
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from models import *
import pandas as pd
import numpy as np
from datetime import datetime
from collections import OrderedDict
import operator
import pickle
import os
import sys
import re

def sort_files(files, reverse_opt, even, odd):
    regex_str = r'Tweets\/streamed_([0-3][0-9])_([0-1][0-9])_([0-9][0-9][0-9][0-9])_([0-9][0-9])_([0-9][0-9])_([0-9][0-9])\.json\.gz'
    unordered_dict = {}
    for file in files:
        groups = re.match(regex_str, file)
        day, month, year, hour, minute, second = groups.groups()
        file_key = datetime(int(year), int(month), int(day), int(hour), int(minute), int(second))
        if even:
            if int(day) % 2 == 0:
                unordered_dict[file_key] = file
        elif odd:
            if not int(day) % 2 == 0:
                unordered_dict[file_key] = file
        else:
            unordered_dict[file_key] = file
    return OrderedDict(sorted(unordered_dict.items(), reverse = reverse_opt, key = operator.itemgetter(0)))

def re_sort(file_url, odd, even, file_out):
    with open(file_url, "rb") as read:
        ordered_dict = pickle.load(read)
    with open(file_url, "rb") as read:
        new_dict = pickle.load(read)
    if even:
        for key, value in ordered_dict.items():
            if not key.day % 2 == 0:
                del new_dict[key]
    elif odd:
        for key, value in ordered_dict.items():
            if key.day % 2 == 0:
                del new_dict[key]
    with open(file_out, "wb") as write:
        pickle.dump(new_dict, write)

if __name__ == "__main__":
    DOC_PATTERN = r'Tweets/streamed_[0-3][0-9]_[0-1][0-9]_[0-9][0-9][0-9][0-9]_[0-9][0-9]_[0-9][0-9]_[0-9][0-9]\.json\.gz$'
    CAT_PATTERN = r'.*Tweets.*'
    FOLDER_PATTERN = r'Tweets'
    root = r'../../Data'
    database_url = os.environ["DB_URL"]
    engine = create_engine(database_url)
    reverse = False
    if len(sys.argv) < 2:
        print("Please Specify File URL for import")
        sys.exit(1)
    if sys.argv[2] == "clean":
        if os.environ["DB_CLEAN_CONFIRM"] == "confirm":
            Base.metadata.drop_all(engine)
            Base.metadata.create_all(engine)
        rebuild = True
    elif sys.argv[2] == "append":
        rebuild = False
    if sys.argv[3] == "reverse":
        reverse = True
    elif sys.argv[3] == "forward":
        reverse = False
    else:
        print("Second Arg Reserved for: clean or append")
        sys.exit(1)
    odd = False
    even = False
    if sys.argv[4] == "odd":
        odd = True
    elif sys.argv[4] == "even":
        even = True

    if reverse:
        file_url = 'rev_tweet_dict'
    else:
        file_url = 'tweet_dict'
    if even:
        file_url = file_url + '_even.pkl'
    elif odd:
        file_url = file_url + '_odd.pkl'
    else:
        file_url = file_url + '.pkl'

    # if rebuild:
    #     if not reverse:
    #         file_path = sys.argv[1]
    #         files = [os.path.join(FOLDER_PATTERN, f) for f in os.listdir(file_path) if re.match(DOC_PATTERN, str(os.path.join(FOLDER_PATTERN,f)))]
    #         files = sort_files(files, False)
    #         with open(file_url, "wb") as write:
    #             pickle.dump(files, write)
    #     else:
    #         file_path = sys.argv[1]
    #         files = [os.path.join(FOLDER_PATTERN, f) for f in os.listdir(file_path) if re.match(DOC_PATTERN, str(os.path.join(FOLDER_PATTERN,f)))]
    #         files = sort_files(files, True)
    #         with open(file_url, "wb") as write:
    #             pickle.dump(files, write)
    if not os.path.isfile(file_url):
        if reverse:
            old_file_url = 'rev_tweet_dict.pkl'
        else:
            old_file_url = 'tweet_dict.pkl'
        re_sort(old_file_url, odd, even, file_url)
    corpus = NewTwitterCorpusReader(root = root, fileids = DOC_PATTERN, cat_pattern = CAT_PATTERN)
    database = ParallelTwitterDatabase(corpus, database_url, file_url)
    updating = database.update_database()
    print(len(list(updating)))
