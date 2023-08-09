'''
This script should pull earnings dates for a single ticker and then pull post-market prices at 
different times and export it as a csv so it can be copied into a google sheets for analysis.
Google sheets: https://docs.google.com/spreadsheets/d/1UxmLRIjj0FW-c8tXj40IWlSjulzNBA1r07jE0qD6QW8/edit?usp=sharing
'''
__author__ = "Ethan Chang"
__email__ = "ethanchang34@yahoo.com"

import datetime
from datetime import timezone
from typing import List
import pandas as pd
import os
import sys

import yfinance as yf
from alpaca.data import StockHistoricalDataClient, TimeFrame, StockBarsRequest


def main():
    # TODO: Just pull date as for first column to clean up datetime look

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
    earnings_dates = df.get_earnings_dates(limit=28).index # error when limit=28 cuz of no data on some prices

    # [TOGGLE] Check that earnings are post-market by looking at the time
    # for index, val in enumerate(earnings_dates):
    #     print(index, val)

    for date in earnings_dates:
        # convert Timestamp to datetime and set to 4PM
        datetime_obj = date.to_pydatetime().replace(hour=16, minute = 0, second = 0)

        # create datetime array of times you want to pull prices
        time_arr = create_time_arr(datetime_obj)
        
        new_row = [None]*10
        # only grab dates in the past
        if datetime_obj < today:
            new_row[0] = datetime_obj # [JUST PULL DATE]

            for index, time in enumerate(time_arr):
                request_params = StockBarsRequest(symbol_or_symbols=ticker, start=time, end=time, timeframe=TimeFrame.Minute)
                try:
                    price = stock_client.get_stock_bars(request_params)[ticker][0]
                    new_row[index+1] = price.close
                except Exception as e:
                    # print("Error: " + str(e))
                    print(f"No data found for {ticker} at {time}")                

            earnings_df.loc[len(earnings_df.index)] = new_row
    
    print(earnings_df)

    # export datafram as csv to earnings folder
    earnings_df.to_csv(f"./earnings/{ticker}_earnings.csv")



def create_time_arr(datetime_obj) -> List[datetime.datetime]:
    """Create an array of datetimes: 4:01PM, 4:05PM, etc."""
    time_arr = []
    time_arr.append(datetime_obj)
    time_arr.append(datetime_obj + datetime.timedelta(minutes=1))
    time_arr.append(datetime_obj + datetime.timedelta(minutes=5))
    time_arr.append(datetime_obj + datetime.timedelta(minutes=30))
    time_arr.append(datetime_obj + datetime.timedelta(hours=1))
    time_arr.append(datetime_obj + datetime.timedelta(hours=1, minutes=30))
    time_arr.append(datetime_obj + datetime.timedelta(hours=2))
    time_arr.append(datetime_obj + datetime.timedelta(hours=2, minutes=30))
    time_arr.append(datetime_obj + datetime.timedelta(hours=3))
    return time_arr


if __name__ == '__main__':
    sys.exit(main())