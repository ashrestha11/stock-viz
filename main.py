import streamlit as st
from reddit import fetch_posts
import pandas as pd
import sqlite3
from datetime import datetime
import datetime as dt
from dateutil.relativedelta import relativedelta

st.set_page_config(layout="wide")

DB_URI = 'database/memes.db'

st.title('Stock Mention')

def get_data(date_range=None):

    conn = sqlite3.connect(DB_URI)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute('select * from reddit2;')
    r = [dict(row) for row in cur.fetchall()]

    df = pd.DataFrame(r)
    df['timestamp']= pd.to_datetime(df['timestamp'])
    df['date'] = df['timestamp'].apply(lambda x: x.strftime('%Y-%m-%d'))

    today = datetime.today()
    
    if date_range == '1 Day':

        day_metrics = df[df['date'] == today.strftime('%Y-%m-%d')]['symbol'].value_counts().head(15)
        return day_metrics

    elif date_range == '1 Week':

        week_ago = (today - dt.timedelta(days=7)).strftime('%Y-%m-%d')
        week_metrics = df[df['date'] >= week_ago]['symbol'].value_counts().head(15)

        return week_metrics
    elif date_range == '1 Month':
        month_ago = (today - relativedelta(months=1)).strftime('%Y-%m-%d')
        m_metrics = df[df['date'] >= month_ago]['symbol'].value_counts().head(15)

        return m_metrics
    else:
        return df, len(df)


values = st.select_slider('Date range', options=['1 Day', '1 Week', '1 Month'])


# Load 10,000 rows of data into the dataframe.
data, counts = get_data()
st.write(counts)

col1, col2  = st.beta_columns([2,2])

with col1 as c:
    st.bar_chart(get_data(date_range=values))

with col2:
    st.write(data)


