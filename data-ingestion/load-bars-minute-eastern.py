'''
Description:
This script pulls minute bars for an inputted ticker symbol for an inputted 
date range and insert the data into the bars_minute_eastern PostgreSQL table in 
RDS.

Usage:
$ python load-bars-minute-eastern.py -t/--ticker INTC -s/--start 20220314 -e/--end 20220420

Required Environment Variables:
ALPACA_API_KEY_ID, ALPACA_SECRET_KEY, PG_HOST, PG_PORT, PG_DB_NAME, 
PG_USERNAME, PG_PASSWORD

Details:
Each weekday bars will be collected from 09:00 to 16:00 EST, except on 
holidays where no bars will be collected.
'''

import argparse
import datetime
import json
import os
import sys

import pandas as pd
import pytz
from alpaca.data import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame
from sqlalchemy import create_engine, sql

def main() -> int:
    #--------------------------------------------------------------------------
    # Collect arguments
    #--------------------------------------------------------------------------
    
    parser = argparse.ArgumentParser(
        prog = 'load-bars-minute.py', 
        description = 'This script pulls minute bars for an inputted ticker symbol for an inputted date range and insert the data into the bars_minute_eastern PostgreSQL table in RDS.', 
        epilog = 'Made with love at Udon Code Studios ❤️'
    )
    
    parser.add_argument('-t', '--tickers', dest='tickers', action='store', required=True, help='Comma separated list of ticker symbol(s) (e.g. INTC,NVDA,WM)')
    parser.add_argument('-s', '--start', dest='start', action='store', required=True, help='Start date in YYYYMMDD format (inclusive).')
    parser.add_argument('-e', '--end', dest='end', action='store', required=True, help='End date in YYYYMMDD format (inclusive).')

    args = parser.parse_args()

    tickers = args.tickers.split(",")
    start = YYYYMMDDtoDate(args.start)
    current = start
    end = YYYYMMDDtoDate(args.end)

    #--------------------------------------------------------------------------
    # Environment setup
    #--------------------------------------------------------------------------

    # get alpaca environment variables
    API_KEY = os.getenv('ALPACA_API_KEY_ID')
    SECRET_KEY = os.getenv('ALPACA_SECRET_KEY')

    # check for missing alpaca environment variables
    if API_KEY == None or SECRET_KEY == None:
        print('[ ERROR ] Environment variables ALPACA_API_KEY_ID or ALPACA_SECRET_KEY not found.')
        print('[ INFO ] Exiting with code -1.')
        return -1

    # get postgres environment variables
    PG_HOST = os.getenv('PG_HOST')
    PG_PORT = os.getenv('PG_PORT')
    PG_DB_NAME = os.getenv('PG_DB_NAME')
    PG_USERNAME = os.getenv('PG_USERNAME')
    PG_PASSWORD = os.getenv('PG_PASSWORD')

    # check for missing environment variables
    if PG_HOST == None or PG_PORT == None or PG_DB_NAME == None or PG_USERNAME == None or PG_PASSWORD == None:
        print('[ ERROR ] Environment variables PG_HOST, PG_PORT, PG_DB_NAME, PG_USERNAME, or PG_PASSWORD not found.')
        print('[ INFO ] Exiting with code -1.')
        return -1

    # load holidays from properties
    holidays = loadHolidays('../properties/market-holidays.json')

    # hard-code table name
    PG_TABLE = 'bars_minute_eastern'

    #--------------------------------------------------------------------------
    # Establish connections
    #--------------------------------------------------------------------------

    # create alpaca client
    stock_client = StockHistoricalDataClient(API_KEY, SECRET_KEY)

    # connect to PostgreSQL instance
    conn_string = "postgresql://{}:{}@{}:{}/{}".format(PG_USERNAME, PG_PASSWORD, PG_HOST, PG_PORT, PG_DB_NAME)
    db = create_engine(conn_string)
    conn = db.connect()

    #------------------------------------------------------------------------------
    # Data loading loop
    #------------------------------------------------------------------------------

    # loop from start to end date one day at a time
    delta = datetime.timedelta(days=1)
    while current <= end:
        # skip weekends
        if isWeekend(current):
            current += delta
            continue

        # skip holidays
        if isHoliday(current, holidays):
            current += delta
            continue

        # pull minute bars for tickers from 09:00 to 16:00 EST
        start_dt = getNoTimeZoneUTCfromNoTimeZoneEST(datetime.datetime(current.year, current.month, current.day, 9, 0))
        end_dt = getNoTimeZoneUTCfromNoTimeZoneEST(datetime.datetime(current.year, current.month, current.day, 16, 0))
        print(f'[ INFO ] Fetching minute bars for {tickers} from 09:00 to 16:00 EST on {current}')
        request_params = StockBarsRequest(symbol_or_symbols=tickers, timeframe=TimeFrame.Minute, start=start_dt, end=end_dt)
        stock_bars_minute = stock_client.get_stock_bars(request_params)

        # convert alpaca data to DataFrame
        stock_bars_minute_df = stock_bars_minute.df
        stock_bars_minute_df.reset_index(inplace=True)

        # drop unused columns
        stock_bars_minute_df.drop('trade_count', axis=1, inplace=True)
        stock_bars_minute_df.drop('vwap', axis=1, inplace=True)

        # timestamp to be timezone unaware (US/Eastern values)
        stock_bars_minute_df['timestamp'] = pd.to_datetime(stock_bars_minute_df['timestamp']).dt.tz_convert(pytz.timezone("US/Eastern")).dt.tz_localize(tz=None)

        # insert rows and commit
        stock_bars_minute_df.to_sql(name=PG_TABLE, con=conn, if_exists='append', index=False)
        conn.commit()

        # go to next day
        current += delta
    
    #--------------------------------------------------------------------------
    # Close connections
    #--------------------------------------------------------------------------

    # rollback any uncommited transactions
    conn.rollback()

    # close db connection
    conn = None

    #--------------------------------------------------------------------------
    # Exit program
    #--------------------------------------------------------------------------

    print('[ INFO ] Exiting normally with code 0.') 
    return 0

'''
Converts a string in YYYYMMDD format to a datetime.date object.
Undefined behavior if input is not a valid YYYYMMDD string.
'''
def YYYYMMDDtoDate(input: str) -> datetime.date: 
    year = int(input[0:4])
    month = int(input[4:6])
    day = int(input[6:8])
    return datetime.date(year, month, day)

def isWeekend(date: datetime.date) -> bool:
    return date.weekday() >= 5

def isHoliday(date: datetime.date, holidays: dict[str, list]) -> bool:
    for holiday in holidays[str(date.year)]:
        if date.month == holiday['month'] and date.day == holiday['day']:
            return True

    return False

def loadHolidays(path: str) -> dict:
    # open market-holidays.json file
    file = open(path)

    # read json into dictionary
    holidays = json.load(file)

    return holidays

def getNoTimeZoneUTCfromNoTimeZoneEST(estDatetime: datetime.datetime) -> datetime.datetime:
    if isDST(datetime.date(estDatetime.year, estDatetime.month, estDatetime.day)):
        return estDatetime + datetime.timedelta(hours=4)
    else:
        return estDatetime + datetime.timedelta(hours=5)
    
'''
During DST, clocks are moved forward 1 hr (e.g. 13:00 —> 14:00).
DST begins at 02:00 on the second Sunday of March.
DST ends at 02:00 on the first Sunday of November.
'''
def isDST(date: datetime.date) -> bool:
    if date.month < 3 or date.month > 11:
        return False
    elif date.month > 3 and date.month < 11:
        return True
    elif date.month == 3:
        return date.day >= getDayOfSecondSundayOfMarch(date.year)
    else: # date.month == 11
        return date.day < getDayOfFirstSundayOfNovember(date.year)

def getDayOfSecondSundayOfMarch(year: int) -> int:
    return getDayOfOrdinalWeekdayOfMonthOfYear(2, 6, 3, year)

def getDayOfFirstSundayOfNovember(year: int) -> int:
    return getDayOfOrdinalWeekdayOfMonthOfYear(1, 6, 11, year)

'''
ordinal (int: first -> 1 ... fourth -> 4)
weekday (int: Monday -> 0 ... Sunday -> 6)
month (int: January -> 1 ... December -> 12)
'''
def getDayOfOrdinalWeekdayOfMonthOfYear(ordinal: int, weekday: int, month: int, year: int) -> int:
    first = datetime.date(year, month, 1)
    firstDayOfWeek = first.weekday()
    firstWeekday = weekday - firstDayOfWeek + 1
    ordinalWeekday = firstWeekday + (7 * (ordinal - 1))
    return ordinalWeekday

if __name__ == '__main__':
    sys.exit(main())
