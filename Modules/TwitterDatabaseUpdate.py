import os
import nltk
import shutil
import pickle
import multiprocessing as mp
import json

from tqdm import tqdm
from langdetect import detect
# from postal.expand import expand_address
# from postal.parser import parse_address
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
from email.utils import parsedate_tz
import sqlalchemy as db

from models import *

import psycopg2

import os
import nltk
import shutil
import pickle
import multiprocessing as mp
import json
import operator
from collections import OrderedDict
import multiprocessing as mp
import atexit
import sys

from tqdm import tqdm
from langdetect import detect
# from postal.expand import expand_address
# from postal.parser import parse_address
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
from email.utils import parsedate_tz
import sqlalchemy as db

from models import *

class TwitterDatabase(object):
    def __init__(self, corpus, database_url, dict_url, **kwargs):
        self.corpus = corpus #Here we specify fileids so that we don't have to do the entire corpus at once
        self.connection = psycopg2.connect(
            host = "localhost",
            database = "twitter",
            user = os.environ["DB_USER"],
            password = os.environ["DB_PASS"]
        )
        self.count = 0
        self.file_url = dict_url
        with open(self.file_url, "rb") as read:
            self.ordered_dict = pickle.load(read)

    def fileids(self, fileids=None, categories=None):
        fileids = self.corpus._resolve(fileids, categories)
        if fileids:
            return fileids
        return self.corpus.fileids()

    #Function that detects language of a tweet
    def getLanguage(self, text):
        try:
            language = detect(text)
            return language
        except:
            return "00"

    def add_user(self, tweet):
        if "retweeted_status" in tweet:
            self.add_user(tweet["retweeted_status"])
        if "quoted_status" in tweet:
            self.add_user(tweet["quoted_status"])
        tweet = tweet["user"]
        new_user = {
            "user_id" : tweet["id"],
            "name" : tweet["name"],
            "handle" : tweet["screen_name"],
            "created" : tweet["created_at"],
            "bio" : tweet["description"],
            "is_verified" : tweet["verified"],
            "num_followers" : tweet["followers_count"],
            "num_friends" : tweet["friends_count"],
            "num_favourites" : tweet["favourites_count"],
            "num_tweets" : tweet["statuses_count"],
            "num_listed" : None,
            "located" : None
        }
        if tweet["location"]:
            new_user["located"] = tweet["location"]
        return new_user

    def add_tweet(self, tweet):
        if "retweeted_status" in tweet:
            self.add_tweet(tweet["retweeted_status"])
        if "quoted_status" in tweet:
            self.add_tweet(tweet["quoted_status"])
        if tweet["coordinates"]:
                self.add_geo(tweet["id"], json.dumps(tweet["coordinates"]))
        new_tweet = {
            "id" : tweet["id"],
            "user_id" : tweet["user"]["id"],
            "created" : tweet["created_at"],
            "reply_id" : tweet["in_reply_to_status_id"],
            "quote_count" : tweet["quote_count"],
            "reply_count" : tweet["reply_count"],
            "retweet_count" : tweet["retweet_count"],
            "favorite_count" : tweet["favorite_count"],
            "retweed_id" : None,
            "quote_id" : None,
        }
        if "retweeted_status" in tweet:
            if "extended_tweet" in tweet["retweeted_status"]:
                new_tweet["full_text"] = tweet["retweeted_status"]["extended_tweet"]["full_text"]
            else:
                new_tweet["full_text"] = tweet["retweeted_status"]["text"]
            new_tweet["retweet_id"] = tweet["retweeted_status"]["id"]
        elif "extended_tweet" in tweet:
            new_tweet["full_text"] = tweet["extended_tweet"]["full_text"]
        else:
            new_tweet["full_text"] = tweet['text']
        if "quoted_status" in tweet:
            new_tweet["quote_id"] = tweet["quoted_status"]["id"]
        new_tweet["language"] = self.getLanguage(new_tweet["full_text"])
        return new_tweet

    """Not In Use"""
    # def add_entities(self, id, tweet_ent):
    #     new_entity = {
    #         "tweet_id" : id,
    #         "entities" : tweet_ent
    #     }
    #     return new_entity

    def add_geo(self, id, geo_json):
        new_geo = {
            "tweet_id" : id,
            "coordinates" : geo_json
        }
        with self.connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO geo VALUES (
                    %(tweet_id)s,
                    %(coordinates)s
                );
            """, new_geo)
        return

    """Not In Use"""
    # def add_place(self, id, place_json):
    #     new_place = {
    #         "tweet_id" : id,
    #         "places" : place_json
    #     }
    #     return new_place

    def process(self, tweet):
        if not "id" in tweet:
            return
        if "retweeted_status" in tweet:
            self.process(tweet["retweeted_status"])
        if "quoted_status" in tweet:
            self.process(tweet["quoted_status"])
        return self.add_all(tweet)

    def update_file(self, filekey, fileid):
        del self.ordered_dict[filekey]
        self.count += 1
        if self.count > 10:
            with open(self.file_url, "wb") as write:
                pickle.dump(self.ordered_dict, write)
            self.count = 0
        print("Adding File: {} ".format(fileid), ("(COMPLETED)"))

    def add_all_users(self):
        with self.connection.cursor() as cursor:
            all_users = [
                self.add_user(tweet)
                for tweet in self.corpus.full_text_tweets_gen() if "id" in tweet
            ]
            psycopg2.extras.execute_batch(cursor, """
                INSERT INTO users VALUES (
                    %(user_id)s,
                    %(name)s,
                    %(handle)s,
                    %(created)s,
                    %(bio)s,
                    %(is_verified)s,
                    %(num_followers)s,
                    %(num_friends)s,
                    %(num_listed)s,
                    %(num_favourites)s,
                    %(num_tweets)s,
                    %(located)s
                ) ON CONFLICT (user_id) DO UPDATE SET users.created = %(created)s;
            """, all_users)

    def add_all_tweets(self):
        with self.connection.cursor() as cursor:
            all_tweets = [
                self.add_tweet(tweet)
                for tweet in self.corpus.full_text_tweets_gen() if "id" in tweet
            ]
            psycopg2.extras.execute_batch(cursor, """
                INSERT INTO tweet VALUES (
                    %(id)s,
                    %(user_id)s,
                    %(created)s,
                    %(full_text)s,
                    %(reply_id)s,
                    %(quote_id)s,
                    %(retweet_id)s,
                    %(quote_count)s,
                    %(reply_count)s,
                    %(retweet_count)s,
                    %(favorite_count)s,
                    %(language)s
                ) ON CONFLICT (id) DO UPDATE SET tweet.created = %(created)s;
            """, all_tweets)

    def add_file(self, fileid, filekey):
        self.corpus.init_doc(fileids = fileid)
        self.add_all_users()
        self.add_all_tweets()
        self.update_file(filekey, fileid)
        return fileid

    def update_database(self):
        files = [(key, value) for key, value in reversed(self.ordered_dict.items())]
        print("Starting Import")
        print("Inserting Tweets")
        tasks = [
            self.add_file(fileid, file_key)
            for file_key, fileid in files
        ]
        print("Finished Inserting {} Files".format(len(tasks)))
        return tasks
