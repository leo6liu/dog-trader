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
for ticker in tickers: # loop through tickers rather than csv files so we can use 'ticker' as a variable
    with open(f"./earnings/{ticker}_earnings.csv") as earnings_csv:
        reader = csv.reader(earnings_csv, delimiter=",")

        for row in reader:
            print(row[0], row[1])

