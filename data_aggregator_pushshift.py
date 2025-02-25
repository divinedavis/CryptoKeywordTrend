#!/usr/bin/env python
"""
data_aggregator_pushshift.py

This script uses the Pushshift API to fetch historical Reddit posts from the r/CryptoCurrency subreddit
for a specified historical period (set here to January 2024). The posts are retrieved in daily chunks and
saved to a local SQLite database.

Dependencies:
  - requests
  - sqlite3 (built-in)
  - datetime (built-in)
  - time (built-in)

Usage:
  python data_aggregator_pushshift.py
"""

import requests
import sqlite3
import datetime
import time

DB_FILE = "trend_data.db"

def create_database():
    """Create the SQLite database and the trend_data table if it does not already exist."""
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
            sentiment_compound REAL,
            sentiment_neg REAL,
            sentiment_neu REAL,
            sentiment_pos REAL
        )
    ''')
    conn.commit()
    conn.close()

def insert_trend_data(data):
    """
    Insert a record into the trend_data table.
    
    Parameters:
      data (dict): Dictionary with keys: title, crypto, score, num_comments, created,
                   sentiment_compound, sentiment_neg, sentiment_neu, sentiment_pos.
    """
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        INSERT INTO trend_data 
        (title, crypto, score, num_comments, created, sentiment_compound, sentiment_neg, sentiment_neu, sentiment_pos)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        data["title"],
        data["crypto"],
        data["score"],
        data["num_comments"],
        data["created"].strftime("%Y-%m-%d %H:%M:%S"),
        data["sentiment_compound"],
        data["sentiment_neg"],
        data["sentiment_neu"],
        data["sentiment_pos"]
    ))
    conn.commit()
    conn.close()

def fetch_pushshift_data(subreddit, after, before, size=100, retries=3, retry_delay=5):
    """
    Fetch posts from Pushshift API with a retry mechanism and additional debug logging.
    
    Parameters:
      subreddit (str): Subreddit name.
      after (int): Epoch timestamp to start from.
      before (int): Epoch timestamp to end at.
      size (int): Number of posts to retrieve per request.
      retries (int): Number of retries if a non-200 status is encountered.
      retry_delay (int): Seconds to wait between retries.
      
    Returns:
      List of posts.
    """
    url = "https://api.pushshift.io/reddit/search/submission/"
    params = {
        "subreddit": subreddit,
        "after": after,
        "before": before,
        "size": size,
        "sort": "asc"
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) CryptoDataAggregator/1.0"
    }
    
    attempt = 0
    while attempt < retries:
        response = requests.get(url, params=params, headers=headers)
        if response.status_code == 200:
            return response.json().get("data", [])
        else:
            print(f"Error fetching data: {response.status_code} for interval {datetime.datetime.fromtimestamp(after)} to {datetime.datetime.fromtimestamp(before)}")
            print("Response text:", response.text)
            attempt += 1
            print(f"Retrying in {retry_delay} seconds... (Attempt {attempt} of {retries})")
            time.sleep(retry_delay)
    return []

def main():
    create_database()
    
    # Define the date range for historical data. For testing, we use January 2024.
    start_date = datetime.datetime(2024, 1, 1)
    end_date = datetime.datetime(2024, 1, 31, 23, 59, 59)
    
    # Convert dates to epoch timestamps
    after_epoch = int(start_date.timestamp())
    before_epoch = int(end_date.timestamp())
    
    subreddit = "CryptoCurrency"
    
    # Iterate through 1-day chunks (86400 seconds)
    chunk_size = 86400  
    current_after = after_epoch
    
    while current_after < before_epoch:
        current_before = current_after + chunk_size
        print(f"Fetching posts from {datetime.datetime.fromtimestamp(current_after)} to {datetime.datetime.fromtimestamp(current_before)}")
        posts = fetch_pushshift_data(subreddit, current_after, current_before, size=100)
        
        if posts:
            for post in posts:
                created = datetime.datetime.fromtimestamp(post["created_utc"])
                data = {
                    "title": post.get("title", ""),
                    "crypto": "bitcoin",  # Update logic as needed for your project
                    "score": post.get("score", 0),
                    "num_comments": post.get("num_comments", 0),
                    "created": created,
                    # Sentiment fields are set to default values; integrate sentiment analysis as desired.
                    "sentiment_compound": 0.0,
                    "sentiment_neg": 0.0,
                    "sentiment_neu": 1.0,
                    "sentiment_pos": 0.0,
                }
                insert_trend_data(data)
        else:
            print("No posts found in this interval.")
        
        current_after = current_before
        # Pause briefly to avoid rate limiting
        time.sleep(1)
        
    print("Data aggregation for the specified period completed.")

if __name__ == "__main__":
    main()
