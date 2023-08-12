'''
This script should pull the earnings data csv generated from the earnings-post-market.py file
and run an analysis on it. This is different from the chart analysis in the Google Sheets.
Google sheets: https://docs.google.com/spreadsheets/d/1UxmLRIjj0FW-c8tXj40IWlSjulzNBA1r07jE0qD6QW8/edit?usp=sharing
'''
__author__ = "Ethan Chang"
__email__ = "ethanchang34@yahoo.com"

import os
import csv

# get csv files
file_names = os.listdir("./earnings")

# get tickers from csv files
tickers = []
for file_name in file_names:
    tickers.append(file_name.split("_")[0])

# open csv files
# for ticker in tickers: # loop through tickers rather than csv files so we can use 'ticker' as a variable
#     with open(f"./earnings/{ticker}_earnings.csv") as earnings_csv:
#         reader = csv.reader(earnings_csv, delimiter=",")

#         # analysis
#         same_direction = 0
#         length = 0
#         next(reader) # skip the first row
#         for row in reader:
#             # fraction of scenarios where movement direction from 4:00 to 4:05 is the same as direction from 4:05 to 4:30
#             # numbers represented as strings can be compared, no need to convert to float
#             if row[4] > row[2] and row[5] > row[4]:
#                 same_direction += 1
#             elif row[4] < row[2] and row[5] < row[4]:
#                 same_direction += 1
#             length += 1
#         print(f"{ticker} 4:00 -> 4:05 and 4:05 -> 4:00 same direction: {same_direction/length}")

ticker = "AAPL"
with open(f"./earnings/{ticker}_earnings.csv") as earnings_csv:
    reader = csv.reader(earnings_csv, delimiter=",")
    same_direction = 0
    length = 0
    next(reader)

    for row in reader:
        if row[4] > row[3]:
            if row[8] > row[4]:
                same_direction += 1
            length += 1

    print(same_direction, length)
    print(f"{ticker} 4:01 -> 4:05 -> 6:00 same direction: {same_direction/length}")
