import pandas as pd
import yfinance as yf
import tensorflow as tf
import numpy as np
import os


# THESE WILL BE INPUTTED EVENTUALLY
tickers = ['AAPL', 'MSFT']

# time range for historical data (adjust manually)
startDate = '2021-01-01'
endDate = '2021-01-08'

# empty data frame that will store the historical data of all inputted tickers
data = pd.DataFrame()

# loop through all tickers and download there historical data
for ticker in tickers:
    # download the tickers data
    tickerData = yf.download(tickers, start=startDate, end=endDate)

    # make a column for the ticker
    tickerData['Ticker'] = ticker

    # add the data for this ticker to the data frame with data from all tickers
    data = pd.concat([data, tickerData])

# save historical data from all tickers into a single csv file
data.to_csv('HistoricalTickerData.csv')

