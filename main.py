import streamlit as st
from reddit import fetch_posts
import pandas as pd
from sqlite3 import Connection
import sqlite3
from datetime import datetime

DB_URI = 'database/memes.db'

st.title('Stock Mention')

def get_data():

    conn = sqlite3.connect(DB_URI)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute('select * from reddit;')
    r = [dict(row) for row in cur.fetchall()]
    df = pd.DataFrame(r)
    df['timestamp']= pd.to_datetime(df['timestamp'])
    df['date'] = df['timestamp'].apply(lambda x: x.strftime('%Y-%m-%d'))

    today_date = datetime.today().strftime('%Y-%m-%d')
    
    leng = df[df['date'] == today_date]['symbol'].value_counts().head(15)

    # leng = df.groupby(by=[df.symbol]).resample('D')['symbol'].count().sort_values()


    counts = len(df)
        
    return df, leng, counts


values = st.select_slider('Date range', options=['1 Hour', ' 1 Day', '3 Day', '1 Week', '3 Weeks', 'Month'])


# Load 10,000 rows of data into the dataframe.
data, leng, counts = get_data()
st.write(counts)

col1, col2  = st.beta_columns([2,2])

with col1 as c:
    st.bar_chart(leng)

with col2:
    st.write(data)


