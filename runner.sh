#!/bin/bash

until ./viz/bin/python3 ./app/collector.py -config 'sheets_config.json' -n 'StockMentions' -s 'wallstreetbets+options+pennystocks' -w 'Raw'
do
    echo "Restarting"
    sleep 10
done