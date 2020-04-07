from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
from datetime import datetime
import twitter_credentials
import gzip
import json
import os
import sys

class TwitterStreamer():
    def __init__(self):
        pass

    def stream_tweets(self, output, dict_path, fetched_tweets_filename, key_words = None, languages = None):
        listener = StdOutListener(output, dict_path, fetched_tweets_filename)
        auth = OAuthHandler(twitter_credentials.API_KEY, twitter_credentials.API_KEY_SECRET)
        auth.set_access_token(twitter_credentials.API_TOKEN, twitter_credentials.API_TOKEN_SECRET)
        stream = Stream(auth, listener)
        stream.filter(track = key_words, languages = languages)

class StdOutListener(StreamListener):
    def __init__(self, output, dict_path, fetched_tweets_filename):
        self.output = output
        self.base_name = fetched_tweets_filename
        self.fetched_tweets_filename = "{}/{}{}".format(output, fetched_tweets_filename, self.getFileEnd())
        self.json_list = []
        self.dict_path = dict_path
        self.id_dict = self.read_dict(dict_path)
        self.duplicates = 0

    def on_data(self, data):
        try:
            if len(self.json_list) > 5000:
                self.output_file()
                #Updating ID dictionary
                self.write_dict(self.dict_path, self.id_dict)
                self.id_dict = read_dict(dict_path)
            self.add_data(data)
            return True
        except BaseException as e:
            print("Error on_data %s" % str(e))
        return True

    def add_data(self, data):
        try:
            self.id_dict[data["id"]] += 1
        except:
            try:
                self.duplicates += 1
                self.id_dict[data["id"]] = 1
                self.json_list.append(data)
            except:
                """the tweet has no id field""" #This is usually a result of rate limitting
                self.json_list.append(data)

    def output_file(self):
        """Opening and writing to Gzip File after hitting 5000 tweets"""
        with gzip.open(self.fetched_tweets_filename + ".gz", 'wb') as f_out:
            f_out.write(json.dumps(self.json_list).encode('utf-8'))
        print("File Outputted: ", self.fetched_tweets_filename)
        #Getting New File Name and Resetting the JSON List
        self.fetched_tweets_filename = "{}/{}{}".format(self.output, self.base_name, self.getFileEnd())
        self.json_list = []

    def getFileEnd(self):
        now = datetime.now()
        return now.strftime("%d_%m_%Y_%H_%M_%S.json")

    def read_dict(self, path):
        with open(path, 'rb') as handle:
            return pickle.load(handle)

    def write_dict(self, path, dict):
        print("{} finished. There were {} duplicates encountered while streaming.".format(self.fetched_tweets_filename, duplicate - self.duplicates))
        with open(path, 'wb') as handle:
            pickle.dump(dict, handle, protocol=pickle.HIGHEST_PROTOCOL)
        self.duplicates = 0

    def on_error(self, status):
        print(status)

if __name__ == '__main__':
    output_directory = "../Tweets"
    dict_path = "../Tweets/id_dictionary.pickle"
    fetched_tweets_filename = "streamed_"
    twitter_streamer = TwitterStreamer()
    key_words = ["virus", "coronavirus", "corona virus", "sars-cov-2", "covid19", "covid", "covid-19", "pandemic", "epidemic", "outbreak", "wuhan", "infect"]
    twitter_streamer.stream_tweets(output_directory, fetched_tweets_filename, dict_path, key_words = key_words)
