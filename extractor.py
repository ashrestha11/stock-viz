import re
from nltk.util import pr
from utils.whitelist import rm_words


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
    return re.sub('[^A-Za-z0-9]+', '', string)


def extract_symbols(text: str):
    """
    Finds words that start with $, capitalized &
    length of 3 or 4 (tickers)

    Filters out words that are not tickers
    """
    
    pre_symbols = [rm_characters(i) for i in remove_emoji(text).split() 
                            if '$' in i 
                            or (len(i) == 3 
                            or len(i) == 4) 
                            and i == i.upper()]

    symbols = [i.upper() for i in pre_symbols if any(e.isdigit() for e in i) == False]

    # check the whitelist
    for idx, symbol in enumerate(symbols):
        if symbol in rm_words():
            print("removed symbol: {}".format(symbols[idx]))
            symbols.pop(idx)
            continue
   
    return list(set(symbols)) # removes duplicates

def _handle_delays():
    pass


def parse_symbols(line: dict):
    """
    Need list of each row in list
    """

    symbols = line['symbols']

    if len(symbols) > 1:
        tmp_dict = line
        rows = []
        for symbol in symbols:
            tmp_dict['symbol'] = symbol
            row = [r for r in tmp_dict]
            rows.append(row)
        
        return rows 
    elif len(symbols) == 1:
        line["symbols"] = line["symbols"][0]

        return [l for l in line]
    else:
        return

