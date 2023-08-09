import os
import datetime
import sys

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import tensorflow as tf
from sqlalchemy import create_engine, sql

mpl.rcParams['figure.figsize'] = (8, 6)
mpl.rcParams['axes.grid'] = False

def main() -> int:
    #--------------------------------------------------------------------------
    # Environment setup
    #--------------------------------------------------------------------------

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

    # hard-code table name
    PG_TABLE = 'bars_minute'

    #------------------------------------------------------------------------------
    # Establish connections
    #------------------------------------------------------------------------------

    # connect to db and open a cursor to perform database operations
    conn_string = "postgresql://{}:{}@{}:{}/{}".format(PG_USERNAME, PG_PASSWORD, PG_HOST, PG_PORT, PG_DB_NAME)
    db = create_engine(conn_string)
    conn = db.connect()

    #------------------------------------------------------------------------------
    # Pull data from db
    #------------------------------------------------------------------------------

    stock_bars_minute_df = pd.read_sql_query(sql=sql.text(f'select * from { PG_TABLE } where SYMBOL=\'NVDA\''), con=conn)
    print('[ INFO ] Data from database:')
    print(stock_bars_minute_df)

    # convert to 

    date_time = pd.to_datetime(stock_bars_minute_df.pop('timestamp'), format='%d.%m.%Y %H:%M:%S')

    plot_cols = ['close', 'volume']
    plot_features = stock_bars_minute_df[plot_cols]
    plot_features.index = date_time
    _ = plot_features.plot(subplots=True)

    #--------------------------------------------------------------------------
    # Exit program
    #--------------------------------------------------------------------------

    print('[ INFO ] Exiting normally with code 0.') 
    return 0

if __name__ == '__main__':
    sys.exit(main())
    