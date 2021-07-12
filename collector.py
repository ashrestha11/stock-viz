"""
Main scripts to collect data from subreddits and push it to db
"""
import os
import logging as logger
import argparse
from datetime import datetime
from datetime import timedelta
from re import sub
import time
import gspread
import praw
import nltk
import pytz
import requests
# from prawcore.exceptions import PrawcoreException
from google.oauth2 import service_account
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from praw.models import MoreComments
from gspread.exceptions import APIError
from dotenv import load_dotenv
from extractor import extract_symbols, process_values

nltk.download('vader_lexicon')

logger.basicConfig(format='%(levelname)s:%(message)s', level=logger.DEBUG)
load_dotenv()

SEC = os.getenv('CLIENT_SEC')
CLIENT = os.getenv('CLIENT')
USER_AGENT = os.getenv('USER_AGENT')
username = os.getenv('username')
pw = os.getenv('pw')

def reddit_client():
    """
    init reddit client
    """
    reddit = praw.Reddit(client_id=CLIENT,
                    client_secret=SEC,
                    user_agent=USER_AGENT,
                    username=username,
                    password=pw)
    return reddit

sid = SentimentIntensityAnalyzer()
tz = pytz.timezone('America/Los_Angeles')
reddit = reddit_client()

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
    for submission in reddit.subreddit(subname).stream.submissions(skip_existing=True):
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
            if submission.selftext is None:
                avg_sentiment = sid.polarity_scores(submission.title)
            else:
                avg_sentiment = sid.polarity_scores(submission.selftext)
            
            infos['sentiment'] = avg_sentiment['compound']
            infos['symbols'] = extract_symbols(submission.title) + \
                               extract_symbols(submission.selftext)

            yield infos
        except requests.exceptions.HTTPError as error:
            logger.debug(error)
            time.sleep(10)
            continue

def gsheet_auth(config_path: str, sheetname: str, worksheet:str):
    """
    auth google api
    """
    scope = ['https://spreadsheets.google.com/feeds',
    'https://www.googleapis.com/auth/drive']
    creds = service_account.Credentials.from_service_account_file(config_path)

    scoped_credentials = creds.with_scopes(scope)
    client = gspread.authorize(scoped_credentials)

    sheetname = client.open(sheetname)
    wrksht = sheetname.worksheet(worksheet)

    return wrksht

def insert_gsheet(config_path:str,sheetname:str, worksheet:str,subreddits:str):
    """
    Main function to collect & insert it to gsheet
    Args:
        config_path (str): gcloud json key
        sheetname (str): gsheet sheetname
        worksheet (str): worksheet name in sheets
        subreddits (str): subreddits
    """
    # auth
    wrksht = gsheet_auth(config_path,sheetname=sheetname,worksheet=worksheet)
    gettime = datetime.now(tz=tz)

    while True:
        for post in fetch_posts(subname=subreddits):

            if datetime.now(tz=tz) > gettime + timedelta(minutes=10):

                logger.info("Reconnected at %s", datetime.now(tz=tz))
                wrksht = gsheet_auth(config_path,sheetname=sheetname,worksheet=worksheet)
                gettime = datetime.now(tz=tz)
            else:
                logger.info("No Need for restart [%s]", datetime.now(tz=tz))
            try:
                process_values(wrksht,post)
                time.sleep(1)
            # catches gspread specific execeptions
            except APIError as error:
                logger.debug(error)
                time.sleep(105)
                process_values(wrksht,post)
                continue
            # general exceptions
            except requests.exceptions.ConnectionError as error:
                logger.debug(error)
                time.sleep(.01)

                wrksht = gsheet_auth(config_path,sheetname=sheetname,worksheet=worksheet)
                process_values(wrksht,post)
                continue

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("-g","--gsconfig", type=str,
                        help="config path for gsheeta api")
    parser.add_argument("-n", "--sheetname", type=str,
                        help='gsheet filename')
    parser.add_argument("-s", "--subreddits", type=str,
                        help="""subreddits (ex. 'python+all')""")
    parser.add_argument("-w", "--worksheet", type=str,
                        help="""worksheet name""")
    args = parser.parse_args()

    insert_gsheet(config_path=args.gsconfig, sheetname=args.sheetname,
                  subreddits=args.subreddits, worksheet=args.worksheet)
