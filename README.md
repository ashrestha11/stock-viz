# stock-viz

This data collection is to test the limits of Google Sheets as a main source of database. The scripts runs 24/7 and collects all the symbols mentioned in subreddit posts.

### Architecture

![arch](./img/arch.png)


### data collection:

1. collect the raw data from social media (posts, date, title, comments, upvote)
2. clean the title and extract symbols on certain conditions 
3. get the sentiment score

## Deployment
1. Google cloud functions (to-do)

### Data Cleaning
1. Raw collection -> Timestamp, symbols, count

### Dashboard 
1. Data Studio
