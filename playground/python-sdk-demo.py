from datetime import datetime
import os
from alpaca.data import CryptoHistoricalDataClient, StockHistoricalDataClient
from alpaca.data.requests import CryptoBarsRequest, StockBarsRequest
from alpaca.data.timeframe import TimeFrame

# get environment variables
print('[ INFO ] Collecting environment variables (ALPACA_API_KEY_ID, ALPACA_SECRET_KEY)...')
API_KEY = os.getenv('ALPACA_API_KEY_ID')
SECRET_KEY = os.getenv('ALPACA_SECRET_KEY')

# check for missing environment variables
if API_KEY == None or SECRET_KEY == None:
    print('[ ERROR ] Environment variables ALPACA_API_KEY_ID or ALPACA_SECRET_KEY not found.')
    print('[ INFO ] Exiting...')
    quit()

# create Alpaca clients
print('[ INFO ] Creating Alpaca clients...')
crypto_client = CryptoHistoricalDataClient()
stock_client = StockHistoricalDataClient(API_KEY, SECRET_KEY)

# get day bar for BTC/USD on 2023/01/27
print('[ INFO ] Fetching day bar for BTC/USD on 2023/01/27...')
request_params = CryptoBarsRequest(symbol_or_symbols=['BTC/USD'], timeframe=TimeFrame.Day, start=datetime(2023, 1, 27))
crypto_day_bars = crypto_client.get_crypto_bars(request_params)

# get day bar for INTC on 2023/01/27
print('[ INFO ] Fetching day bar for INTC,AMD,NVDA on 2023/01/27...')
request_params = StockBarsRequest(symbol_or_symbols=['INTC', 'AMD', 'NVDA'], timeframe=TimeFrame.Day, start=datetime(2023, 1, 27))
stock_day_bars = stock_client.get_stock_bars(request_params)

# convert bars to dataframes
crypto_day_bars = crypto_day_bars.df
stock_day_bars = stock_day_bars.df

# print bar data
print('[ INFO ] BTC/USD day bar:\n', crypto_day_bars, sep='', end='\n\n')
print('[ INFO ] INTC day bar:\n', stock_day_bars, sep='', end='\n\n')
