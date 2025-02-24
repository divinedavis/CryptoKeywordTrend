#!/usr/bin/env python
"""
reddit_trend_analysis.py

This script connects to the Reddit API using PRAW to query the latest posts from the r/CryptoCurrency subreddit.
It extracts key metrics (title, score, number of comments, and creation time) and analyzes the sentiment of each post’s title
using NLTK's VADER sentiment analyzer.

Dependencies:
  - praw
  - nltk

To install dependencies, run:
  pip install praw nltk

Before running, ensure you have created a Reddit app at:
  https://old.reddit.com/prefs/apps/
and update the CLIENT_ID, CLIENT_SECRET, and USER_AGENT below.
"""

import praw
import datetime
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer

# Download VADER lexicon if not already present
nltk.download('vader_lexicon')

# Reddit API credentials (replace with your actual credentials)
CLIENT_ID = "DDa-OMRxG21tMNKBazW2Fw"
CLIENT_SECRET = "_9p7eUHSlXEUvtl7lumi1CXBQa6JAw"
USER_AGENT = "CryptoTrendDashboard by divinedavis"

def main():
    # Initialize the Reddit instance using PRAW
    reddit = praw.Reddit(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        user_agent=USER_AGENT
    )

    # Choose the subreddit and number of posts to fetch
    subreddit_name = "CryptoCurrency"
    subreddit = reddit.subreddit(subreddit_name)
    limit_posts = 100  # Adjust the number of posts as needed

    # Fetch posts from the 'new' category (you can also use .hot() or .top())
    posts = subreddit.new(limit=limit_posts)

    # Initialize the sentiment analyzer
    sia = SentimentIntensityAnalyzer()

    # List to store extracted trend data
    trend_data = []

    # Loop through posts and extract data
    for post in posts:
        title = post.title
        score = post.score  # Upvotes minus downvotes
        num_comments = post.num_comments
        created = datetime.datetime.utcfromtimestamp(post.created_utc)

        # Analyze the sentiment of the title using VADER
        sentiment = sia.polarity_scores(title)

        # Append the data for this post to our list
        trend_data.append({
            "title": title,
            "score": score,
            "num_comments": num_comments,
            "created": created,
            "sentiment": sentiment
        })

    # Print out the trend data for review
    for data in trend_data:
        print(f"Title: {data['title']}")
        print(f"Score: {data['score']}, Comments: {data['num_comments']}")
        print(f"Created: {data['created']}")
        print(f"Sentiment: {data['sentiment']}")
        print("-" * 80)

if __name__ == "__main__":
    main()
