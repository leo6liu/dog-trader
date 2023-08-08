'''
This script should read a file containing earnings dates for certain tickers
and pull post market values and export it as a csv so it can be copied into the
google sheets for analysis.
'''

import datetime
import time
import os
import sys
import json


file = open("earnings.json")
data = json.load(file)

# {
#     "TSLA":
#         ["2023-07-19T20:00:00+00:00", "2023-04-19T20:00:00+00:00"]
# }

# date is in ISO 8601 format
for ticker in data:
    print(ticker)
    for date in data[ticker]:
        print(date)
        print(datetime.datetime.fromisoformat(date))

file.close()


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
