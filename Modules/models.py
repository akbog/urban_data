from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import sqlalchemy as db

Base = declarative_base()

class Users(Base):
    __tablename__ = 'users'
    user_id = db.Column(db.BigInteger, primary_key = True)
    name = db.Column(db.String(128), nullable = True, unique = False)
    handle = db.Column(db.String(64), nullable = False)
    created = db.Column(db.DateTime(), nullable = False, unique = False)
    bio = db.Column(db.Text, nullable = True, unique = False)
    is_verified = db.Column(db.Boolean, default = False)
    num_followers = db.Column(db.Integer, nullable = True, unique = False)
    num_friends = db.Column(db.Integer, nullable = True, unique = False)
    num_listed = db.Column(db.Integer, nullable = True, unique = False)
    num_favourites = db.Column(db.Integer, nullable = True, unique = False)
    num_tweets = db.Column(db.Integer, nullable = True, unique = False)
    located = db.Column(db.Text, nullable = True, unique = False)
    tweet = relationship('Tweet', backref = 'users', lazy = True)
    location = relationship('Location', backref = 'users', lazy = True)

# class Location(Base):
#     __tablename__ = 'location'
#     user_id = db.Column(db.BigInteger, db.ForeignKey('users.user_id'), primary_key = True, nullable = False)
#     suburb = db.Column(db.String(32), nullable = True, unique = False)
#     city_dist = db.Column(db.String(32), nullable = True, unique = False)
#     city = db.Column(db.String(32), nullable = True, unique = False)
#     state_dist = db.Column(db.String(32), nullable = True, unique = False)
#     state = db.Column(db.String(32), nullable = True, unique = False)
#     region_cn = db.Column(db.String(32), nullable = True, unique = False)
#     country = db.Column(db.String(32), nullable = True, unique = False)
#     region_wd = db.Column(db.String(32), nullable = True, unique = False)

class Location(Base):
    __tablename__ = 'location'
    user_id = db.Column(db.BigInteger, db.ForeignKey('users.user_id'), primary_key = True, nullable = False)
    address = db.Column(db.Text, nullable = True, unique = False)
    longitude = db.Column(db.Float, nullable = True, unique = False)
    latitude = db.Column(db.Float, nullable = True, unique = False)

class Tweet(Base):
    __tablename__ = 'tweet'
    id = db.Column(db.BigInteger, primary_key = True)
    user_id = db.Column(db.BigInteger, db.ForeignKey('users.user_id'), unique = False, nullable = False)
    created = db.Column(db.DateTime(), nullable = False, unique = False)
    full_text = db.Column(db.Text, unique = False, nullable = False)
    reply_id = db.Column(db.BigInteger, unique = False, nullable = True)
    quote_id = db.Column(db.BigInteger, unique = False, nullable = True)
    retweet_id = db.Column(db.BigInteger, unique = False, nullable = True)
    quote_count = db.Column(db.Integer, unique = False, nullable = True)
    reply_count = db.Column(db.Integer, unique = False, nullable = True)
    retweet_count = db.Column(db.Integer, unique = False, nullable = True)
    favorite_count = db.Column(db.Integer, unique = False, nullable = True)
    language = db.Column(db.String(8), unique = False, nullable = False)
    tokenized = db.Column(db.JSON(), nullable = True, unique = False)
    entities = relationship('Entity', backref = 'tweet', lazy = True)
    # tokens = relationship('TokenizedTweet', backref = 'tweet', lazy = True)
    geos = relationship('Geo', backref = 'tweet', lazy = True)
    places = relationship('Place', backref = 'tweet', lazy = True)

# class TokenizedTweet(Base):
#     __tablename__ = 'tokenizedtweet'
#     tweet_id = db.Column(db.BigInteger, db.ForeignKey('tweet.id'), primary_key = True)
#     tokenized = db.Column(db.JSON(), nullable = False, unique = False)

class Entity(Base):
    __tablename__ = 'entity'
    tweet_id = db.Column(db.BigInteger, db.ForeignKey('tweet.id'), primary_key = True)
    entities = db.Column(db.JSON(), nullable = False, unique = False)

class Geo(Base):
    __tablename__ = 'geo'
    tweet_id = db.Column(db.BigInteger, db.ForeignKey('tweet.id'), primary_key = True)
    coordinates = db.Column(db.JSON(), nullable = False, unique = False)

class Place(Base):
    __tablename__ = 'place'
    tweet_id = db.Column(db.BigInteger, db.ForeignKey('tweet.id'), primary_key = True)
    places = db.Column(db.JSON(), nullable = False, unique = False)
