'''
This script should pull earnings dates for a single ticker and then pull post-market prices at 
different times and export it as a csv so it can be copied into a google sheets for analysis.
Google sheets: https://docs.google.com/spreadsheets/d/1UxmLRIjj0FW-c8tXj40IWlSjulzNBA1r07jE0qD6QW8/edit?usp=sharing
'''
__author__ = "Ethan Chang"
__email__ = "ethanchang34@yahoo.com"

import datetime
from datetime import timezone
import pytz
import pandas as pd
import time
import os
import sys
import json

import yfinance as yf
from alpaca.data import StockHistoricalDataClient, TimeFrame, StockBarsRequest


# declare ticker
ticker = "TSLA"

# get Alpaca environment variables
API_KEY = os.getenv('APCA_API_KEY_ID')
SECRET_KEY = os.getenv('APCA_API_SECRET_KEY')

# check for missing alpaca environment variables
if API_KEY is None or SECRET_KEY is None:
    print('[ ERROR ] Environment variables ALPACA_API_KEY_ID or ALPACA_SECRET_KEY not found.')
    print('[ INFO ] Exiting...')
    quit()

# create Alpaca clients
stock_client = StockHistoricalDataClient(API_KEY, SECRET_KEY)

# create empty dataframe to populate and export as csv at the end
data = {
    'Date': [],
    '4:00PM': [],
    '4:01PM': [],
    '4:05PM': [],
    '4:30PM': [],
    '5:00PM': [],
    '5:30PM': [],
    '6:00PM': [],
    '6:30PM': [],
    '7:00PM': []
}
earnings_df = pd.DataFrame(data)

# get earnings dates
today = datetime.datetime.now(tz=timezone.utc)
df = yf.Ticker(ticker)
earnings_dates = df.get_earnings_dates(limit=28).index

for date in earnings_dates:
    # convert Timestamp to datetime and set to 4PM
    datetime_obj = date.to_pydatetime().replace(hour=16, minute = 0, second = 0)
    
    new_row = []
    # only grab dates in the past
    if datetime_obj < today:
        new_row.append(datetime_obj)

        request_params = StockBarsRequest(symbol_or_symbols=ticker, start=datetime_obj, end=datetime_obj, timeframe=TimeFrame.Minute)
        price = stock_client.get_stock_bars(request_params)[ticker][0]
        new_row.append(price.close)
        # print(datetime_obj, price.close, price.timestamp)

        newtime = datetime_obj + datetime.timedelta(minutes=1)
        request_params = StockBarsRequest(symbol_or_symbols=ticker, start=newtime, end=newtime, timeframe=TimeFrame.Minute)
        price = stock_client.get_stock_bars(request_params)[ticker][0]
        new_row.append(price.close)

        newtime = datetime_obj + datetime.timedelta(minutes=5)
        request_params = StockBarsRequest(symbol_or_symbols=ticker, start=newtime, end=newtime, timeframe=TimeFrame.Minute)
        price = stock_client.get_stock_bars(request_params)[ticker][0]
        new_row.append(price.close)

        newtime = datetime_obj + datetime.timedelta(minutes=30)
        request_params = StockBarsRequest(symbol_or_symbols=ticker, start=newtime, end=newtime, timeframe=TimeFrame.Minute)
        price = stock_client.get_stock_bars(request_params)[ticker][0]
        new_row.append(price.close)

        newtime = datetime_obj + datetime.timedelta(hours=1)
        request_params = StockBarsRequest(symbol_or_symbols=ticker, start=newtime, end=newtime, timeframe=TimeFrame.Minute)
        price = stock_client.get_stock_bars(request_params)[ticker][0]
        new_row.append(price.close)

        newtime = datetime_obj + datetime.timedelta(hours=1, minutes=30)
        request_params = StockBarsRequest(symbol_or_symbols=ticker, start=newtime, end=newtime, timeframe=TimeFrame.Minute)
        price = stock_client.get_stock_bars(request_params)[ticker][0]
        new_row.append(price.close)

        newtime = datetime_obj + datetime.timedelta(hours=2)
        request_params = StockBarsRequest(symbol_or_symbols=ticker, start=newtime, end=newtime, timeframe=TimeFrame.Minute)
        price = stock_client.get_stock_bars(request_params)[ticker][0]
        new_row.append(price.close)

        newtime = datetime_obj + datetime.timedelta(hours=2, minutes=30)
        request_params = StockBarsRequest(symbol_or_symbols=ticker, start=newtime, end=newtime, timeframe=TimeFrame.Minute)
        price = stock_client.get_stock_bars(request_params)[ticker][0]
        new_row.append(price.close)

        newtime = datetime_obj + datetime.timedelta(hours=3)
        request_params = StockBarsRequest(symbol_or_symbols=ticker, start=newtime, end=newtime, timeframe=TimeFrame.Minute)
        price = stock_client.get_stock_bars(request_params)[ticker][0]
        new_row.append(price.close)

        print(new_row)


# datetime_obj = datetime.datetime(2023, 8, 7, 19, 45, 0, 0, tzinfo=timezone.utc)
# request_params = StockBarsRequest(symbol_or_symbols=ticker, start=datetime_obj, end=datetime_obj, timeframe=TimeFrame.Minute)
# response = stock_client.get_stock_bars(request_params)[ticker][0].close
# print(response)


# start_dt = datetime(2023, 1, 27, 14, 40, 0, 0, tzinfo=timezone.utc) # 2023/01/27 14:40 UTC
# end_dt = datetime(2023, 1, 27, 14, 42, 0, 0, tzinfo=timezone.utc) # 2023/01/27 14:42 UTC

# ------------------------------------------------------------------------------
# Example of getting alpaca data (need changes to minutes and `looping list date)
# ------------------------------------------------------------------------------
# start_dt = get_last_weekday()
#     end_dt = start_dt + datetime.timedelta(days=1)
#     print("[ INFO ] Fetching previous day bar for", ", ".join(tickers))
#     request_params = StockBarsRequest(symbol_or_symbols=tickers, start=start_dt, end=end_dt, timeframe=TimeFrame.Day)
#     previous_day_bar = stock_client.get_stock_bars(request_params)
#     # print('Previous day bar:', previous_day_bar)
