"""
Predictor - Make stock price predictions using pre-trained models
"""

import numpy as np
import pandas as pd
import os

from tensorflow.keras.models import load_model
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

from .data_fetcher import DataFetcher
from .preprocessor import DataPreprocessor

class StockPredictor:
    """Stock prediction using pre-trained models"""

    def __init__(self, ticker, config):
        self.ticker = ticker.upper()
        self.config = config
        self.fetcher = DataFetcher(ticker)
        self.data = None
        self.preprocessor = None
        self.model = None
        self.scaler = None
        self.predictions = None
        self.metrics = None

    def fetch_and_prepare_data(self):
        """Fetch and prepare data safely"""
        self.data = self.fetcher.fetch_data(period='max')
        if self.data is None or len(self.data) < self.config.SEQUENCE_LENGTH + 2:
            print(f"[DEBUG] Not enough data rows ({0 if self.data is None else len(self.data)}) for {self.ticker}.")
            return False
        self.preprocessor = DataPreprocessor(self.data)
        self.preprocessor.clean_data()
        self.preprocessor.add_features()
        # Prepare data for LSTM
        X, y, scaler = self.preprocessor.prepare_lstm_data(sequence_length=self.config.SEQUENCE_LENGTH)
        print(f"[DEBUG] LSTM X shape: {X.shape}, y shape: {y.shape}")
        if X.shape[0] < 2:  # need at least 2 samples to train/test split
            print(f"[DEBUG] Not enough LSTM samples ({X.shape[0]}) for {self.ticker}.")
            return False
        return True

    def load_model(self, model_path=None):
        """Load pre-trained LSTM model"""
        if model_path is None:
            # Try multiple possible model paths
            possible_paths = [
                f"{self.config.MODEL_DIR}/{self.ticker}_lstm_model.h5",
                f"{self.config.MODEL_DIR}/lstm_model.h5",
                f"models/{self.ticker}_lstm_model.h5",
                f"models/lstm_model.h5"
            ]
            for path in possible_paths:
                if os.path.exists(path):
                    model_path = path
                    break
        if model_path is None or not os.path.exists(model_path):
            return False
        try:
            self.model = load_model(model_path)
            print(f"✓ Loaded model from: {model_path}")
            return True
        except Exception as e:
            print(f"✗ Error loading model: {str(e)}")
            return False

    def predict_with_loaded_model(self):
        """Make predictions using loaded model"""
        if self.model is None:
            return None, None
        X, y, self.scaler = self.preprocessor.prepare_lstm_data(
            sequence_length=self.config.SEQUENCE_LENGTH
        )
        # Split data (use only test set for prediction)
        split_idx = int(len(X) * self.config.TRAIN_SIZE)
        X_test = X[split_idx:]
        y_test = y[split_idx:]
        if len(X_test) == 0 or len(y_test) == 0:
            print("[DEBUG] No test data available after split.")
            return None, None
        predictions_scaled = self.model.predict(X_test, verbose=0)
        self.predictions = self.scaler.inverse_transform(predictions_scaled)
        y_test_actual = self.scaler.inverse_transform(y_test.reshape(-1, 1))
        self.metrics = self.calculate_metrics(y_test_actual, self.predictions)
        return self.predictions, self.metrics

    def predict_future(self, days=30):
        """Predict future stock prices"""
        if self.model is None or self.scaler is None:
            return None
        # Get last sequence
        data_cleaned = self.preprocessor.data.dropna()
        last_sequence = data_cleaned['Close'].tail(self.config.SEQUENCE_LENGTH).values
        last_sequence_scaled = self.scaler.transform(last_sequence.reshape(-1, 1))
        current_sequence = last_sequence_scaled.reshape(1, self.config.SEQUENCE_LENGTH, 1)
        future_predictions = []
        for _ in range(days):
            next_pred = self.model.predict(current_sequence, verbose=0)
            future_predictions.append(next_pred[0, 0])
            current_sequence = np.roll(current_sequence, -1, axis=1)
            current_sequence[0, -1, 0] = next_pred[0, 0]
        future_predictions = np.array(future_predictions).reshape(-1, 1)
        future_predictions_actual = self.scaler.inverse_transform(future_predictions)
        last_date = pd.to_datetime(data_cleaned['Date'].iloc[-1])
        future_dates = pd.date_range(start=last_date + pd.Timedelta(days=1), periods=days, freq='D')
        return {
            'dates': [date.strftime('%Y-%m-%d') for date in future_dates],
            'prices': future_predictions_actual.flatten().tolist()
        }

    def calculate_metrics(self, actual, predicted):
        mse = mean_squared_error(actual, predicted)
        rmse = np.sqrt(mse)
        mae = mean_absolute_error(actual, predicted)
        mape = np.mean(np.abs((actual - predicted) / actual)) * 100
        r2 = r2_score(actual, predicted)
        return {
            'mse': float(mse),
            'rmse': float(rmse),
            'mae': float(mae),
            'mape': float(mape),
            'r2_score': float(r2)
        }

    def get_historical_data(self):
        if self.data is None:
            return None
        return {
            'dates': self.data['Date'].dt.strftime('%Y-%m-%d').tolist(),
            'open': self.data['Open'].tolist(),
            'high': self.data['High'].tolist(),
            'low': self.data['Low'].tolist(),
            'close': self.data['Close'].tolist(),
            'volume': self.data['Volume'].tolist()
        }

    def get_stock_info(self):
        return self.fetcher.get_stock_info()

    def get_recent_performance(self, days=30):
        if self.data is None:
            return None
        recent_data = self.data.tail(days)
        start_price = recent_data['Close'].iloc[0]
        end_price = recent_data['Close'].iloc[-1]
        change = end_price - start_price
        change_pct = (change / start_price) * 100
        return {
            'start_price': float(start_price),
            'end_price': float(end_price),
            'change': float(change),
            'change_pct': float(change_pct),
            'high': float(recent_data['High'].max()),
            'low': float(recent_data['Low'].min()),
            'avg_volume': float(recent_data['Volume'].mean())
        }
