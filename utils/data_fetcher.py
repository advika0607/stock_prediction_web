import yfinance as yf
import pandas as pd
import numpy as np
import requests
import time
from datetime import datetime, timedelta
import hashlib
import warnings

warnings.filterwarnings('ignore')

class DataFetcher:
    def __init__(self, ticker):
        self.ticker = ticker.upper()
        self.data = None
        self.info = None
        self.data_source = None

    def fetch_data(self, period='5y'):
        print(f"[INFO] Fetching data for {self.ticker} (Yahoo Finance only)...")
        for attempt in range(3):
            try:
                print(f"[DEBUG] yfinance attempt {attempt+1}/3...")
                session = requests.Session()
                session.headers.update({'User-Agent': 'Mozilla/5.0 AppleWebKit/537.36'})
                stock = yf.Ticker(self.ticker, session=session)
                self.data = stock.history(period=period, interval='1d', auto_adjust=False, actions=False, timeout=10)
                if self.data is not None and not self.data.empty and len(self.data) >= 1:
                    self.data.reset_index(inplace=True)
                    self.data_source = "Yahoo"
                    print(f"[SUCCESS] YFinance success for {self.ticker} ({len(self.data)} rows)")
                    return self.data
            except Exception as e:
                print(f"[WARN] yfinance attempt {attempt+1} failed: {e}")
            time.sleep(2 * (attempt + 1))
        print(f"[CRITICAL] All Yahoo Finance fetch attempts failed. Using synthetic data fallback.")
        self.data = self._create_sample_data()
        self.data_source = "Synthetic"
        return self.data

    def _create_sample_data(self):
        seed_val = int(hashlib.sha256(self.ticker.encode()).hexdigest(), 16) % (2 ** 32)
        np.random.seed(seed_val)
        dates = pd.date_range(end=datetime.now(), periods=1260, freq='D')
        base_price = np.random.uniform(50, 250)
        drift = np.random.normal(0.0003, 0.02, len(dates))
        prices = base_price * np.exp(np.cumsum(drift))
        df = pd.DataFrame({
            'Date': dates,
            'Open': prices * (1 + np.random.uniform(-0.01, 0.01, len(dates))),
            'High': prices * (1 + np.random.uniform(0, 0.02, len(dates))),
            'Low': prices * (1 + np.random.uniform(-0.02, 0, len(dates))),
            'Close': prices,
            'Volume': np.random.randint(10_000_000, 120_000_000, len(dates))
        })
        return df

    def get_stock_info(self):
        try:
            print(f"[INFO] Fetching info for {self.ticker} (Yahoo Finance)...")
            session = requests.Session()
            session.headers.update({'User-Agent': 'Mozilla/5.0 AppleWebKit/537.36'})
            stock = yf.Ticker(self.ticker, session=session)
            info = {}
            try:
                info = stock.info
            except Exception as e:
                print(f"[WARN] Yahoo info fetch failed: {e}")

            # Always fetch latest data if missing
            if self.data is None or self.data.empty:
                print("[DEBUG] Data not loaded, fetching now.")
                self.fetch_data(period='1mo')

            # Prefer Yahoo info if available
            current_price = info.get('currentPrice') or info.get('regularMarketPrice') or 0
            previous_close = info.get('previousClose') or info.get('regularMarketPreviousClose') or 0
            day_high = info.get('dayHigh') or info.get('regularMarketDayHigh') or 0
            day_low = info.get('dayLow') or info.get('regularMarketDayLow') or 0
            volume = info.get('volume') or info.get('regularMarketVolume') or 0
            avg_volume = info.get('averageVolume') or 0
            fifty_two_week_high = info.get('fiftyTwoWeekHigh') or 0
            fifty_two_week_low  = info.get('fiftyTwoWeekLow') or 0

            # Fallback to historical if info missing
            if self.data is not None and not self.data.empty:
                hist = self.data
                if not current_price:    current_price    = float(hist['Close'].iloc[-1])
                if not previous_close:   previous_close   = float(hist['Close'].iloc[-2]) if len(hist) > 1 else float(hist['Close'].iloc[-1])
                if not day_high:         day_high         = float(hist['High'].iloc[-1])
                if not day_low:          day_low          = float(hist['Low'].iloc[-1])
                if not volume:           volume           = int(hist['Volume'].iloc[-1])
                if not avg_volume:       avg_volume       = int(hist['Volume'].mean())
                lookback = min(252, len(hist))
                if not fifty_two_week_high: fifty_two_week_high = float(hist['High'].tail(lookback).max())
                if not fifty_two_week_low:  fifty_two_week_low  = float(hist['Low'].tail(lookback).min())

            # FINAL FRESH YFINANCE ATTEMPT if returned price looks synthetic or fallback
            if not current_price or abs(current_price - previous_close) < 0.1 or current_price == previous_close:
                try:
                    print("[DEBUG] Attempting fresh real-time fetch (1d)...")
                    fresh = stock.history(period="1d", interval="1d")
                    if not fresh.empty:
                        current_price = float(fresh["Close"].iloc[-1])
                        previous_close = float(fresh["Open"].iloc[-1])
                        day_high = float(fresh["High"].iloc[-1])
                        day_low = float(fresh["Low"].iloc[-1])
                        volume = int(fresh["Volume"].iloc[-1])
                        print(f"[SUCCESS] Fresh data retrieved: {current_price}")
                except Exception as e:
                    print(f"[DEBUG] Fresh real-time fetch failed: {e}")

            self.info = {
                "symbol": self.ticker,
                "name": info.get("longName", self.ticker),
                "currency": info.get("currency", "USD"),
                "exchange": info.get("exchange", "NASDAQ"),
                "market_cap": info.get("marketCap", 0),
                "current_price": current_price,
                "previous_close": previous_close,
                "day_high": day_high,
                "day_low": day_low,
                "volume": volume,
                "avg_volume": avg_volume,
                "52_week_high": fifty_two_week_high,
                "52_week_low": fifty_two_week_low,
            }
            print(f"[SUCCESS] Final price for {self.ticker}: ${self.info['current_price']}")
            return self.info

        except Exception as e:
            print(f"[ERROR] Info fetch failed for {self.ticker}: {e}")
            return {"symbol": self.ticker, "current_price": 0}
