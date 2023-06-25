# Gap Day Trading Bot

import datetime
import os
import sys

from alpaca.data import StockHistoricalDataClient, TimeFrame, StockBarsRequest


def main():
    """Gap Day Trading Bot"""

    # TODO: Ticker list implementation
    # TODO: Holiday edge cases on previous weekday function
    # TODO: Display trading results/graph
    # TODO: Understand which market conditions this work for

    # Tickers: AAPL, SBUX, TSLA, NVDA, GOOG, GOOGL, MSFT, AMZN, META, JNJ, JPM, XOM, PG, COST, AMD
    tickers = ['AAPL', 'SBUX']

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
    # Get previous trading day's high/low
    #------------------------------------------------------------------------------

    start_dt = get_last_weekday()
    end_dt = start_dt + datetime.timedelta(days=1)
    print("[ INFO ] Fetching previous day bar for", ", ".join(tickers))
    request_params = StockBarsRequest(symbol_or_symbols=tickers, start=start_dt, end=end_dt, timeframe=TimeFrame.Day)
    previous_day_bar = stock_client.get_stock_bars(request_params)
    # print('Previous day bar:', previous_day_bar)

    for ticker in tickers:
        previous_high = previous_day_bar[ticker][0].high
        previous_low = previous_day_bar[ticker][0].low
        print(f'\033[1m{ticker}\033[0m\nPrevious day high: {previous_high} \nPrevious day low: {previous_low}')

        #------------------------------------------------------------------------------
        # TRADE CONDITIONS AND EXECUTIONS GO HERE
        #------------------------------------------------------------------------------


    # print('Previous day high:', previous_high, '\nPrevious day low:', previous_low)


def get_last_weekday() -> datetime.datetime:
    """Get the last weekday"""
    today = datetime.datetime.today()
    offset = max(1, (today.weekday() + 6) % 7 - 3)
    last_weekday = today - datetime.timedelta(days=offset)
    return last_weekday.replace(hour=0, minute=0, second=0, microsecond=0)

if __name__ == '__main__':
    sys.exit(main())
