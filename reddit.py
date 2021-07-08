import os
import praw
from dotenv import load_dotenv
from datetime import datetime
from datetime import timedelta
from prawcore.exceptions import PrawcoreException
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
from google.oauth2 import service_account

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
            infos['symbols'] = extract_symbols(submission.title) + extract_symbols(submission.selftext)

            yield infos
        except PrawcoreException as e:
            logger.log(e)

def gsheet_auth(config_path: str, sheetname: str):
  
    scope = ['https://spreadsheets.google.com/feeds',
    'https://www.googleapis.com/auth/drive']
    creds = service_account.Credentials.from_service_account_file(config_path)

    scoped_credentials = creds.with_scopes(scope)
    client = gspread.authorize(scoped_credentials)

    sh = client.open(sheetname)
    ws = sh.sheet1

    return ws

def insert_gsheet(config_path,sheetname, subreddits):

    # auth
    ws = gsheet_auth(config_path, sheetname)
    gettime = datetime.now(tz=tz)

    while True:
        for post in fetch_posts(subname=subreddits):

            # check the timedelta right away
            if datetime.now(tz=tz) > gettime + timedelta(minutes=20):
                logger.info("Reconnected at {}".format(datetime.now()))

                ws = gsheet_auth(config_path, sheetname)
                gettime = datetime.now(tz=tz)
            else:
                logger.info(f"No Need for restart [{datetime.now(tz=tz)}]")

            len_symbols = len(post['symbols'])
            if len_symbols == 1:
                post['symbols'] = post['symbols'][0]
            elif len_symbols > 1:
                post['symbols'] = str(post['symbols'])
        
            values = [v for v in post.values() if len(post['symbols']) != 0] # skip if empty
            logger.info(values)

            try:
                ws.append_row(values)
            
            except APIError as e:
                time.sleep(101)

                ws.append_row(values)
                continue
            except Exception as e:
                logger.debug(e)
                time.sleep(.01) 

                ws = gsheet_auth(config_path, sheetname)
                ws.append_row(values)
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
