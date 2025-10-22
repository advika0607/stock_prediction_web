"""
Flask Application - Stock Price Prediction Web App
Uses Pre-trained Models - FIXED VERSION
"""

from flask import Flask, render_template, request, jsonify
import json
import os
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import Config
from utils.data_fetcher import DataFetcher
from utils.predictor import StockPredictor
import warnings
warnings.filterwarnings('ignore')

# Initialize Flask app
app = Flask(__name__)

# Load configuration
app.config.from_object(Config)

# Initialize app with config
Config.init_app(app)

# Print config for debugging
print(f"\n[DEBUG] Config loaded:")
print(f"  SEQUENCE_LENGTH: {app.config.get('SEQUENCE_LENGTH', 'NOT FOUND')}")
print(f"  MODEL_DIR: {app.config.get('MODEL_DIR', 'NOT FOUND')}")
print(f"  DEMO_MODE: {app.config.get('DEMO_MODE', False)}")

# Initialize watchlist file
watchlist_file = app.config.get('WATCHLIST_FILE', 'data/watchlist.json')
if not os.path.exists(watchlist_file):
    os.makedirs(os.path.dirname(watchlist_file), exist_ok=True)
    with open(watchlist_file, 'w') as f:
        json.dump([], f)


@app.route('/')
def index():
    """Home page"""
    return render_template('index.html')


@app.route('/predict')
def predict_page():
    """Prediction page"""
    ticker = request.args.get('ticker', '').upper()
    return render_template('predict.html', ticker=ticker)


@app.route('/watchlist')
def watchlist_page():
    """Watchlist page"""
    with open(watchlist_file, 'r') as f:
        watchlist = json.load(f)
    return render_template('watchlist.html', watchlist=watchlist)


@app.route('/dashboard/<ticker>')
def dashboard(ticker):
    """Dashboard page for specific stock"""
    return render_template('dashboard.html', ticker=ticker.upper())


# API Endpoints

@app.route('/api/search', methods=['POST'])
def search_stock():
    """Search for a stock"""
    data = request.get_json()
    ticker = data.get('ticker', '').upper()
    
    if not ticker:
        return jsonify({'success': False, 'error': 'No ticker provided'})
    
    try:
        fetcher = DataFetcher(ticker)
        info = fetcher.get_stock_info()
        
        if info is None:
            return jsonify({'success': False, 'error': 'Could not fetch stock information'})
        
        return jsonify({'success': True, 'info': info})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/predict', methods=['POST'])
def predict():
    """Generate prediction for a stock using pre-trained model"""
    data = request.get_json()
    ticker = data.get('ticker', '').upper()
    
    if not ticker:
        return jsonify({'success': False, 'error': 'No ticker provided'})
    
    try:
        print(f"\n[DEBUG] Starting prediction for {ticker}")
        
        # Create predictor with Config object
        predictor = StockPredictor(ticker, Config)
        
        # Fetch and prepare data
        print(f"[DEBUG] Fetching data...")
        if not predictor.fetch_and_prepare_data():
            return jsonify({'success': False, 'error': 'Could not fetch sufficient data'})
        
        print(f"[DEBUG] Data fetched successfully")
        
        # Load pre-trained model
        print(f"[DEBUG] Loading model...")
        model_loaded = predictor.load_model()
        
        if not model_loaded:
            return jsonify({
                'success': False, 
                'error': f'No pre-trained model found for {ticker}. Please train a model first or place models in: {Config.MODEL_DIR}'
            })
        
        print(f"[DEBUG] Model loaded successfully")
        
        # Make predictions using loaded model
        print(f"[DEBUG] Making predictions...")
        predictions, metrics = predictor.predict_with_loaded_model()
        
        if predictions is None:
            return jsonify({'success': False, 'error': 'Failed to generate predictions'})
        
        print(f"[DEBUG] Predictions generated")
        
        # Get future predictions
        print(f"[DEBUG] Generating future predictions...")
        future = predictor.predict_future(days=Config.PREDICTION_DAYS)
        
        # Get historical data
        historical = predictor.get_historical_data()
        
        # Get stock info
        info = predictor.get_stock_info()
        
        # Get recent performance
        performance = predictor.get_recent_performance(days=30)
        
        print(f"[DEBUG] Prediction complete for {ticker}")
        
        return jsonify({
            'success': True,
            'ticker': ticker,
            'info': info,
            'historical': historical,
            'future': future,
            'metrics': metrics,
            'performance': performance
        })
        
    except Exception as e:
        print(f"[ERROR] Prediction failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': f'Server error: {str(e)}'})


@app.route('/api/historical/<ticker>')
def get_historical(ticker):
    """Get historical data for a stock"""
    try:
        fetcher = DataFetcher(ticker.upper())
        data = fetcher.fetch_data(period='1y')
        
        if data is None:
            return jsonify({'success': False, 'error': 'Could not fetch data'})
        
        historical = {
            'dates': data['Date'].dt.strftime('%Y-%m-%d').tolist(),
            'open': data['Open'].tolist(),
            'high': data['High'].tolist(),
            'low': data['Low'].tolist(),
            'close': data['Close'].tolist(),
            'volume': data['Volume'].tolist()
        }
        
        return jsonify({'success': True, 'data': historical})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/check-model/<ticker>')
def check_model(ticker):
    """Check if pre-trained model exists for ticker"""
    ticker = ticker.upper()
    
    possible_paths = [
        f"{Config.MODEL_DIR}/{ticker}_lstm_model.h5",
        f"{Config.MODEL_DIR}/lstm_model.h5",
        f"models/{ticker}_lstm_model.h5",
        f"models/lstm_model.h5"
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return jsonify({'success': True, 'exists': True, 'path': path})
    
    return jsonify({'success': True, 'exists': False, 'message': 'No model found'})


@app.route('/api/watchlist/add', methods=['POST'])
def add_to_watchlist():
    """Add stock to watchlist"""
    data = request.get_json()
    ticker = data.get('ticker', '').upper()
    
    if not ticker:
        return jsonify({'success': False, 'error': 'No ticker provided'})
    
    with open(watchlist_file, 'r') as f:
        watchlist = json.load(f)
    
    if ticker in watchlist:
        return jsonify({'success': False, 'error': 'Stock already in watchlist'})
    
    watchlist.append(ticker)
    
    with open(watchlist_file, 'w') as f:
        json.dump(watchlist, f)
    
    return jsonify({'success': True, 'message': 'Added to watchlist'})


@app.route('/api/watchlist/remove', methods=['POST'])
def remove_from_watchlist():
    """Remove stock from watchlist"""
    data = request.get_json()
    ticker = data.get('ticker', '').upper()
    
    with open(watchlist_file, 'r') as f:
        watchlist = json.load(f)
    
    if ticker in watchlist:
        watchlist.remove(ticker)
    
    with open(watchlist_file, 'w') as f:
        json.dump(watchlist, f)
    
    return jsonify({'success': True, 'message': 'Removed from watchlist'})


@app.route('/api/watchlist/get')
def get_watchlist():
    """Get watchlist with current prices"""
    try:
        with open(watchlist_file, 'r') as f:
            watchlist = json.load(f)
        
        print(f"[DEBUG] Loading watchlist: {watchlist}")
        
        stocks = []
        for ticker in watchlist:
            try:
                print(f"[DEBUG] Fetching data for watchlist ticker: {ticker}")
                fetcher = DataFetcher(ticker)
                
                # Fetch historical data first to ensure we have something
                data = fetcher.fetch_data(period='1mo')
                
                # Then get info (which will use the data as fallback)
                info = fetcher.get_stock_info()
                
                if info and info.get('current_price', 0) > 0:
                    stocks.append(info)
                    print(f"[DEBUG] Added {ticker} to watchlist with price: ${info['current_price']}")
                else:
                    print(f"[WARNING] {ticker} has no valid price data")
                    # Add with default message
                    stocks.append({
                        'symbol': ticker,
                        'name': ticker,
                        'sector': 'N/A',
                        'industry': 'N/A',
                        'market_cap': 0,
                        'currency': 'USD',
                        'exchange': 'N/A',
                        'current_price': 0,
                        'previous_close': 0,
                        'day_high': 0,
                        'day_low': 0,
                        'volume': 0,
                        'avg_volume': 0,
                        '52_week_high': 0,
                        '52_week_low': 0,
                    })
            except Exception as e:
                print(f"[ERROR] Error loading {ticker}: {str(e)}")
                continue
        
        print(f"[DEBUG] Returning {len(stocks)} stocks to watchlist")
        return jsonify({'success': True, 'stocks': stocks})
        
    except Exception as e:
        print(f"[ERROR] Watchlist error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)})


@app.errorhandler(404)
def not_found(error):
    """404 error handler"""
    return render_template('index.html'), 404


@app.errorhandler(500)
def internal_error(error):
    """500 error handler"""
    return jsonify({'success': False, 'error': 'Internal server error'}), 500


if __name__ == '__main__':
    print("\n" + "="*70)
    print("  STARTING STOCK PREDICTION WEB APP")
    print("="*70)
    print(f"  Config: {Config.__name__}")
    print(f"  Debug: {Config.DEBUG}")
    print(f"  Model Dir: {Config.MODEL_DIR}")
    print(f"  Sequence Length: {Config.SEQUENCE_LENGTH}")
    print("="*70 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)


@app.route('/')
def index():
    """Home page"""
    return render_template('index.html')


@app.route('/predict')
def predict_page():
    """Prediction page"""
    ticker = request.args.get('ticker', '').upper()
    return render_template('predict.html', ticker=ticker)


@app.route('/watchlist')
def watchlist_page():
    """Watchlist page"""
    # Load watchlist
    with open(app.config['WATCHLIST_FILE'], 'r') as f:
        watchlist = json.load(f)
    
    return render_template('watchlist.html', watchlist=watchlist)


@app.route('/dashboard/<ticker>')
def dashboard(ticker):
    """Dashboard page for specific stock"""
    return render_template('dashboard.html', ticker=ticker.upper())


# API Endpoints

@app.route('/api/search', methods=['POST'])
def search_stock():
    """Search for a stock"""
    data = request.get_json()
    ticker = data.get('ticker', '').upper()
    
    if not ticker:
        return jsonify({'success': False, 'error': 'No ticker provided'})
    
    fetcher = DataFetcher(ticker)
    if not fetcher.validate_ticker():
        return jsonify({'success': False, 'error': 'Invalid ticker symbol'})
    
    info = fetcher.get_stock_info()
    if info is None:
        return jsonify({'success': False, 'error': 'Could not fetch stock information'})
    
    return jsonify({'success': True, 'info': info})


@app.route('/api/predict', methods=['POST'])
def predict():
    """Generate prediction for a stock using pre-trained model"""
    data = request.get_json()
    ticker = data.get('ticker', '').upper()
    
    if not ticker:
        return jsonify({'success': False, 'error': 'No ticker provided'})
    
    try:
        # Create predictor
        predictor = StockPredictor(ticker, app.config)
        
        # Fetch and prepare data
        if not predictor.fetch_and_prepare_data():
            return jsonify({'success': False, 'error': 'Could not fetch sufficient data'})
        
        # Load pre-trained model
        model_loaded = predictor.load_model()
        
        if not model_loaded:
            return jsonify({
                'success': False, 
                'error': f'No pre-trained model found for {ticker}. Please train a model first.'
            })
        
        # Make predictions using loaded model
        predictions, metrics = predictor.predict_with_loaded_model()
        
        if predictions is None:
            return jsonify({'success': False, 'error': 'Failed to generate predictions'})
        
        # Get future predictions
        future = predictor.predict_future(days=app.config['PREDICTION_DAYS'])
        
        # Get historical data
        historical = predictor.get_historical_data()
        
        # Get stock info
        info = predictor.get_stock_info()
        
        # Get recent performance
        performance = predictor.get_recent_performance(days=30)
        
        return jsonify({
            'success': True,
            'ticker': ticker,
            'info': info,
            'historical': historical,
            'future': future,
            'metrics': metrics,
            'performance': performance
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/historical/<ticker>')
def get_historical(ticker):
    """Get historical data for a stock"""
    try:
        fetcher = DataFetcher(ticker.upper())
        data = fetcher.fetch_data(period='1y')
        
        if data is None:
            return jsonify({'success': False, 'error': 'Could not fetch data'})
        
        historical = {
            'dates': data['Date'].dt.strftime('%Y-%m-%d').tolist(),
            'open': data['Open'].tolist(),
            'high': data['High'].tolist(),
            'low': data['Low'].tolist(),
            'close': data['Close'].tolist(),
            'volume': data['Volume'].tolist()
        }
        
        return jsonify({'success': True, 'data': historical})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/check-model/<ticker>')
def check_model(ticker):
    """Check if pre-trained model exists for ticker"""
    ticker = ticker.upper()
    
    possible_paths = [
        f"{app.config['MODEL_DIR']}/{ticker}_lstm_model.h5",
        f"{app.config['MODEL_DIR']}/lstm_model.h5",
        f"models/{ticker}_lstm_model.h5",
        f"models/lstm_model.h5"
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return jsonify({'success': True, 'exists': True, 'path': path})
    
    return jsonify({'success': True, 'exists': False, 'message': 'No model found'})


@app.route('/api/watchlist/add', methods=['POST'])
def add_to_watchlist():
    """Add stock to watchlist"""
    data = request.get_json()
    ticker = data.get('ticker', '').upper()
    
    if not ticker:
        return jsonify({'success': False, 'error': 'No ticker provided'})
    
    # Validate ticker
    fetcher = DataFetcher(ticker)
    if not fetcher.validate_ticker():
        return jsonify({'success': False, 'error': 'Invalid ticker symbol'})
    
    # Load current watchlist
    with open(app.config['WATCHLIST_FILE'], 'r') as f:
        watchlist = json.load(f)
    
    # Check if already in watchlist
    if ticker in watchlist:
        return jsonify({'success': False, 'error': 'Stock already in watchlist'})
    
    # Add to watchlist
    watchlist.append(ticker)
    
    # Save watchlist
    with open(app.config['WATCHLIST_FILE'], 'w') as f:
        json.dump(watchlist, f)
    
    return jsonify({'success': True, 'message': 'Added to watchlist'})


@app.route('/api/watchlist/remove', methods=['POST'])
def remove_from_watchlist():
    """Remove stock from watchlist"""
    data = request.get_json()
    ticker = data.get('ticker', '').upper()
    
    # Load current watchlist
    with open(app.config['WATCHLIST_FILE'], 'r') as f:
        watchlist = json.load(f)
    
    # Remove from watchlist
    if ticker in watchlist:
        watchlist.remove(ticker)
    
    # Save watchlist
    with open(app.config['WATCHLIST_FILE'], 'w') as f:
        json.dump(watchlist, f)
    
    return jsonify({'success': True, 'message': 'Removed from watchlist'})


@app.route('/api/watchlist/get')
def get_watchlist():
    """Get watchlist with current prices"""
    try:
        # Load watchlist
        with open(app.config['WATCHLIST_FILE'], 'r') as f:
            watchlist = json.load(f)
        
        # Get current data for each stock
        stocks = []
        for ticker in watchlist:
            fetcher = DataFetcher(ticker)
            info = fetcher.get_stock_info()
            if info:
                stocks.append(info)
        
        return jsonify({'success': True, 'stocks': stocks})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.errorhandler(404)
def not_found(error):
    """404 error handler"""
    return render_template('index.html'), 404


@app.errorhandler(500)
def internal_error(error):
    """500 error handler"""
    return jsonify({'success': False, 'error': 'Internal server error'}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)