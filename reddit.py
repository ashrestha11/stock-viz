"""
Main scripts to collect data from subreddits and push it to db
"""

import os
import logging as logger
import argparse
from datetime import datetime
from datetime import timedelta
import time
import gspread
import praw
import nltk
import pytz
import requests
from prawcore.exceptions import PrawcoreException
from google.oauth2 import service_account
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from praw.models import MoreComments
from gspread.exceptions import APIError
from dotenv import load_dotenv
from extractor import extract_symbols

nltk.download('vader_lexicon')


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
    """
    Checks for new posts and calls api to
    get the post from subreddit

    Args:
        subname (str): subredddit names
                        "all+reddit"

    Yields:
        [dict]: line of dict
    """

    for submission in reddit.subreddit(subname).stream.submissions():
        try:
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
            infos['symbols'] = extract_symbols(submission.title) + \
                               extract_symbols(submission.selftext)

            yield infos
        except PrawcoreException as error:
            logger.debug(error)
            continue

def gsheet_auth(config_path: str, sheetname: str):
    """
    auth google api
    """

    scope = ['https://spreadsheets.google.com/feeds',
    'https://www.googleapis.com/auth/drive']
    creds = service_account.Credentials.from_service_account_file(config_path)

    scoped_credentials = creds.with_scopes(scope)
    client = gspread.authorize(scoped_credentials)

    sheetname = client.open(sheetname)
    wrksht = sheetname.sheet1

    return wrksht

def insert_gsheet(config_path:str,sheetname:str, subreddits:str):
    """
    Main function to collect & insert it to gsheet
    Args:
        config_path (str): gcloud json key
        sheetname (str): gsheet sheetname
        subreddits (str): subreddits
    """

    # auth
    wrksht = gsheet_auth(config_path, sheetname)
    gettime = datetime.now(tz=tz)

    while True:
        for post in fetch_posts(subname=subreddits):

            if datetime.now(tz=tz) > gettime + timedelta(minutes=20):

                logger.info("Reconnected at %s", datetime.now(tz=tz))
                wrksht = gsheet_auth(config_path, sheetname)
                gettime = datetime.now(tz=tz)
            else:
                logger.info("No Need for restart [%s]", datetime.now(tz=tz))

            len_symbols = len(post['symbols'])
            if len_symbols == 1:
                post['symbols'] = post['symbols'][0]
            elif len_symbols > 1:
                post['symbols'] = str(post['symbols'])

            values = [v for v in post.values() if len(post['symbols']) != 0] # skip if empty
            logger.info(values)

            try:
                wrksht.append_row(values)
                time.sleep(1)
            # catches gspread specific execeptions
            except APIError as error:
                logger.debug(error)
                time.sleep(105)
                wrksht.append_row(values)
                continue
            # general exceptions
            except requests.exceptions.ConnectionError as error:
                logger.debug(error)
                time.sleep(.01)

                wrksht = gsheet_auth(config_path, sheetname)
                wrksht.append_row(values)
                continue


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
