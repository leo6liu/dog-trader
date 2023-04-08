# dog-trader

A trading bot which uses an ML model trained on historical stock data.

## What is finished?

- DB table to store minute bar data has been created.
- A demo script has been written to pull market data from Alpaca.
- A demo script has been written to pull data from DB into a DataFrame.
- Script to load minute bar data into DB for historical trading days.

## Next Steps

- Ethan local system setup (WSL).
- Ethan -> Demo script: get sentiment info from ChatGPT (https://help.openai.com/en/collections/3675931-openai-api) (e.g. 0-9, 0-4 sell, 5-9 buy)
- Ethan -> Figure out pricing and rate limits of ChatGPT API.
- Leo -> Create trader service.
- Train model which predicts ticker price at next minute (using only single ticker input).
- Demo script: execute trades with Alpaca.

## Data Ingestion (Python)

## Training (Python)

## Trader Logic (Go)

1. get current minute data and calculate numberical perdiction
2. get sentiment (afterwards put in database for future use)
3. execute explicit logic based on 1. and 2. to decide buy/hold/sell
4. execute transaction

## Future Visions

- Everyday market data is automatically loaded into AWS Timestream and the model is retrained in AWS SageMaker.
- The bot can simulate and visualize it's performance over historical data.
- The bot can predict how much it will make by market close.
- The bot can predict long-term stock prices.
- The bot can use additional metrics such as market sector categorization, financials, and dividends.
- The bot can use additional metrics such as current news articles and stock sentiment analysis.
