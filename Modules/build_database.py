#So, I think I should build the database, without location built in
#Then, cycle through and build the database with locations
from TwitterReader import NewTwitterCorpusReader
from TwitterDatabase import ParallelTwitterDatabase
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

def sort_files(files):
    regex_str = r'Tweets\/streamed_([0-3][0-9])_([0-1][0-9])_([0-9][0-9][0-9][0-9])_([0-9][0-9])_([0-9][0-9])_([0-9][0-9])\.json\.gz'
    unordered_dict = {}
    for file in files:
        groups = re.match(regex_str, file)
        day, month, year, hour, minute, second = groups.groups()
        file_key = datetime(int(year), int(month), int(day), int(hour), int(minute), int(second))
        unordered_dict[file_key] = file
    return OrderedDict(sorted(unordered_dict.items(), key = operator.itemgetter(0)))

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
    elif len(sys.argv) <= 4:
        if sys.argv[2] == "clean":
            Base.metadata.drop_all(engine)
            Base.metadata.create_all(engine)
        elif sys.argv[2] == "append":
            pass
        elif sys.argv[3] == "reverse":
            reverse = True
        elif sys.argv[3] == "forward":
            reverse = False
        else:
            print("Second Arg Reserved for: clean or append")
            sys.exit(1)
    if reverse:
        file_url = 'tweet_dict.pkl'
    else:
        file_url = 'rev_tweet_dict.pkl'
    if not os.path.isfile(file_url):
        if not reverse:
            file_path = sys.argv[1]
            files = [os.path.join(FOLDER_PATTERN, f) for f in os.listdir(file_path) if re.match(DOC_PATTERN, str(os.path.join(FOLDER_PATTERN,f)))]
            files = sort_files(files)
            with open(file_url, "wb") as write:
                pickle.dump(files, write)
        else:
            file_path = sys.argv[1]
            files = [os.path.join(FOLDER_PATTERN, f) for f in os.listdir(file_path) if re.match(DOC_PATTERN, str(os.path.join(FOLDER_PATTERN,f)))]
            files = reverse(sort_files(files))
            with open(file_url, "wb") as write:
                pickle.dump(files, write)
    corpus = NewTwitterCorpusReader(root = root, fileids = DOC_PATTERN, cat_pattern = CAT_PATTERN)
    database = ParallelTwitterDatabase(corpus, database_url, file_url)
    updating = database.update_database()
    print(len(list(updating)))
