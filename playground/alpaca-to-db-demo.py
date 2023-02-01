'''
This script pulls 3 minute bars of Intel and Nvidia stock from the Alpaca 
Market Data API, loads those 6 bars into the bar_minutes database table, then 
reads the same bars from the table.
'''

from datetime import datetime, timezone
import os

import pandas as pd
from alpaca.data import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame
from sqlalchemy import create_engine, sql

#------------------------------------------------------------------------------
# Environment setup
#------------------------------------------------------------------------------

# get alpaca environment variables
API_KEY = os.getenv('ALPACA_API_KEY_ID')
SECRET_KEY = os.getenv('ALPACA_SECRET_KEY')

# check for missing alpaca environment variables
if API_KEY == None or SECRET_KEY == None:
    print('[ ERROR ] Environment variables ALPACA_API_KEY_ID or ALPACA_SECRET_KEY not found.')
    print('[ INFO ] Exiting...')
    quit()

# get postgres environment variables
PG_HOST = os.getenv('PG_HOST')
PG_PORT = os.getenv('PG_PORT')
PG_DB_NAME = os.getenv('PG_DB_NAME')
PG_USERNAME = os.getenv('PG_USERNAME')
PG_PASSWORD = os.getenv('PG_PASSWORD')

# check for missing environment variables
if PG_HOST == None or PG_PORT == None or PG_DB_NAME == None or PG_USERNAME == None or PG_PASSWORD == None:
    print('[ ERROR ] Environment variables PG_HOST, PG_PORT, PG_DB_NAME, PG_USERNAME, or PG_PASSWORD not found.')
    print('[ INFO ] Exiting...')
    quit()

#------------------------------------------------------------------------------
# Establish connections
#------------------------------------------------------------------------------

# create alpaca client
stock_client = StockHistoricalDataClient(API_KEY, SECRET_KEY)

# connect to db and open a cursor to perform database operations
conn_string = "postgresql://{}:{}@{}:{}/{}".format(PG_USERNAME, PG_PASSWORD, PG_HOST, PG_PORT, PG_DB_NAME)
db = create_engine(conn_string)
conn = db.connect()

# conn_string = "host='{}' port='{}' dbname='{}' user='{}' password='{}'".format(PG_HOST, PG_PORT, PG_DB_NAME, PG_USERNAME, PG_PASSWORD)
# conn = psycopg2.connect(conn_string)
# cur = conn.cursor()

#------------------------------------------------------------------------------
# Pull Alpaca data
#------------------------------------------------------------------------------

# get minute bar for INTC and NVDA on 2023/01/27 from 9:40 to 9:42 EST
start_dt = datetime(2023, 1, 27, 14, 40, 0, 0, tzinfo=timezone.utc) # 2023/01/27 14:40 UTC
end_dt = datetime(2023, 1, 27, 14, 42, 0, 0, tzinfo=timezone.utc) # 2023/01/27 14:42 UTC
print('[ INFO ] Fetching minute bars for INTC and NVDA on 2023/01/27 for 9:40, 9:41, and 9:42 EST...')
request_params = StockBarsRequest(symbol_or_symbols=['INTC','NVDA'], timeframe=TimeFrame.Minute, start=start_dt, end=end_dt)
stock_bars_minute = stock_client.get_stock_bars(request_params)

#------------------------------------------------------------------------------
# Push data to DB
#------------------------------------------------------------------------------

# convert alpaca data to DataFrame and fix columns to match db
stock_bars_minute_df = stock_bars_minute.df
stock_bars_minute_df.reset_index(inplace=True)

# insert rows and commit
stock_bars_minute_df.to_sql(name='bars_minute', con=conn, if_exists='append', index=False)
# conn.commit() # uncomment to commit changes to db

#------------------------------------------------------------------------------
# Pull data from DB
#------------------------------------------------------------------------------

stock_bars_minute_df = pd.read_sql_query(sql=sql.text('SELECT * FROM bars_minute'), con=conn)
print('[ INFO ] Data from database:')
print(stock_bars_minute_df)

#------------------------------------------------------------------------------
# Close connections
#------------------------------------------------------------------------------

# rollback any uncommited transactions
conn.rollback()

# close db connection
conn = None