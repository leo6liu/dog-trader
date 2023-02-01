# dog-trader

A trading bot which uses an ML model trained on historical stock data.

## What is finished?

- DB table to store minute bar data has been created.
- A demo script has been written to pull market data from Alpaca.
- A demo script has been written to pull data from DB into a DataFrame.

## Next Steps

- Script to load minute bar data into DB for historical trading days.

## Future Visions

- Everyday market data is automatically loaded into AWS Timestream and the model is retrained in AWS SageMaker.
- The bot can simulate and visualize it's performance over historical data.
- The bot can predict how much it will make by market close.
- The bot can predict long-term stock prices.
- The bot can use additional metrics such as market sector categorization, financials, and dividends.
- The bot can use additional metrics such as current news articles and stock sentiment analysis.
