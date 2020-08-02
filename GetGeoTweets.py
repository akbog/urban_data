import os
import sys
import traceback
import pyspark
import time
import pyspark.sql.functions as f
from pyspark.sql import SQLContext
from pyspark.sql import Window
from pyspark.sql.functions import mean as _mean, stddev as _stddev, to_date as _to_date, sqrt as _sqrt, col, lit, monotonically_increasing_id, udf
from datetime import date, datetime


def get_list(dir_path, output_path):
    in_folders = {datetime.strptime(folder, "%Y_%m_%d") for folder in os.listdir(dir_path) if len(folder) == 10}
    out_folders = {datetime.strptime(folder, "%Y_%m_%d") for folder in os.listdir(output_path)}
    folders = list(in_folders - out_folders)
    folders.sort()
    return [os.path.join(dir_path, folder.strftime("%Y_%m_%d")) for folder in folders]

if __name__=="__main__":
    os.environ["JAVA_HOME"] = "/usr/lib/jvm/java-1.8.0-openjdk-amd64/jre"
    os.environ["SPARK_HOME"] = "../venv-tweets/lib/python3.6/site-packages/pyspark/"
    memory = '32g'
    pyspark_submit_args = ' --driver-memory ' + memory + ' pyspark-shell'
    os.environ["PYSPARK_SUBMIT_ARGS"] = pyspark_submit_args
    sc = pyspark.SparkContext()
    sc.setLogLevel("WARN")
    sqlCtx = SQLContext(sc)
    try:
        dir_path = sys.argv[1]
    except:
        dir_path = "../../SparkNLP/Tweets"
    try:
        output_path = sys.argv[2]
    except:
        output_path = "../../SparkNLP/GeoTaggedTweets"
    try:
        if sys.argv[3] == "filter_tweets":
            filter_tweets = True
        else:
            filter_tweets = False
    except:
        filter_tweets = True
    try:
        if sys.argv[4] == "filter_users":
            filter_users = True
        else:
            filter_users = False
    except:
        filter_users = True
    dir_days = get_list(dir_path, output_path)
    log_list = []
    running_total = 0
    for folder in dir_days:
        start_time = datetime.now()
        file_name = folder.replace(dir_path + "/", "")
        try:
            print("[{}] Reading in Directory: ".format(start_time.strftime("%Y-%m-%d %H:%m:%S")), file_name, end = "| ")
            twitter = sqlCtx.read.json(folder)
            twitter.registerTempTable("tweets")
            print("(Completed)", end = "\n")
            #Cleaning up empty/useless tweets
            twitter = twitter.where(~col("id").isNull())
            if filter_tweets:
                print("\t(Filtering to root{n})", end = "| ")
                retweets = twitter.groupBy("retweeted_status.id").count().orderBy(col("count").desc())
                w = Window.partitionBy('retweeted_status.id').orderBy('retweeted_status.id')
                rt_count = twitter.withColumn('mono_id', f.row_number().over(w))
                root_filt = rt_count.withColumn('rt_count', f.max('mono_id').over(w)).where((f.col('mono_id') <= f.ceil(f.sqrt('rt_count'))) | (f.col('retweeted_status.id').isNull()))
                root_filt = root_filt.drop("rt_count").drop("mono_id")
            if filter_users:
                print("(Removing Suspicious Users)", end = "| ")
                stats = twitter.select(
                        f.mean(f.log10(col('user.followers_count') + 1)).alias('followers_mean'),
                        f.stddev(f.log10(col('user.followers_count') + 1)).alias('followers_std'),
                        f.mean(f.log10(col('user.friends_count') + 1)).alias('friends_mean'),
                        f.stddev(f.log10(col('user.friends_count') + 1)).alias('friends_std'),
                        f.mean(f.log10(col('user.statuses_count') + 1)).alias('statuses_mean'),
                        f.stddev(f.log10(col('user.statuses_count') + 1)).alias('statuses_std')
                        ).collect()
                user_filt = twitter.where((f.log10(f.col('user.followers_count')) <= stats[0]['followers_mean'] + 3*stats[0]['followers_std']) & \
                        (f.log10(f.col('user.friends_count')) <= stats[0]['friends_mean'] + 3*stats[0]['friends_std']) & \
                        (f.log10(f.col('user.statuses_count')) <= stats[0]['statuses_mean'] + 3*stats[0]['statuses_std']) & \
                        (f.log10(f.col('user.followers_count')) >= stats[0]['followers_mean'] - 3*stats[0]['followers_std']) & \
                        (f.log10(f.col('user.friends_count')) >= stats[0]['friends_mean'] - 3*stats[0]['friends_std']) & \
                        (f.log10(f.col('user.statuses_count')) >= stats[0]['statuses_mean'] - 3*stats[0]['statuses_std']))
            if filter_users and filter_tweets:
                print("(Intersecting Filters)", end = "| ")
                if user_filt.count() > root_filt.count():
                    urt_root = user_filt.join(root_filt,["id"], how ='leftsemi')
                else:
                    urt_root = root_filt.join(user_filt,["id"], how ='leftsemi')
            elif filter_user:
                urt_root = user_filt
            elif filter_tweets:
                urt_root = root_filt
            else:
                urt_root = twitter
            print("(Retaining Geo Tweets)", end = "\n")
            final = urt_root.where((~col("geo").isNull()) | (~col("retweeted_status.geo").isNull()) | (~col("quoted_status.geo").isNull()) |
                                    (~col("place").isNull()) | (~col("retweeted_status.place").isNull()) | (~col("quoted_status.place").isNull()) |
                                    (~col("coordinates").isNull()) | (~col("retweeted_status.coordinates").isNull()) | (~col("quoted_status.coordinates").isNull()))
            final.write.option("compression", "gzip").json(os.path.join(output_path, file_name))
            print("\tProcess Completed in ({:.2f}) minutes".format((datetime.now() - start_time).seconds/60))
            running_former = running_total
            running_total += final.count()
            print("\t# of Tweets Added: ", running_total - running_former, "(Total:{})".format(running_total))
        except Exception:
            print("\n!-Encountered Unexpected Issue-! (Skipping: {})".format(file_name))
            log_list.append(file_name)
            traceback.print_exc()
            time.sleep(10)
    print("\tErrors Occured in: ", log_list)
