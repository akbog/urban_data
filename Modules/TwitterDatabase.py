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
        self.engine = db.create_engine(database_url)
        self.make_session = sessionmaker(self.engine)
        self.session = self.make_session()
        self.file_url = dict_url
        with open(self.file_url, "rb") as read:
            self.ordered_dict = pickle.load(read)

    def initialize(self):
        Base.metadata.create_all(self.engine)

    def cleardb(self, confirm_string):
        if confirm_string == "confirm":
            Base.metadata.drop_all(self.engine)

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

    def add_tweet(self, tweet):
        new_tweet = Tweet(
            id = tweet["id"],
            user_id = tweet["user"]["id"],
            created = tweet["created_at"],
            reply_id = tweet["in_reply_to_status_id"],
            quote_count = tweet["quote_count"],
            reply_count = tweet["reply_count"],
            retweet_count = tweet["retweet_count"],
            favorite_count = tweet["favorite_count"]
        )
        if "retweeted_status" in tweet:
            if "extended_tweet" in tweet["retweeted_status"]:
                new_tweet.full_text = tweet["retweeted_status"]["extended_tweet"]["full_text"]
            else:
                new_tweet.full_text = tweet["retweeted_status"]["text"]
            new_tweet.retweet_id = tweet["retweeted_status"]["id"]
        elif "extended_tweet" in tweet:
            new_tweet.full_text = tweet["extended_tweet"]["full_text"]
        else:
            new_tweet.full_text = tweet['text']
        if "quoted_status" in tweet:
            new_tweet.quote_id = tweet["quoted_status"]["id"]
        new_tweet.language = self.getLanguage(new_tweet.full_text)
        # self.tweets_lst.append(new_tweet.__dict__)
        self.engine.execute(
           Tweet.__table__.insert(),
           [new_tweet.__dict__]
        )
        # self.session.add(new_tweet)
        # self.session.commit()

    def add_user(self, tweet):
        """Check if in table first"""
        if self.session.query(Users).filter_by(user_id = tweet["id"]).first():
            return
        new_user = Users(
            user_id = tweet["id"],
            name = tweet["name"],
            handle = tweet["screen_name"],
            created = tweet["created_at"],
            bio = tweet["description"],
            is_verified = tweet["verified"],
            num_followers = tweet["followers_count"],
            num_friends = tweet["friends_count"],
            num_favourites = tweet["favourites_count"],
            num_tweets = tweet["statuses_count"]
        )
        if tweet["location"]:
            new_user.located = tweet["location"]
        # self.users_lst.append(new_user.__dict__)
        self.engine.execute(
           Users.__table__.insert(),
           [new_user.__dict__]
        )
        # self.session.add(new_user)
        # self.session.commit()
        # self.addUserLocation(new_user, tweet)

    def add_entities(self, id, tweet_ent):
        new_entity = Entity(
            tweet_id = id,
            entities = tweet_ent
        )
        # self.entity_lst.append(new_entity.__dict__)
        self.engine.execute(
           Entity.__table__.insert(),
           [new_entity.__dict__]
        )
        # self.session.add(new_entity)

    def add_geo(self, id, geo_json):
        new_geo = Geo(
            tweet_id = id,
            coordinates = geo_json
        )
        # self.geo_lst.append(new_geo.__dict__)
        self.engine.execute(
           Geo.__table__.insert(),
           [new_geo.__dict__]
        )
        # self.session.add(new_geo)

    def add_place(self, id, place_json):
        new_place = Place(
            tweet_id = id,
            places = place_json
        )
        self.engine.execute(
           Place.__table__.insert(),
           [new_place.__dict__]
        )
        # self.place_lst.append(new_place.__dict__)
        # self.session.add(new_place)

    def add_all(self, tweet):
        if self.session.query(Tweet).filter_by(id = tweet["id"]).first():
            return
        self.add_user(tweet["user"])
        self.add_tweet(tweet)
        self.add_entities(tweet["id"], json.dumps(tweet["entities"]))
        if tweet["coordinates"]:
            self.add_geo(tweet["id"], json.dumps(tweet["coordinates"]))
        if tweet["place"]:
            self.add_place(tweet["id"], json.dumps(tweet["place"]))
        # self.session.commit()

    def process(self, tweet):
        if not "id" in tweet:
            return
        self.add_all(tweet)
        if "retweeted_status" in tweet:
            self.process(tweet["retweeted_status"])
        if "quoted_status" in tweet:
            self.process(tweet["quoted_status"])

    def add_file(self, fileid):
        for tweet in self.corpus.full_text_tweets(fileids = fileid):
            self.process(tweet)
        return fileid

    def update_database(self, fileids = None, categories = None):
        if self.file_url:
            count = 0
            files = [(key, value) for key, value in reversed(self.ordered_dict.items())]
            print("Inserting Tweets")
            while(len(files)):
                count += 1
                file_key, file_name = files.pop()
                try:
                    print("Adding File: {} ".format(file_name), end = " ")
                    yield self.add_file(file_name)
                    print("(Completed)")
                except:
                    print("Unexpected Error:", sys.exc_info()[0])
                    with open(file_url, "wb") as write:
                        pickle.dump(ordered_dict, write)
                    print("Uploaded {} Files Before Unplanned Exit".format(count))
                    continue
                del ordered_dict[file_key]
        else:
            for fileid in self.fileids(fileids, categories):
                yield self.add_file(fileid)

def save_file(file_name, ordered_dict):
    with open(file_name, "wb") as write:
        pickle.dump(ordered_dict, write)

class ParallelTwitterDatabase(TwitterDatabase):

    def __init__(self, *args, **kwargs):
        self.tasks = mp.cpu_count()
        self.results = []
        super(ParallelTwitterDatabase, self).__init__(*args, **kwargs)
        # atexit.register(save_file, self.file_url, self.ordered_dict)

    def on_result(self, file_key):
        print("Added File: ", result, " (COMPLETED)")
        del self.ordered_dict[file_key]
        def inner(result):
            self.results.append(result)
        return inner

    def update_database(self):
        pool = mp.Pool(processes = self.tasks)
        files = [(key, value) for key, value in reversed(self.ordered_dict.items())]
        print(len(files))
        print("Initializing Pool")
        tasks = [
            pool.apply_async(self.add_file, (fileid,), callback = self.on_result(file_key))
            for file_key, fileid in files
        ]
        print(len(tasks))
        pool.close()
        print("Starting Pool")
        pool.join()
        return self.results
