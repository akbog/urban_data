from pyspark import SparkConf, SparkContext
from pyspark.sql import SQLContext, Row
from pyspark.sql.functions import mean as _mean, stddev as _stddev, col, udf

from textblob import TextBlob

import sparknlp
from sparknlp.base import Finisher, DocumentAssembler
from sparknlp.annotator import Tokenizer, Normalizer, LemmatizerModel, StopWordsCleaner, ViveknSentimentApproach, SentimentDetector, SentenceDetector, Stemmer, Lemmatizer
from pyspark.ml import Pipeline


if __name__ == "__main__":
    spark = sparknlp.start()
    print("Submitted")
