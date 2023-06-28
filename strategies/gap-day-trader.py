# Gap Day Trading Bot

import datetime
import os
import sys

from alpaca.data import StockHistoricalDataClient, TimeFrame, StockBarsRequest
from alpaca.data.live.stock import StockDataStream
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest, LimitOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce

all_gaps_checked = False

def main():
    """Gap Day Trading Bot"""
    # TODO: Consider storing initial BUY limit order_id's into an array. Loop over the array to cancel them at 10:00
    # TODO: How to grab today's opening price? First data in websocket stream? Call day bar? Call minute bar?
    # TODO: Trade conditionals
    # TODO: Trade execution
    # TODO: Holiday edge cases on previous weekday function
    # TODO: Display trading results/graph
    # TODO: If generalizable, add scanner implementation to generate ticker list
    # TODO: Understand which market conditions this work for/stick to one market


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
    stock_stream = StockDataStream(API_KEY, SECRET_KEY)
    # Add this to StockDataStream params and test during trading hours to see if we can reduce the speed of each response
    # websocket_params={"ping_interval": 10, "ping_timeout": 180, "max_queue": 1024,} # No success in slowing responses
    
    # Account information
    # account = dict(trading_client.get_account())
    # for k,v in account.items():
    #     print(f'{k:30}{v}')


    #------------------------------------------------------------------------------
    # Get Previous Trading Day's High/Low
    #------------------------------------------------------------------------------
    start_dt = get_last_weekday()
    end_dt = start_dt + datetime.timedelta(days=1)
    print("[ INFO ] Fetching previous day bar for", ", ".join(tickers))
    request_params = StockBarsRequest(symbol_or_symbols=tickers, start=start_dt, end=end_dt, timeframe=TimeFrame.Day)
    previous_day_bar = stock_client.get_stock_bars(request_params)
    # print('Previous day bar:', previous_day_bar)


    #------------------------------------------------------------------------------
    # Create Ticker Objects and Store in Dictionary
    #------------------------------------------------------------------------------
    tickers_dict = {} # Dictionary with key as ticker symbol and value as the ticker object
    for ticker in tickers:
        previous_high = previous_day_bar[ticker][0].high
        previous_low = previous_day_bar[ticker][0].low
        ticker_obj = Tickers(ticker, previous_high, previous_low) # Store high/low values into ticker objects
        tickers_dict[ticker_obj.symbol] = ticker_obj # Add ticker object to dictionary
        # print(f'\033[1m---{ticker}---\033[0m\nPrevious day high: {previous_high} \nPrevious day low: {previous_low}')
        

    #------------------------------------------------------------------------------
    # Stream Real-Time Stock Market Data
    #------------------------------------------------------------------------------
    gap_orders = [] # The limit orders that get opened at 9:30 if there's a gap and used later to close any unfilled gap orders
    # Async handler
    async def quote_data_handler(data):
        global all_gaps_checked
        
        # If all gaps are checked, there's no need to check each ticker again
        if not all_gaps_checked:

            # If the ticker has already been checked, we don't need to check it again
            if not tickers_dict[data.symbol].gap_check:
                market_price = data.ask_price # Assume market price is the ask price since that's what we'd buy at

                if market_price > 1.03 * tickers_dict[data.symbol].high: # Only consider a 3% gap up

                    tickers_dict[data.symbol].gap_up = True # [COULD BE REDUNDANT]

                    # Request sell limit order
                    order_data = LimitOrderRequest(symbol=data.symbol, limit_price=previous_high-0.02, qty=100, side=OrderSide.SELL, time_in_force=TimeInForce.DAY)
                    limit_order = trading_client.submit_order(order_data=order_data)
                    gap_orders.append(limit_order.id)

                elif market_price < 0.98 * tickers_dict[data.symbol].low: # Only consider a 2% gap down

                    tickers_dict[data.symbol].gap_down = True # [COULD BE REDUNDANT]

                    # Request buy limit order
                    order_data = LimitOrderRequest(symbol=data.symbol, limit_price=previous_low+0.02, qty=100, side=OrderSide.BUY, time_in_force=TimeInForce.DAY)
                    limit_order = trading_client.submit_order(order_data=order_data)
                    gap_orders.append(limit_order.id) # Store order_id to cancel the order if it's not filled
                    
                tickers_dict[data.symbol].gap_check = True
            
            # Check if all_gaps_checked should now be True
            all_gaps_checked = True
            for t_obj in tickers_dict.values():

                # If a ticker's gap is not checked, then all_gaps_checked is False
                if not t_obj.gap_check:
                    all_gaps_checked = False

        # If all tickers are checked, we can close the real-time data stream       
        else:
            stock_stream.close()


        print(data) # Quote data
    stock_stream.subscribe_quotes(quote_data_handler, 'AAPL', 'SBUX')
    stock_stream.run()


    print('OUTSIDE WEBSOCKET~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
    for t_obj in tickers_dict.values():
        #------------------------------------------------------------------------------
        # TRADE CONDITIONS AND EXECUTIONS
        # TODO: Set custom time expiration on limit orders
        # TODO: More difficult than using expiration, but hardcode a timer to cancel orders by ID if their status is not filled
        # TODO: Set stop loss
        # TODO: Set profit locks
        # TODO: Consider fill speed
        # TODO: Set FPO condition
        #------------------------------------------------------------------------------
        print('foobar')



class Tickers:
    """Ticker Object"""
    def __init__(self, symbol, high, low):
        self.symbol = symbol
        self.high = high
        self.low = low
    gap_up = False
    gap_down = False
    gap_check = False
    order_id = ""


def get_last_weekday() -> datetime.datetime:
    """Get the last weekday"""
    today = datetime.datetime.today()
    offset = max(1, (today.weekday() + 6) % 7 - 3)
    last_weekday = today - datetime.timedelta(days=offset)
    return last_weekday.replace(hour=0, minute=0, second=0, microsecond=0)


if __name__ == '__main__':
    sys.exit(main())
