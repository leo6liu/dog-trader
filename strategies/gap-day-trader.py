# Gap Day Trading Bot

import datetime
import os
import sys

from alpaca.data import StockHistoricalDataClient, TimeFrame, StockBarsRequest


def main():
    """Gap Day Trading Bot"""

    # TODO: ticker list implementation
    # TODO: Holiday edge cases on previous weekday function

    # ------------------------------------------------------------------------------
    # Environment setup
    # ------------------------------------------------------------------------------

    # Get Alpaca environment variables
    API_KEY = os.getenv('ALPACA_API_KEY_ID')
    SECRET_KEY = os.getenv('ALPACA_SECRET_KEY')

    # Check for missing alpaca environment variables
    if API_KEY is None or SECRET_KEY is None:
        print('[ ERROR ] Environment variables ALPACA_API_KEY_ID or ALPACA_SECRET_KEY not found.')
        print('[ INFO ] Exiting...')
        quit()


    # ------------------------------------------------------------------------------
    # Establish connections
    # ------------------------------------------------------------------------------

    # Create Alpaca Client
    stock_client = StockHistoricalDataClient(API_KEY, SECRET_KEY)


    #------------------------------------------------------------------------------
    # Get previous high/low
    #------------------------------------------------------------------------------

    start_dt = get_last_weekday()
    end_dt = start_dt + datetime.timedelta(days=1)
    print("[ INFO ] Fetching previous day bar for AAPL")
    request_params = StockBarsRequest(symbol_or_symbols=['AAPL'], start=start_dt, end=end_dt, timeframe=TimeFrame.Day)
    previous_day_bar = stock_client.get_stock_bars(request_params)
    # print('Previous day bar:', previous_day_bar)

    previous_low = previous_day_bar['AAPL'][0].low
    previous_high = previous_day_bar['AAPL'][0].high
    print('Previous day low:', previous_low, '\nPrevious day high:', previous_high)

def get_last_weekday() -> datetime.datetime:
    """Get the last weekday"""
    today = datetime.datetime.today()
    # print('today:', today)
    offset = max(1, (today.weekday() + 6) % 7 - 3)
    last_weekday = today - datetime.timedelta(days=offset)
    return last_weekday.replace(hour=0, minute=0, second=0, microsecond=0)

if __name__ == '__main__':
    sys.exit(main())
