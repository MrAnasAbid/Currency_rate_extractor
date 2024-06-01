import tweepy
import os
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

# Retrieve API keys and access tokens from environment variables
consumer_key = os.getenv('API_KEY')
consumer_secret = os.getenv('API_SECRET_KEY')
access_token = os.getenv('ACCESS_TOKEN')
access_token_secret = os.getenv('ACCESS_TOKEN_SECRET')

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth)

# Get the 10 most recent tweets from your timeline
public_tweets = api.home_timeline(screen_name='@elonmusk', count=10)

print('10 most recent tweets from @elonmusk:')
for tweet in public_tweets:
    print(tweet.text)
    print('------------------------------------')