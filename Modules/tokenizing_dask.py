import dask.dataframe as dd
import pyarrow.parquet as pq
import pyarrow as pa
from pyarrow import csv
import pandas as pd
from dask.distributed import Client
import os
import re
import nltk
from redditscore.tokenizer import CrazyTokenizer
from timeit import default_timer as timer

OUTPUT_DIR = "../../../Tweet_Directory/DFST/"

DATA_DIR = "../../../Tweet_Directory/DFS/"

PATTERNS = [
    ('group1',re.compile(r"(?i)sars-cov|sars-cov-2|sarscov-2|sarscov2|sarscov|sars-cov|covid_19|covidー19|covid-19|covid19|covid19|cov-2|cov2|covid2019|cov2019|cov19|corona-virus|corona virus|covid 19|cov 19|covid|corona"),"coronavirus"),
]

def tokenize(partition):
    partition_name = "{}-{}-{}".format(partition["tw_year"].iloc[0],partition["tw_month"].iloc[0],partition["tw_day"].iloc[0])
    start = timer()
    print("Begining Tokenization: {}".format(partition_name))
    tokenizer = CrazyTokenizer(extra_patterns = PATTERNS, lowercase = True, normalize = 3, ignore_quotes = False,
                        ignore_stopwords = True, stem = "lemm", remove_punct = True, remove_numbers = True,
                        remove_breaks = True, decontract = True, hashtags = "split", twitter_handles = '', urls = False)
    partition["tokens"] = partition["full_text"].apply(tokenizer.tokenize)
    table = pa.Table.from_pandas(partition)
    pq.write_to_dataset(table, root_path = OUTPUT_DIR, partition_cols=['tw_year', 'tw_month', 'tw_day'])
    end = timer()
    print("Tokenization Finished for {}. Took {} seconds.".format(partition_name, end-start))

if __name__ == "__main__":
    c = Client(n_workers = 64, processes = True)
    # c = Client()
    print(c)
    filters = [[("tw_year", "=", 2020), ("tw_month", "=", 4), ("tw_day", "=", 8)],[("tw_year", "=", 2020), ("tw_month", "=", 4), ("tw_day", "=", 9)],[("tw_year", "=", 2020), ("tw_month", "=", 4), ("tw_day", "=", 10)],[("tw_year", "=", 2020), ("tw_month", "=", 4), ("tw_day", "=", 11)], [("tw_year", "=", 2020), ("tw_month", "=", 4), ("tw_day", "=", 12)], [("tw_year", "=", 2020), ("tw_month", "=", 4), ("tw_day", "=", 13)], [("tw_year", "=", 2020), ("tw_month", "=", 4), ("tw_day", "=", 14)]]
    data = dd.read_parquet(DATA_DIR, filters = filters)
    data.map_partitions(tokenize).compute()
