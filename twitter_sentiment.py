#!/usr/bin/env python
"""
twitter_sentiment.py

This script uses Twitter's free API (via Tweepy) to fetch recent tweets containing a specific keyword
(e.g., a cryptocurrency like "bitcoin"), performs sentiment analysis on each tweet using NLTK's VADER,
and prints the results.

Dependencies:
  - tweepy
  - nltk
  - python-dotenv (optional, if you prefer using a .env file for credentials)

Usage:
1. Create a Twitter developer account and obtain your API credentials (API Key, API Secret, and Bearer Token).
2. Set your credentials in this file or as environment variables.
3. Install the required packages:
     pip install tweepy nltk python-dotenv
4. Run the script:
     python twitter_sentiment.py
"""

import os
import tweepy
import datetime
from nltk.sentiment import SentimentIntensityAnalyzer
import nltk

# Download VADER lexicon (if not already present)
nltk.download('vader_lexicon')

# Twitter API credentials
# Replace these with your actual credentials or set them as environment variables
# Access token: 1121762105848365057-o7NyITiR3qS2TTWZ6vrHCpmkrTisvb
TWITTER_API_KEY = os.getenv("i8rs3xO7UQkP1FiXv5WAJBXWn", "i8rs3xO7UQkP1FiXv5WAJBXWn")
TWITTER_API_SECRET = os.getenv("4nCyTPGrNx17tCTTngAPUwm4vH7pLx9NAVB47PoNDafLrFOTW9", "4nCyTPGrNx17tCTTngAPUwm4vH7pLx9NAVB47PoNDafLrFOTW9")
TWITTER_BEARER_TOKEN = os.getenv("AAAAAAAAAAAAAAAAAAAAAIk3zgEAAAAAYBbcP2cfLc%2BPLFzigEAnnCIFS5A%3Dw9QhCWcE4xHPL9g0vsCIJGrm40jGdpjgBiRa3IvPlItcfNwGTE", "AAAAAAAAAAAAAAAAAAAAAIk3zgEAAAAAYBbcP2cfLc%2BPLFzigEAnnCIFS5A%3Dw9QhCWcE4xHPL9g0vsCIJGrm40jGdpjgBiRa3IvPlItcfNwGTE")

def fetch_tweets(keyword, max_results=100):
    """
    Fetch recent tweets matching the keyword using Twitter's API v2.
    
    Parameters:
      keyword (str): The search keyword.
      max_results (int): Maximum number of tweets to fetch (up to 100).
      
    Returns:
      List of tweet objects.
    """
    # Initialize the Tweepy client with your bearer token
    client = tweepy.Client(bearer_token=TWITTER_BEARER_TOKEN)
    # Build a query: search for keyword, exclude retweets, and only in English
    query = f"{keyword} -is:retweet lang:en"
    tweets_response = client.search_recent_tweets(query=query, max_results=max_results, tweet_fields=["created_at", "text"])
    if tweets_response.data is None:
        return []
    return tweets_response.data

def analyze_sentiment(text):
    """
    Analyze the sentiment of the provided text using VADER.
    
    Parameters:
      text (str): Text to analyze.
      
    Returns:
      Dictionary with sentiment scores (neg, neu, pos, compound).
    """
    sia = SentimentIntensityAnalyzer()
    return sia.polarity_scores(text)

def main():
    # Define the keyword for which to search tweets (e.g., "bitcoin")
    keyword = "bitcoin"
    print(f"Fetching tweets for keyword: {keyword}\n")
    
    tweets = fetch_tweets(keyword)
    print(f"Found {len(tweets)} tweets. Analyzing sentiment...\n")
    
    # Iterate through the tweets and analyze sentiment
    for tweet in tweets:
        text = tweet.text
        sentiment = analyze_sentiment(text)
        # Using tweet.created_at if available; otherwise, show 'N/A'
        created_at = tweet.created_at if tweet.created_at else "N/A"
        print(f"Tweet: {text}")
        print(f"Created At: {created_at}")
        print(f"Sentiment: {sentiment}")
        print("-" * 80)

if __name__ == "__main__":
    main()
