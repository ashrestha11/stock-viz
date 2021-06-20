import streamlit as st
from reddit import fetch_posts
import pandas as pd
from sqlite3 import Connection
import sqlite3

DB_URI = 'database/memes.db'

st.title('Stock Mention')

def get_data():

    conn = sqlite3.connect(DB_URI)
    cur = conn.cursor()
    cur.execute('select * from reddit;')
    r = cur.fetchall()
    df = pd.DataFrame(r)
    #df.iloc[:,1]= df.iloc[:,1].apply(lambda x: str(x.split(',')))

    leng = len(df)

    return df, leng

def load_data():
    posts = fetch_posts('wallstreetbets')
    df = pd.DataFrame(posts)
    return df

data_load_state = st.text('Loading data...')
# Load 10,000 rows of data into the dataframe.
data, leng = get_data()
# Notify the reader that the data was successfully loaded.
data_load_state.text('Loading data...done!')
st.write(leng)
st.write(data)