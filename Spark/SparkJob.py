from pyspark import SparkConf, SparkContext
from pyspark.sql import SQLContext, Row
from pyspark.sql.functions import mean as _mean, stddev as _stddev, col, udf

from textblob import TextBlob

import sparknlp
from sparknlp import SparkSession
from sparknlp.base import Finisher, DocumentAssembler
from sparknlp.annotator import Tokenizer, Normalizer, LemmatizerModel, StopWordsCleaner, ViveknSentimentApproach, SentimentDetector, SentenceDetector, Stemmer, Lemmatizer
from pyspark.ml import Pipeline
import sys
import time


if __name__ == "__main__":
    #Launching Spark
    # spark = sparknlp.start()
    get_ip = sys.argv[1]
    get_port = sys.argv[2]
    spark = SparkSession.builder \
        .appName("Spark NLP")\
        .master("{}:{}".format(get_ip, get_port))\
        .config("spark.driver.memory","200G")\
        .config("spark.jars.packages", "com.johnsnowlabs.nlp:spark-nlp_2.11:2.5.3")\
        .config("spark.kryoserializer.buffer.max", "1000M")\
        .getOrCreate()
    print("here")
    while(True):
        time.sleep(100)
    print("here")
    # sqlCtx = SQLContext(spark)
    # spark.sparkContext.setLogLevel('ERROR')
    # #Setting input Directory
    # input_file = "../../../Tweets_Sorted/2020_3_31/"
    # twitter = sqlCtx.read.json(input_file)
    # twitter.registerTempTable("tweets")
    # print("Reached Here")
    # print("Number of Tweets:", twitter.count())
