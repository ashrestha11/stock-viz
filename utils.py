import re


def remove_emoji(string):
    emoji_pattern = re.compile("["
                           u"\U0001F600-\U0001F64F"  # emoticons
                           u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                           u"\U0001F680-\U0001F6FF"  # transport & map symbols
                           u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                           u"\U00002702-\U000027B0"
                           u"\U000024C2-\U0001F251"
                           "]+", flags=re.UNICODE)
    return emoji_pattern.sub(r'', string)

def rm_characters(string):
    return re.sub('[^A-Za-z0-9]+', '', string)


def extract_symbols(text):
    exlcude = ['THE', 'FLY', 'API', 'FREE', 'NEW','DD', 'BUY', 'PUT',
     'YOLO', 'WSB', 'BETS', 'PAID', 'LOSS', 'GAIN', 'PORN', 'HEAR', 'OUT', 'MOON'] # whitelist
    # + stop words
    
    pre_symbols = [rm_characters(i) for i in remove_emoji(text).split() 
                            if '$' in i 
                            or (len(i) == 3 
                            or len(i) == 4) 
                            and i == i.upper()]

    symbols = [i.upper() for i in pre_symbols if any(e.isdigit() for e in i) == False
                            and any(n in i for n in exlcude) == False
                            and len(i) >= 2]
   
    return list(set(symbols)) # removes duplicates

# import sqlite3
# import pandas as pd

# DB_URI = 'database/memes.db'

# conn = sqlite3.connect(DB_URI)
# conn.row_factory = sqlite3.Row
# cur = conn.cursor()
# cur.execute('select * from reddit;')
# r = [dict(row) for row in cur.fetchall()]
# df = pd.DataFrame(r)
# df['timestamp']= pd.to_datetime(df['timestamp'])
# df.set_index('timestamp', inplace=True)
# c = df.groupby(by=[df.symbol]).resample('1H')['symbol'].count()
# print(c)