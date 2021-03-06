# stock-viz

Analytics tool to analysis trend and sentiment scores of "Meme" stock mentioned in popular subreddit posts to find insights next potiental big price actions. Many retail traders are using Reddit groups to find stocks that could return high rate of return in short amount of time. Even the financial news are using subreddit, such as Wallstreetbets, to reference most mentioned "meme" stocks.

[Dashboard Demo 👀📈](https://datastudio.google.com/reporting/d6c5a543-0735-45e4-a75c-9869c8736d0a)

Some examples are:
- https://finance.yahoo.com/news/beyond-gamestop-reddit-wallstreetbets-now-142205449.html
- https://markets.businessinsider.com/news/stocks/reddit-meme-stocks-wall-street-bets-top-ten-talking-about-2021-7
- https://investorplace.com/2021/07/7-reddit-penny-stocks-about-to-explode/

### Architecture

The core architecture idea:
  - Reddit API Wrapper --> extractor scripts --> load the data to a data source (google sheets)
  - Simple ETL ideas that checks for new posts 24 hours
 
### How to run:
1. Get Google Sheets and Reddit API credientials
2. copy Reddit API creds to .env file in project's root dir
3. Move Google Sheets API to project's root dir

- change the export variables in ```runner.sh ``` to your variables 
- give permission to the dir
- then:  
``` ./runner.sh ```
### In process:
- Using Deep learning model to extract symbols instead of using an algothrim
  - Better extracting probablity and no need to use whitelists
- Add a config file to dynamically change subreddits and whitelists
