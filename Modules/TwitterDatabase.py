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

class TwitterDatabase(object):
    def __init__(self, corpus, database_url, **kwargs):
        self.corpus = corpus #Here we specify fileids so that we don't have to do the entire corpus at once
        self.engine = db.create_engine(database_url)
        self.make_session = sessionmaker(self.engine)
        self.session = self.make_session()

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


    # def locDict(self, loc_array):
    #     """
    #         Function is Depracated
    #         Replaced by Nominatim Geocoding Raw String
    #     """
    #     loc_dict = {"suburb" : None,
    #                 "city_district" : None,
    #                 "city" : None,
    #                 "state_district" : None,
    #                 "state" : None,
    #                 "country_region" : None,
    #                 "country" : None,
    #                 "world_region" : None}
    #     for parse in loc_array:
    #         loc_dict[parse[1]] = parse[0]
    #     return loc_dict

    # def addUserLocation(self, row, tweet):
    #     """
    #         Function is Depracated
    #         Replaced by Nominatim Geocoding Raw String
    #     """
    #     if not tweet["location"]:
    #         return
    #     loc_dict = self.locDict(parse_address(tweet["location"]))
    #     new_location = Location(
    #         user_id = row.user_id,
    #         suburb = loc_dict["suburb"],
    #         city_dist = loc_dict["city_district"],
    #         city = loc_dict["city"],
    #         state_dist = loc_dict["state_district"],
    #         state = loc_dict["state"],
    #         region_cn = loc_dict["country_region"],
    #         country = loc_dict["country"],
    #         region_wd = loc_dict["world_region"]
    #     )
    #     self.session.add(new_location)
    #     self.session.commit()

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
        self.session.add(new_tweet)
        self.session.commit()

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
        self.session.add(new_user)
        self.session.commit()
        # self.addUserLocation(new_user, tweet)

    def add_entities(self, id, tweet_ent):
        new_entity = Entity(
            tweet_id = id,
            entities = tweet_ent
        )
        self.session.add(new_entity)

    def add_geo(self, id, geo_json):
        new_geo = Geo(
            tweet_id = id,
            coordinates = geo_json
        )
        self.session.add(new_geo)

    def add_place(self, id, place_json):
        new_place = Place(
            tweet_id = id,
            places = place_json
        )
        self.session.add(new_place)

    def add_all(self, tweet):
        self.add_user(tweet["user"])
        self.add_tweet(tweet)
        self.add_entities(tweet["id"], json.dumps(tweet["entities"]))
        if tweet["coordinates"]:
            self.add_geo(tweet["id"], json.dumps(tweet["coordinates"]))
        if tweet["place"]:
            self.add_place(tweet["id"], json.dumps(tweet["place"]))
        self.session.commit()

    def to_datetime(self, datestring):
        time_tuple = parsedate_tz(datestring.strip())
        dt = datetime(*time_tuple[:6])
        return dt - timedelta(seconds = time_tuple[-1])

    def update_values(self, tweet):
        tweet_old = self.session.query(Tweet).filter_by(id = tweet["id"]).first()
        if tweet_old.created < self.to_datetime(tweet["created_at"]):
            self.session.delete(tweet_old)
            self.session.commit()
            self.add_all(tweet)

    def checkTweetID(self, tweet):
        if self.session.query(Tweet).filter_by(id = tweet["id"]).first():
            self.update_values(tweet)
        else:
            self.add_all(tweet)

    def process(self, tweet):
        if not "id" in tweet:
            return
        self.checkTweetID(tweet)
        if "retweeted_status" in tweet:
            self.process(tweet["retweeted_status"])
        if "quoted_status" in tweet:
            self.process(tweet["quoted_status"])

    def add_file(self, fileid):
        for tweet in self.corpus.full_text_tweets(fileids = fileid):
            self.process(tweet)

    def update_database(self, fileids = None, categories = None, file_url = None):
        if file_url:
            count = 0
            with open(file_url, "rb") as read:
                files = pickle.load(read)
            while(len(files)):
                count += 1
                try:
                    file_name = files.pop()
                    print("Adding File: {} ".format(file_name), end = "")
                    yield self.add_file(file_name)
                    print("(Completed)")
                except:
                    with open("tweet_list.pkl", "wb") as write:
                        pickle.dump(files, write)
                    print("Uploaded {} Files Before Unplanned Exit".format(count))
        else:
            for fileid in self.fileids(fileids, categories):
                yield self.add_file(fileid)
