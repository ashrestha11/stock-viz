import os
import praw
from dotenv import load_dotenv
import pandas as pd
from datetime import datetime
import pytz
from utils import extract_symbols
import sqlite3

load_dotenv()

SEC = os.getenv('CLIENT_SEC')
CLIENT = os.getenv('CLIENT')
USER_AGENT = os.getenv('USER_AGENT')
username = os.getenv('username')
pw = os.getenv('pw')

reddit = praw.Reddit(client_id=CLIENT,
                    client_secret=SEC,
                    user_agent=USER_AGENT,
                    username=username,
                    password=pw)


def fetch_posts(subname):

    tz = pytz.timezone('America/Los_Angeles')

    connection = sqlite3.connect('database/memes.db')
    cursor = connection.cursor()

    for submission in reddit.subreddit(subname).stream.submissions():
        infos = {}
        infos['id'] = submission.id
        infos['title'] = submission.title
        infos['timestamp'] = datetime.fromtimestamp(submission.created_utc, tz)
        infos['upvotes'] = submission.score
        c = submission.comments.list()
        infos['comments'] = len(c)

        symbols = extract_symbols(submission.title)

        if len(symbols) == 1:

            infos['symbol'] = symbols[0]
            cursor.execute("""INSERT INTO reddit(id, symbol, title, timestamp, upvotes, comments) VALUES (:id, :symbol, :title, :timestamp, :upvotes, :comments);""", infos)
        elif len(symbols) > 1:
            for symbol in symbols:
                infos['symbol'] = symbol
                cursor.execute("""INSERT INTO reddit(id, symbol, title, timestamp, upvotes, comments) VALUES (:id, :symbol, :title, :timestamp, :upvotes, :comments);""", infos)
        else:
            print('No symbol found')

        connection.commit()

if __name__ == '__main__':
    fetch_posts('wallstreetbets')
