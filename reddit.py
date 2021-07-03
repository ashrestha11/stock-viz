import os
import praw
from dotenv import load_dotenv
import pandas as pd
from datetime import datetime
import pytz
from extractor import extract_symbols
import nltk
nltk.download('vader_lexicon')
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from praw.models import MoreComments
import gspread
import time
from gspread.exceptions import APIError
import argparse

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
sid = SentimentIntensityAnalyzer()
tz = pytz.timezone('America/Los_Angeles')

def fetch_posts(subname:str):

    for submission in reddit.subreddit(subname).stream.submissions():
        infos = {}
        infos['id'] = submission.id
        infos['title'] = submission.title
        infos['timestamp'] = datetime.fromtimestamp(submission.created_utc, tz).isoformat()
        infos['upvotes'] = submission.upvote_ratio
        comments = submission.comments.list()
        infos['comments'] = len(comments)
        infos['subreddit'] = submission.subreddit.display_name

        # sentiment scores
        scores = []
        for comment in comments:
            if isinstance(comment, MoreComments):
                continue
            comment_sentiment = sid.polarity_scores(comment.body)
            scores.append(comment_sentiment['compound'])

        # # avg for the post
        if len(comments) > 0:
            avg_sentiment = sum(scores) / len(comments)
        else:
            avg_sentiment = sid.polarity_scores(submission.selftext)['compound']
        infos['polarity'] = avg_sentiment
        # joining symbols from title & body
        infos['symbols'] = extract_symbols(submission.title) + extract_symbols(submission.selftext)

        yield infos

# TO DO:
#   connection error when it just waits for new posts
#   avoid the api limit

def insert_gsheet(config_path,sheetname, subreddits):

    gc = gspread.service_account(filename=config_path)
    sh = gc.open(sheetname)
    worksheet = sh.sheet1

    for post in fetch_posts(subname=subreddits):

        len_symbols = len(post['symbols'])
        if len_symbols == 1:
            post['symbols'] = post['symbols'][0]
        elif len_symbols > 1:
            post['symbols'] = str(post['symbols'])
     
        values = [v for v in post.values() if len(post['symbols']) != 0] # skip if empty
        print(values)

        try:
            worksheet.append_row(values)  # need to batch load
        except APIError as e:
            print(e)
            continue

        time.sleep(4)

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("-g","--gsconfig", type=str,
                        help="config path for gsheeta api")
    parser.add_argument("-n", "--sheetname", type=str,
                        help='gsheet filename')
    parser.add_argument("-s", "--subreddits", type=str,
                        help="""subreddits (ex. 'python+all')""")
    
    args = parser.parse_args()

    while True:
        insert_gsheet(config_path=args.gsconfig, sheetname=args.sheetname,
                  subreddits=args.subreddits)
