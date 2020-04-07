from Modules.NewTwitterReader import GzipStreamBackedCorpusView, NewTwitterCorpusReader
import pickle

if __name__ == "__main__":
    root = r'../'
    doc_pattern = r'Tweets/streamed_[0-3][0-9]_[0-1][0-9]_[0-9][0-9][0-9][0-9]_[0-9][0-9]_[0-9][0-9]_[0-9][0-9]\.json\.gz$'
    cat_pattern = r'.*Tweets.*'
    dict_path = "../Tweets/id_dictionary.pickle"
    pre_corpus = NewTwitterCorpusReader(root = root, fileids = doc_pattern, cat_pattern = cat_pattern)
    pre_corpus.update_data_dictionary(dict_path, categories = cat_pattern)
    with open(dict_path, 'rb') as handle:
        ids = pickle.load(handle)
    print("There are {} unique tweets".format(len(ids)))
