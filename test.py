import sqlite3
import pandas as pd

# DB_URI = 'database/memes.db'

# conn = sqlite3.connect(DB_URI)
# conn.row_factory = sqlite3.Row
# cur = conn.cursor()
# cur.execute('select * from reddit;')
# r = [dict(row) for row in cur.fetchall()]
# df = pd.DataFrame(r)
# df['timestamp']= pd.to_datetime(df['timestamp'])
# # df.set_index('timestamp', inplace=True)
# df['timestamp'] = df['timestamp'].apply(lambda x: x.strftime('%Y-%m-%d'))
# # c = df.groupby(by=[df.symbol]).resample('1H')['symbol'].count()
# # print(c)

# from datetime import datetime
# import datetime as dt
# from dateutil.relativedelta import relativedelta
# d = datetime.today()

# week = (d - dt.timedelta(days=7)).strftime('%Y-%m-%d')
# print(d)

# print(d - relativedelta(months=1))
a = [1,4,6,7]

print(sum(a)/len(a))