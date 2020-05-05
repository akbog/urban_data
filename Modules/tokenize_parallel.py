import os
import sys
import pyarrow.parquet as pq
import pyarrow as pa
from pyarrow import csv
import pandas as pd

def build_output_file(output_file):
    print("Building File For Parsing: ", end = "")
    temp = pd.DataFrame(columns = ['id', 'user_id', 'created', 'full_text', 'tw_year', 'tw_month', 'tw_day'])
    temp.to_csv(output_file, index = False)
    print("(COMPLETE)")

def iterate_chunks(input_file, output_file):
    print("Appending to File for Parsing: ", end = "")
    data_types = {'id' : 'int64', 'user_id' : 'int64', 'full_text' : 'object'}
    df = pd.read_csv(input_file, dtype = data_types, parse_dates = ['created'], iterator = True, encoding = "utf-8")
    go = True
    while(go):
        try:
            chunk = df.get_chunk(100000)
        except Exception as e:
            print("(COMPLETE)")
            print(type(e))
            go = False
        chunk['tw_year'] = pd.DatetimeIndex(chunk['created']).year
        chunk['tw_month'] = pd.DatetimeIndex(chunk['created']).month
        chunk['tw_day'] = pd.DatetimeIndex(chunk['created']).day
        chunk = chunk.astype({'id' : 'int64', 'user_id' : 'int64', 'full_text' : 'object','tw_year' : 'int64', 'tw_month' : 'int64', 'tw_day' : 'int64'})
        chunk.to_csv(output_file, mode = 'a', line_terminator = '\n', header = None, index = False)

def build_directory(input_file, output_directory):
    print("Building Parquet Output Directory: ", end = "")
    wd_types = {'id' : 'int64', 'user_id' : 'int64', 'full_text' : 'object','tw_year' : 'int64', 'tw_month' : 'int64', 'tw_day' : 'int64'}
    with_days_csv = pd.read_csv(input_file, header = 0, dtype = wd_types, parse_dates = ['created'], lineterminator = "\n")
    table = pa.Table.from_pandas(with_days_csv)
    pq.write_to_dataset(table, root_path = output_directory, partition_cols=['tw_year', 'tw_month', 'tw_day'])
    print("(COMPLETE)")

if __name__ == "__main__":
    input_file = sys.argv[1]
    inter_file = sys.argv[2]
    output_dir = sys.argv[3]
    build_output_file(inter_file)
    iterate_chunks(input_file, inter_file)
    build_directory(inter_file, output_dir)
