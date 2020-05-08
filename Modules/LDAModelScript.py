from Urban_Research.urban_data.Modules.NewParquetTransformer import GensimTopicModels
import pyarrow.parquet as pq
import pyarrow as pa
import dask.dataframe as dd
from pyarrow.parquet import read_schema, ParquetDataset
from sklearn.externals import joblib

DATA_DIR = "Tweet_Directory/DFST/"

def get_text(data, row_chunks):
    for i in range(len(row_chunks)):
        for index, row in data.get_partition(i).compute().iterrows(): #error is here
            yield row["tokens"]

if __name__ == "__main__":
    filters = [[("tw_year", "=", 2020), ("tw_month", "=", 3), ("tw_day", "=", 31)],[("tw_year", "=", 2020), ("tw_month", "=", 4)]]
    data = dd.read_parquet(DATA_DIR, columns = ['tokens'], filters = filters)
    row_chunks = list(data.map_partitions(len).compute())
    corpus = get_text(data, row_chunks)
    docs = (tokens for tokens in corpus)
    gensim_lda = GensimTopicModels(docs, time_slices = row_chunks)
    gensim_lda.fit()
    try:
        output_model = "GensimModelSpecific.model"
        gensim_lda.model.named_steps['model'].gensim_model.save(output_model)
    except:
        print("Could not save output_model, no such method")
    try:
        output_model = "GensimModelTop.model"
        gensim_lda.save(output_model)
    except:
        print("No Method For Pipeline Object: Save")
    try:
        output_model = "GensimModelMiddle.model"
        gensim_lda.model.named_steps['model'].save(output_model)
    except:
        print("No Method For Mid Pipeline Object: Save")
    try:
        joblib.dump(gensim_lda, "GensimModel.pkl")
    except:
        print("Cannot Dump Model")
    try:
        joblib.dump(gensim_lda.model.named_steps['model'], "MidGensimModel.pkl")
    except:
        print("Cannot Dump Model")
