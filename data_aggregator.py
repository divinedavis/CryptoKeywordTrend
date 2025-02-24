#!/usr/bin/env python
"""
data_aggregator.py

This script connects to the Reddit API using PRAW to query the latest posts from the r/CryptoCurrency subreddit,
extracts key metrics (title, score, number of comments, and creation time), and analyzes the sentiment of each post’s title
using NLTK's VADER sentiment analyzer. The aggregation job is scheduled to run every 6 hours.

Dependencies:
  - praw
  - nltk
  - schedule

To install dependencies, run:
  pip install praw nltk schedule

Before running, ensure you have created a Reddit app at:
  https://old.reddit.com/prefs/apps/
and update the CLIENT_ID, CLIENT_SECRET, and USER_AGENT below.
"""

import praw
import datetime
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
import schedule
import time

# Download VADER lexicon if not already present
nltk.download('vader_lexicon')

# Reddit API credentials (replace with your actual credentials)
CLIENT_ID = "DDa-OMRxG21tMNKBazW2Fw"
CLIENT_SECRET = "_9p7eUHSlXEUvtl7lumi1CXBQa6JAw"
USER_AGENT = "CryptoTrendDashboard by divinedavis"

def aggregate_trend_data():
    """Query the subreddit and extract trend data including sentiment analysis."""
    reddit = praw.Reddit(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        user_agent=USER_AGENT
    )
    subreddit_name = "CryptoCurrency"
    subreddit = reddit.subreddit(subreddit_name)
    posts = subreddit.new(limit=100)  # You can change to .hot() or .top() as needed

    sia = SentimentIntensityAnalyzer()
    trend_data = []

    for post in posts:
        title = post.title
        score = post.score
        num_comments = post.num_comments
        created = datetime.datetime.utcfromtimestamp(post.created_utc)
        sentiment = sia.polarity_scores(title)

        trend_data.append({
            "title": title,
            "score": score,
            "num_comments": num_comments,
            "created": created,
            "sentiment": sentiment
        })

    # For now, simply print the aggregated data. You can also store it to a file or database.
    print(f"\n--- Aggregated Trend Data ({datetime.datetime.now()}) ---")
    for data in trend_data:
        print(f"Title: {data['title']}")
        print(f"Score: {data['score']}, Comments: {data['num_comments']}")
        print(f"Created: {data['created']}")
        print(f"Sentiment: {data['sentiment']}")
        print("-" * 80)

def job():
    """Job to run the data aggregation."""
    print("\nStarting data aggregation job...")
    aggregate_trend_data()
    print("Data aggregation job completed.\n")

def main():
    # Schedule the job to run every 6 hours
    schedule.every(6).hours.do(job)
    print("Data aggregator is running. Press Ctrl+C to exit.")

    # Optionally, run once immediately
    job()

    # Keep the script running and check for pending scheduled jobs
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute

if __name__ == "__main__":
    main()
