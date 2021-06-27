import pandas as pd
import sqlite3
from datetime import datetime
import datetime as dt
from dateutil.relativedelta import relativedelta


class Metrics:
    def __init__(self, uri, config=None):
        self.DB_URI = uri
        self.config = None
        self.conn = sqlite3.connect(self.DB_URI)
        self.conn.row_factory = sqlite3.Row
        self.cur = self.conn.cursor()
    
    def _raw_data(self):
        self.cur.execute('select * from reddit2;')
        r = [dict(row) for row in self.cur.fetchall()]

        return pd.DataFrame(r)

    def counts(self, period):

        df = self._raw_data()
        df['timestamp']= pd.to_datetime(df['timestamp'])
        df['date'] = df['timestamp'].apply(lambda x: x.strftime('%Y-%m-%d'))

        today = datetime.today()
    
        if period == '1 Day':
            time = today.strftime('%Y-%m-%d')
        elif period == '1 Week':
            time = (today - dt.timedelta(days=7)).strftime('%Y-%m-%d')
        elif period == '1 Month':
            time = (today - relativedelta(months=1)).strftime('%Y-%m-%d')

        counts = df[df['date'] >= time]['symbol'].value_counts().head(15)

        symbols = [symbol for symbol in counts.index]
        print(df.columns)
        self.chart_sentiment(df, symbols, time)

        return counts

    @staticmethod
    def chart_sentiment(df, symbols, time):

        new_df = df[df['date'] >= time]
        period_df = new_df[new_df['symbol'].isin(symbols)]
        d_sentiment = period_df[['symbol', 'date', 'polarity']].groupby(by=['symbol', 'date'])['polarity'].mean()

        return d_sentiment
    
    def price_action(self):
        pass

m = Metrics(uri= 'database/memes.db')

c = m.counts(period='1 Week')