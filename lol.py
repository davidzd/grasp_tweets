import couchdb
import httplib
import tweepy
import json
import time
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer


ACCESS_TOKEN = '726231819289382912-z7VrMFkGq1xJTTBiVSFtNOP1H0ctDOW'
ACCESS_SECRET = 'nU4iLfPzcmxsVaZ7ZE0YEJKndoDCGW6JyV9FnWOicRD7a'
CONSUMER_KEY = '1rx2B1kw9FeZIGjVtkf01u3rG'
CONSUMER_SECRET = 'W3s4Mxj8TuXBgWcJkiZSPoXkR6ItE60WdL9XqwRXt8zkQ9sI4t'

def db():
	couch_database = couchdb.Server('http://127.0.0.1:5984/')
	cloud_tweets = couch_database['cloud_tweets_world']
	return cloud_tweets

def save_data_into_database(database, tweet):
	database.save(tweet)

try:
    db = db()
    print("opened")
    sid = SentimentIntensityAnalyzer()
except couchdb.ResourceNotFound:
    print("creating db")

class StreamListener(tweepy.StreamListener):
	# def on_data(self, data):
	# 	try:
	# 		print data
	# 	except BaseException, e:
	# 		print 'What happened: ', str(e)
    def on_status(self, status):
        global db  # couchdb (global)
        try:
            # print(status.created_at)
            # skip retweets
            if status.retweet_count:
                return True
            # skip if already in couch
            if status.id_str in db:
                return True
            results = {}
            # status info. See: https://dev.twitter.com/docs/api/1/get/statuses/show/%3Aid
            results['text'] = status.text.lower()
            results['orig_text'] = status.text
            results['sentiment'] = sid.polarity_scores(status.text)['compound']
            results['id_str'] = status.id_str
            results['created_at'] = time.asctime(time.localtime(time.mktime(status.created_at.utctimetuple())))
            results['location'] = status.place.full_name
            # time.mktime(status.created_at.utctimetuple())
            results['entities'] = status.entities  # urls, hashtags, mentions,
            results['source'] = status.source
            results['geo'] = status.geo
            # results['location'] = status.location
            results['lang'] = status.lang
            results['retweet_count'] = status.retweet_count
            results['retweeted'] = status.retweeted
            results['device'] = status.source
            # user info
            results['user_id'] = status.user.id
            results['user_color'] = status.user.profile_link_color
            results['user_location'] = status.user.location
            results['user_friends_count'] = status.user.friends_count
            results['user_followers_count'] = status.user.followers_count
            db.save(results)
        except BaseException, e:
            print 'What happened: ', str(e)

	def on_error(self, status):
		print status

def stream_twitter():

	oauth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
	oauth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
	api = tweepy.API(oauth)
	stream_listener = StreamListener()
	tweet_stream = tweepy.streaming.Stream(auth=api.auth, listener=stream_listener)
	tweet_stream.filter(locations=[-74,40,-73,41])

stream_twitter()
