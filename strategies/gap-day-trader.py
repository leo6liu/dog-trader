# Gap Day Trading Bot

import datetime
import os
import sys

from alpaca.data import StockHistoricalDataClient, TimeFrame, StockBarsRequest
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest, LimitOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce


def main():
    """Gap Day Trading Bot"""

    # TODO: Trade conditionals
    # TODO: Trade execution
    # TODO: Holiday edge cases on previous weekday function
    # TODO: Display trading results/graph
    # TODO: Understand which market conditions this work for

    # Tickers: AAPL, SBUX, TSLA, NVDA, GOOG, GOOGL, MSFT, AMZN, META, JNJ, JPM, XOM, PG, COST, AMD
    tickers = ['AAPL', 'SBUX']

    # ------------------------------------------------------------------------------
    # Environment Setup
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
    # Establish Connections/Create Alpaca Clients
    # ------------------------------------------------------------------------------
    # Create Alpaca clients
    stock_client = StockHistoricalDataClient(API_KEY, SECRET_KEY)
    trading_client = TradingClient(API_KEY, SECRET_KEY, paper=True)


    #------------------------------------------------------------------------------
    # Get Previous Trading Day's High/Low
    #------------------------------------------------------------------------------
    start_dt = get_last_weekday()
    end_dt = start_dt + datetime.timedelta(days=1)
    print("[ INFO ] Fetching previous day bar for", ", ".join(tickers))
    request_params = StockBarsRequest(symbol_or_symbols=tickers, start=start_dt, end=end_dt, timeframe=TimeFrame.Day)
    previous_day_bar = stock_client.get_stock_bars(request_params)
    # print('Previous day bar:', previous_day_bar)


    for ticker in tickers:
        # Print each ticker's previous high and low
        previous_high = previous_day_bar[ticker][0].high
        previous_low = previous_day_bar[ticker][0].low
        print(f'\033[1m---{ticker}---\033[0m\nPrevious day high: {previous_high} \nPrevious day low: {previous_low}')


        #------------------------------------------------------------------------------
        # TRADE CONDITIONS AND EXECUTIONS
        #------------------------------------------------------------------------------
        gap_up = False
        gap_down = False
        # [Conditions for gap up and gap down]

        if gap_down:

            order_data = LimitOrderRequest(symbol=ticker, limit_price=previous_low+0.02, qty=100, side=OrderSide.BUY, time_in_force=TimeInForce.DAY)
            limit_order = trading_client.submit_order(order_data=order_data)
        elif gap_up:

            order_data = LimitOrderRequest(symbol=ticker, limit_price=previous_high-0.02, qty=100, side=OrderSide.SELL, time_in_force=TimeInForce.DAY)
            limit_order = trading_client.submit_order(order_data=order_data)
        gap_up = False
        gap_down = False




def get_last_weekday() -> datetime.datetime:
    """Get the last weekday"""
    today = datetime.datetime.today()
    offset = max(1, (today.weekday() + 6) % 7 - 3)
    last_weekday = today - datetime.timedelta(days=offset)
    return last_weekday.replace(hour=0, minute=0, second=0, microsecond=0)

if __name__ == '__main__':
    sys.exit(main())
