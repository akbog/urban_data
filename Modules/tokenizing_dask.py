import dask.dataframe as dd
import pyarrow.parquet as pq
import pyarrow as pa
from pyarrow import csv
import pandas as pd
from dask.distributed import Client
import os
import re
import nltk
from .RedditScore.redditscore.tokenizer import CrazyTokenizer
from timeit import default_timer as timer

OUTPUT_DIR = "../../../Tweet_Directory/DFST/"

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
    # c = Client(processes = True)
    c = Client()
    print(c)
    data = dd.read_parquet()
    data.map_partitions(tokenize).compute()
