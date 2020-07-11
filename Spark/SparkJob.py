from pyspark import SparkConf, SparkContext
from pyspark.sql import SQLContext, Row
from pyspark.sql.functions import mean as _mean, stddev as _stddev, col, udf

from textblob import TextBlob

import sparknlp
from sparknlp import SparkSession
from sparknlp.base import Finisher, DocumentAssembler
from sparknlp.annotator import Tokenizer, Normalizer, LemmatizerModel, StopWordsCleaner, ViveknSentimentApproach, SentimentDetector, SentenceDetector, Stemmer, Lemmatizer
from pyspark.ml import Pipeline


if __name__ == "__main__":
    #Launching Spark
    spark = sparknlp.start()
    # spark = SparkSession.builder \
    #     .appName("Spark NLP")\
    #     .master("local[*]")\
    #     .config("spark.driver.memory","256G")\
    #     .config("spark.jars.packages", "com.johnsnowlabs.nlp:spark-nlp_2.11:2.5.3")\
    #     .config("spark.kryoserializer.buffer.max", "1000M")\
    #     .getOrCreate()
    sqlCtx = SQLContext(spark)
    spark.sparkContext.setLogLevel('ERROR')
    #Setting input Directory
    input_file = "../../../Tweets_Sorted/2020_3_31/"
    twitter = sqlCtx.read.json(input_file)
    twitter.registerTempTable("tweets")
    print("Reached Here")
    print("Number of Tweets:", twitter.count())
