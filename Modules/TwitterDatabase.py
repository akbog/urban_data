import os
import nltk
import shutil
import pickle
import multiprocessing as mp
import json

from tqdm import tqdm
from langdetect import detect
from .java_tweet_tokenizer import *
from sqlalchemy.orm import sessionmaker
import sqlalchemy as db
from postal.expand import expand_address
from postal.parser import parse_address

from .models import *

class TwitterDatabase(object):
    def __init__(self, corpus, database_url, **kwargs):
        self.corpus = corpus
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


    def locDict(self, loc_array):
        loc_dict = {"suburb" : None,
                    "city_district" : None,
                    "city" : None,
                    "state_district" : None,
                    "state" : None,
                    "country_region" : None,
                    "country" : None,
                    "world_region" : None}
        for parse in loc_array:
            loc_dict[parse[1]] = parse[0]
        return loc_dict

    def addUserLocation(self, row, tweet):
        if not tweet["location"]:
            return
        loc_dict = self.locDict(parse_address(tweet["location"]))
        new_location = Location(
            user_id = row.user_id,
            suburb = loc_dict["suburb"],
            city_dist = loc_dict["city_district"],
            city = loc_dict["city"],
            state_dist = loc_dict["state_district"],
            state = loc_dict["state"],
            region_cn = loc_dict["country_region"],
            country = loc_dict["country"],
            region_wd = loc_dict["world_region"]
        )
        self.session.add(new_location)
        self.session.commit()

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
        if tweet["truncated"]:
            new_tweet.full_text = tweet["extended_tweet"]["full_text"]
        else:
            new_tweet.full_text = tweet['text']
        try:
            new_tweet.quote_id = tweet["quoted_status_id"]
        except:
            pass
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
        self.session.add(new_user)
        self.session.commit()
        self.addUserLocation(new_user, tweet)

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

    def add_file(self, fileid):
        for tweet in self.corpus.full_text_tweets(fileids = fileid):
            try:
                tweet["id"]
            except:
                continue
            if self.session.query(Tweet).filter_by(id = tweet["id"]).first():
                continue
            self.add_user(tweet["user"])
            self.add_tweet(tweet)
            self.add_entities(tweet["id"], json.dumps(tweet["entities"]))
            if tweet["coordinates"]:
                self.add_geo(tweet["id"], json.dumps(tweet["coordinates"]))
            if tweet["place"]:
                self.add_place(tweet["id"], json.dumps(tweet["place"]))
            self.session.commit()


    def update_database(self, fileids = None, categories = None):
        for fileid in self.fileids(fileids, categories):
            yield self.add_file(fileid)
