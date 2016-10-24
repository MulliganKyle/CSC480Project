'''
Make new twitter dummy acct
Check rate limit. on remaining trends, queries, searches
Print tweets to file.
Scrub file.
'''
from __future__ import print_function
import time
import sys
import tweepy
import re
import pickle
from tweepy import OAuthHandler
from apiKeys import * #consumer_key, consumer_secret, access_token, and access_secret
from Tweet import *

# Authentication
united_states_woeid = 23424977
non_bmp_map = dict.fromkeys(range(0x10000, sys.maxunicode + 1), 0xfffd)
auth = OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_secret)
api = tweepy.API(auth)
EXHAUST_TIME = 900 #15 mins
DAILY_TIME = 86400 #24 hours
NUM_OF_TWEETS = 1 #Per trending topic
dumpFile = open('Dump', 'a') #Append to dump file

def rate_limit_status():
	data = api.rate_limit_status()
	print("Rate Limit Status:\n")
	print("Trends: " + str(data['resources']['trends']['/trends/place']))
	print("Searches: " + str(data['resources']['search']['/search/tweets']))

def time_delay(timeToWait):
	time.sleep(timeToWait)

# If remaining is 1 or 15 wait 15mins. Running once a day? every 12 hours?
def check_limit():
	data = api.rate_limit_status()
	trendsRemaining = data['resources']['trends']['/trends/place']['remaining']
	searchesRemaining = data['resources']['search']['/search/tweets']['remaining']
	if trendsRemaining == 1 or searchesRemaining == 50:
		print("Exhausted limit...Waiting 15 mins.\n")
		TimeDelay(WAIT_TIME)

def dump_tweets(serialized_tweets):
	pickle.dump(serialized_tweets, open( "SerializedTweets.p", "wb" ))
	for tweet in serialized_tweets:
		dumpFile.write("Topic: " + tweet.topic + "\nTweet(s):\n")
		dumpFile.write(tweet.text.encode('utf8'))
# For testing only
#	dumpFile.write("Retrieved " + str(len(trendNames)) + " US trending topics:\n")
#	dumpFile.write(str(trendNames))
#	dumpFile.write("\nPrinting " + str(NUM_OF_TWEETS) + " tweet per topic\n")
'''	for trendName in trendNames:
		dumpFile.write("Topic: " + trendName.encode('utf8') + ".\nTweet(s):\n")
  		#get 1 tweet per trendName (max 100)
   		tweets = tweepy.Cursor(api.search, q = trendName).items(NUM_OF_TWEETS)
   		for tweet in tweets:
   			dumpFile.write(tweet.text.translate(non_bmp_map).encode('utf8'))
   			dumpFile.write('\n\n')
'''

def scrub_tweet(tweet):
	# Take out RT's
	if tweet.text[:3] == 'RT ':
		tweet.text = tweet.text[3:]
	# Take out hyper links
	tweet.text = re.sub(r"http\S+", "", tweet.text)

#   Pulls tweets from twitter
#   Scrubs each one
#   Then places them in a set of Tweet objects
#   Returns set to be written to file.
def pull_tweets():
	tweets_to_analyze = set()
	trends = api.trends_place(united_states_woeid)[0]['trends']
	trendNames = [trend['name'] for trend in trends]
	for trendName in trendNames:
		tweets = tweepy.Cursor(api.search, q = trendName).items(NUM_OF_TWEETS)
		for tweet in tweets:
			new_tweet_object = Tweet(trendName, tweet.text.translate(non_bmp_map))
			print("Pre-scrub:\n" + new_tweet_object.text + "\n")
			scrub_tweet(new_tweet_object)
			print("Post-scrub:\n" + new_tweet_object.text + "\n")
			tweets_to_analyze.add(new_tweet_object)
	return tweets_to_analyze

def main():
	'''
	while True:
		#Rate limit status
		RateLimitStatus()
		#Check rate limit
		CheckLimit()
		#IF it's fine, dump tweets
		DumpTweets()
		#Rate limit status
		RateLimitStatus()
		#wait 24 hours
		TimeDelay(DAILY_TIME)
	'''
	#Rate limit status
	rate_limit_status()
	#Check rate limit
	check_limit()
	#Pull tweets
	serialized_tweets = pull_tweets()
	#Dump tweets
	dump_tweets(serialized_tweets)
	#Rate limit status
	rate_limit_status()
	#wait 24 hours

if __name__ == "__main__":
	main()