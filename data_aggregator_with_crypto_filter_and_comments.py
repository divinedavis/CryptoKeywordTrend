#!/usr/bin/env python
"""
data_aggregator_with_crypto_filter_and_comments.py

This script connects to the Reddit API using PRAW to query the latest posts from the r/CryptoCurrency subreddit,
extracts key metrics (title, score, number of comments, creation time), and analyzes the sentiment of each post’s title
using NLTK's VADER sentiment analyzer. It now checks both the post (title and selftext) and the top comments for mentions
of specific cryptocurrencies based on a predefined keyword list. The aggregated data is saved to a local SQLite database.
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

# Define a list of cryptocurrency keywords (names or symbols in lowercase)
CRYPTO_KEYWORDS = {
    "bitcoin": ["bitcoin", "btc"],
    "ethereum": ["ethereum", "eth"],
    "solana": ["solana", "sol"],
    "dogecoin": ["dogecoin", "doge"],
    "xrp": ["xrp","xrp"]
    # Add more as needed...
}

def identify_crypto_in_text(text):
    """
    Checks the given text for any crypto keyword.
    Returns the crypto name if found, otherwise None.
    """
    text_lower = text.lower()
    for crypto, keywords in CRYPTO_KEYWORDS.items():
        for keyword in keywords:
            if keyword in text_lower:
                return crypto
    return None

def identify_crypto(post):
    """
    Identify which cryptocurrency is mentioned in the post.
    First, check the title and selftext. If not found, check the top few comments.
    Returns the first matching crypto name, or 'Unknown' if none are found.
    """
    # Combine title and selftext (if available)
    text_to_search = post.title
    if hasattr(post, 'selftext') and post.selftext:
        text_to_search += " " + post.selftext
    crypto = identify_crypto_in_text(text_to_search)
    if crypto:
        return crypto

    # If not found in the post content, check top few comments
    post.comments.replace_more(limit=0)
    comments = post.comments.list()
    # Check first 5 comments (or fewer if less available)
    for comment in comments[:5]:
        crypto = identify_crypto_in_text(comment.body)
        if crypto:
            return crypto

    return "Unknown"

def create_database():
    """Create the SQLite database and the trend_data table if they do not already exist."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS trend_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            crypto TEXT,
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
      data (dict): Should contain keys: title, crypto, score, num_comments, created, and sentiment (a dict).
    """
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        INSERT INTO trend_data (title, crypto, score, num_comments, created, sentiment_neg, sentiment_neu, sentiment_pos, sentiment_compound)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        data["title"],
        data["crypto"],
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
    """Query the subreddit, analyze posts (including comments), and store the data in the database."""
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
        # Identify cryptocurrency from post title, selftext, or top comments
        crypto = identify_crypto(post)

        record = {
            "title": title,
            "crypto": crypto,
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
        print(f"Crypto: {data['crypto']}")
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
