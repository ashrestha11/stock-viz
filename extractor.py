"""
Clean texts, extracts symbols and
checks for non-symbols to remove
"""
import re
from utils.whitelist import remove_whitelist

def remove_emoji(string):
    """
    Removes emoji from the string
    """
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
    """
    remove special characters
    """
    return re.sub('[^A-Za-z0-9]+', '', string)

def extract_symbols(text: str):
    """
    Finds words that start with $, capitalized &
    length of 3 or 4 (tickers)

    Filters out words that are not tickers
    """
    pre_symbols = [rm_characters(i)
                    for i in remove_emoji(text).split()
                        if '$' in i
                        or (len(i) == 3
                        or len(i) == 4)
                        and i == i.upper()]
    symbols = [i.upper() for i in pre_symbols
                if any(e.isdigit() for e in i) is False]

    # check the whitelist
    symbols = remove_whitelist(symbols)
    return list(set(symbols)) # removes duplicates
