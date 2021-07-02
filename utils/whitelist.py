from nltk.corpus import stopwords


def rm_words():
    exclude = ['THE', 'FLY', 'API', 'FREE', 'NEW','DD', 'BUY', 'PUT',
        'YOLO', 'WSB', 'WTF', 'BETS', 'PAID', 'LOSS', 'GAIN', 'PORN', 
        'HEAR', 'OUT', 'MOON', 'BABY', 'ATH', 'ITM', 'IPO', 'US', 'OTM', 
        'LETS', 'BOOM', 'SOME', 'LUCK', 'AND', 'FAQ', 'THIS', 'THAT', 'CEO', 'PART',
        'IM', 'PL', 'PUTS', 'CALLS'] # whitelist

    stop_words = stopwords.words('english')
    whitelists = exclude + [x.upper() for x in stop_words if len(x) <= 4]

    return whitelists