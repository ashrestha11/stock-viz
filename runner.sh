#!/bin/bash

export ENV="./viz/bin/python3" # your python env w/ all package
export GSHEET_CONFIG="sheets_config.json" # your google sheets api creds
export SHEET_NAME="StockMentions"
export SUBREDDITS="wallstreetbets+options+pennystocks" # which stocks to track
export WORKSHEET="Raw"

until $ENV ./app/collector.py -config $GSHEET_CONFIG -n $SHEET_NAME -s $SUBREDDITS -w $WORKSHEET
do
    echo "Restarting"
    sleep 10
done

