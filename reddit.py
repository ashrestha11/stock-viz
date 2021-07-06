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
import logging as logger

logger.basicConfig(format='%(levelname)s:%(message)s', level=logger.DEBUG)
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
#   async requests
# loggers 

def gsheet_auth(config_path: str, sheetname: str):
    gc = gspread.service_account(filename=config_path)
   
    sh = gc.open(sheetname)
    worksheet = sh.sheet1

    return worksheet

def insert_gsheet(config_path,sheetname, subreddits):

    # auth
    ws = gsheet_auth(config_path, sheetname)
    gettime = time.time()

    while True:
        for post in fetch_posts(subname=subreddits):

            len_symbols = len(post['symbols'])
            if len_symbols == 1:
                post['symbols'] = post['symbols'][0]
            elif len_symbols > 1:
                post['symbols'] = str(post['symbols'])
        
            values = [v for v in post.values() if len(post['symbols']) != 0] # skip if empty
            logger.info(values)

            try:
                ws.append_row(values)  # need to batch load
            except APIError as e:
                logger.debug(e)
                time.sleep(60) # if it researches limit

                ws.append_row(values)
                continue

            time.sleep(3)

            if(time.time() - gettime > 60* 59):
                logger.info("Re-Auth at {}".format(time.time()))
                ws = gsheet_auth(config_path,sheetname)
                gettime = time.time()


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("-g","--gsconfig", type=str,
                        help="config path for gsheeta api")
    parser.add_argument("-n", "--sheetname", type=str,
                        help='gsheet filename')
    parser.add_argument("-s", "--subreddits", type=str,
                        help="""subreddits (ex. 'python+all')""")
    
    args = parser.parse_args()

    insert_gsheet(config_path=args.gsconfig, sheetname=args.sheetname,
                  subreddits=args.subreddits)
