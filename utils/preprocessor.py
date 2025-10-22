"""
Data Preprocessor - Clean and prepare data
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler


class DataPreprocessor:
    """Preprocess stock data"""
    
    def __init__(self, data):
        self.data = data.copy()
        self.scaler = MinMaxScaler(feature_range=(0, 1))
    
    def clean_data(self):
        """Clean and prepare data"""
        # Handle missing values
        self.data.fillna(method='ffill', inplace=True)
        self.data.fillna(method='bfill', inplace=True)
        
        # Remove duplicates
        self.data.drop_duplicates(inplace=True)
        
        # Sort by date
        if 'Date' in self.data.columns:
            self.data.sort_values('Date', inplace=True)
            self.data.reset_index(drop=True, inplace=True)
        
        return self.data
    
    def add_features(self):
        """Add basic features"""
        # Returns
        self.data['Returns'] = self.data['Close'].pct_change()
        
        # Moving averages
        self.data['MA_5'] = self.data['Close'].rolling(window=5).mean()
        self.data['MA_20'] = self.data['Close'].rolling(window=20).mean()
        self.data['MA_50'] = self.data['Close'].rolling(window=50).mean()
        
        # Volatility
        self.data['Volatility'] = self.data['Returns'].rolling(window=20).std()
        
        # Price change
        self.data['Price_Change'] = self.data['Close'].diff()
        
        return self.data
    
    def prepare_lstm_data(self, sequence_length=60, target_col='Close'):
        """Prepare data for LSTM"""
        # Drop NaN values
        data_cleaned = self.data.dropna()
        
        # Scale data
        values = data_cleaned[[target_col]].values
        scaled_data = self.scaler.fit_transform(values)
        
        # Create sequences
        X, y = [], []
        for i in range(sequence_length, len(scaled_data)):
            X.append(scaled_data[i-sequence_length:i, 0])
            y.append(scaled_data[i, 0])
        
        X = np.array(X)
        y = np.array(y)
        
        # Reshape for LSTM [samples, time steps, features]
        X = np.reshape(X, (X.shape[0], X.shape[1], 1))
        
        return X, y, self.scaler
    
    def split_data(self, X, y, train_size=0.8):
        """Split into train and test sets"""
        split_idx = int(len(X) * train_size)
        
        X_train = X[:split_idx]
        y_train = y[:split_idx]
        X_test = X[split_idx:]
        y_test = y[split_idx:]
        
        return X_train, y_train, X_test, y_test
    
    def get_data(self):
        """Get processed data"""
        return self.data