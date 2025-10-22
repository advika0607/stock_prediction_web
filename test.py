import yfinance as yf
print("Testing yfinance connection...")
ticker = yf.Ticker("AAPL")
hist = ticker.history(period="1d")
print(hist)