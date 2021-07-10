"""
Module that contains functions to
remove non-symbols
"""
from nltk.corpus import stopwords

def rm_words():
    """
    exclude words + stopwords
    """
    exclude = ['THE', 'FLY', 'API', 'FREE', 'NEW','DD', 'BUY', 'PUT',
        'YOLO', 'WSB', 'WTF', 'BETS', 'PAID', 'LOSS', 'GAIN', 'PORN',
        'HEAR', 'OUT', 'MOON', 'BABY', 'ATH', 'ITM', 'IPO', 'US', 'OTM',
        'LETS', 'BOOM', 'SOME', 'LUCK', 'AND', 'FAQ', 'THIS', 'THAT', 'CEO', 'PART',
        'IM', 'PL', 'PUTS', 'CALLS', 'DIP', 'LOVE'] # whitelist

    stop_words = stopwords.words('english')
    whitelists = exclude + [x.upper() for x in stop_words if len(x) <= 4]

    return whitelists

def remove_whitelist(symbols:list):
    """
    find and remove words that are not
    symbols
    """
    tmp = symbols.copy()
    for symbol in tmp:
        if symbol in rm_words():
            try:
                while True:
                    print("removed symbol: {}".format(symbol))
                    symbols.remove(symbol)
            except ValueError:
                pass
    return list(filter(None,symbols))
