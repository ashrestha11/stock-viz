import streamlit as st
from reddit import fetch_posts
import pandas as pd

st.title('Stock Mention')

def load_data():
    posts = fetch_posts('wallstreetbets')
    df = pd.DataFrame(posts)
    return df

data_load_state = st.text('Loading data...')
# Load 10,000 rows of data into the dataframe.
data = load_data()
# Notify the reader that the data was successfully loaded.
data_load_state.text('Loading data...done!')

st.write(data)