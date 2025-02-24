#!/usr/bin/env python
"""
data_aggregator_with_db.py

This script connects to the Reddit API using PRAW to query the latest posts from the r/CryptoCurrency subreddit,
extracts key metrics (title, score, number of comments, creation time), and analyzes the sentiment of each post’s title
using NLTK's VADER sentiment analyzer. The aggregated data is then saved to a local SQLite database.
The job is scheduled to run every 6 hours.

Dependencies:
  - praw
  - nltk
  - schedule

Install dependencies via:
  pip install praw nltk schedule

Before running, create a Reddit app at:
  https://old.reddit.com/prefs/apps/
and update the CLIENT_ID, CLIENT_SECRET, and USER_AGENT below.
"""

import praw
import datetime
import nltk
import sqlite3
from nltk.sentiment import SentimentIntensityAnalyzer
import schedule
import time

# Download VADER lexicon if not already present
nltk.download('vader_lexicon')

# Reddit API credentials (replace with your actual credentials)
CLIENT_ID = "DDa-OMRxG21tMNKBazW2Fw"
CLIENT_SECRET = "_9p7eUHSlXEUvtl7lumi1CXBQa6JAw"
USER_AGENT = "CryptoTrendDashboard by divinedavis"

# Database file name
DB_FILE = "trend_data.db"

def create_database():
    """Create the SQLite database and the trend_data table if they do not already exist."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS trend_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            score INTEGER,
            num_comments INTEGER,
            created TEXT,
            sentiment_neg REAL,
            sentiment_neu REAL,
            sentiment_pos REAL,
            sentiment_compound REAL
        )
    ''')
    conn.commit()
    conn.close()

def insert_trend_data(data):
    """
    Insert a record into the trend_data table.
    
    Parameters:
      data (dict): A dictionary containing the keys:
           title, score, num_comments, created, sentiment (which is another dict with keys 'neg', 'neu', 'pos', 'compound')
    """
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        INSERT INTO trend_data (title, score, num_comments, created, sentiment_neg, sentiment_neu, sentiment_pos, sentiment_compound)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        data["title"],
        data["score"],
        data["num_comments"],
        data["created"].strftime("%Y-%m-%d %H:%M:%S"),
        data["sentiment"]["neg"],
        data["sentiment"]["neu"],
        data["sentiment"]["pos"],
        data["sentiment"]["compound"]
    ))
    conn.commit()
    conn.close()

def aggregate_trend_data():
    """Query the subreddit, analyze posts, and store the data in the database."""
    reddit = praw.Reddit(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        user_agent=USER_AGENT
    )
    subreddit_name = "CryptoCurrency"
    subreddit = reddit.subreddit(subreddit_name)
    posts = subreddit.new(limit=100)

    sia = SentimentIntensityAnalyzer()
    trend_data = []

    for post in posts:
        title = post.title
        score = post.score
        num_comments = post.num_comments
        created = datetime.datetime.utcfromtimestamp(post.created_utc)
        sentiment = sia.polarity_scores(title)

        record = {
            "title": title,
            "score": score,
            "num_comments": num_comments,
            "created": created,
            "sentiment": sentiment
        }
        trend_data.append(record)
        insert_trend_data(record)  # Save each record to the database

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
    # Create the database and table if not exists
    create_database()

    # Schedule the job to run every 6 hours
    schedule.every(6).hours.do(job)
    print("Data aggregator is running. Press Ctrl+C to exit.")

    # Optionally, run the job once immediately
    job()

    # Keep the script running and check for pending scheduled jobs
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute

if __name__ == "__main__":
    main()
