import pandas as pd
import yfinance as yf
import tensorflow as tf
import numpy as np
import os
import pandas_ta as ta  # For technical indicators
import pandas_datareader.data as web  # For macroeconomic data
import datetime

# Function to add technical indicators
def add_technical_indicators(df):
    # Calculate RSI (Relative Strength Index)
    df['RSI'] = ta.rsi(df['Close'], length=14)

    # Calculate MACD (Moving Average Convergence Divergence)
    macd = ta.macd(df['Close'], fast=12, slow=26, signal=9)
    df = df.join(macd)

    # Calculate Moving Averages
    df['MA_50'] = ta.sma(df['Close'], length=50)
    df['MA_200'] = ta.sma(df['Close'], length=200)

    # Calculate Daily Returns
    df['Daily_Return'] = df['Close'].pct_change()

    return df

url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
table = pd.read_html(url)
tickers = table[0]['Symbol'].tolist()
tickers = [ticker.replace('.', '-') for ticker in tickers]

# Define tickers and date range
start_date = "2013-01-01"
end_date = "2025-01-01"  # Adjust as needed

# Download data
df = yf.download(tickers, start=start_date, end=end_date, group_by="ticker")

# Restructure data into tidy format
data = []
for ticker in tickers:
    stock = df[ticker].copy()
    stock["Ticker"] = ticker
    stock.reset_index(inplace=True)  # Make Date a column
    data.append(stock)

# Combine all tickers into a single DataFrame
final_df = pd.concat(data, ignore_index=True)

# Rename column
# Reorder columns
# Add technical indicators to each stock
final_df = final_df.groupby('Ticker').apply(add_technical_indicators)

# Fetch macroeconomic data (e.g., US Federal Funds Rate)
start = datetime.datetime(2013, 1, 1)
end = datetime.datetime(2025, 1, 1)
interest_rates = web.DataReader('FEDFUNDS', 'fred', start, end)

# Merge macroeconomic data with the main dataset
final_df = final_df.merge(interest_rates, how='left', left_on='Date', right_index=True)
final_df.rename(columns={'FEDFUNDS': 'Interest_Rate'}, inplace=True)

# Reorder columns
final_df = final_df[["Date", "Ticker", "Open", "High", "Low", "Close", "Volume", 
                     "RSI", "MACD_12_26_9", "MACDs_12_26_9", "MACDh_12_26_9", 
                     "MA_50", "MA_200", "Daily_Return", "Interest_Rate"]]


# Save to CSV
final_df.to_csv("stock_data.csv", index=False)

print(final_df)