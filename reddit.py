import os
import praw
import datetime 
import spacy
from dotenv import load_dotenv

load_dotenv()

SEC = os.getenv('CLIENT_SEC')
CLIENT = os.getenv('CLIENT_SEC')
USER_AGENT = os.getenv('USER_AGENT')
username = os.getenv('username')
pw = os.getenv('pw')

reddit = praw.Reddit(client_id=CLIENT,
                    client_secret=SEC,
                    user_agent=USER_AGENT,
                    username=username,
                    password=pw)

def extract_symbols(text):
    nlp = spacy.load('en_core_web_sm')
    doc = nlp(text)

    orgs = []
    for entity in doc.ents:
        if entity.label_ == 'ORG':
            orgs.append(entity.text)
    
    return orgs

def fetch_posts(subname):

    for submission in reddit.subreddit(subname).new(limit=10):
        infos = {}
        stock = extract_symbols(submission.selftext)

        if len(stock) == 0:
            stock = extract_symbols(submission.title)
    
        infos['id'] = submission.id
        infos['title'] = submission.title
        infos['date_time'] = submission.created_utc
        infos['upvotes'] = submission.score

        print(stock)
        print(infos)
        
        c = submission.comments.list()
        print(len(c))
        # print([i.body for i in c])

fetch_posts('wallstreetbets')