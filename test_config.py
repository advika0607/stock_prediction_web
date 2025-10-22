"""
Test Config Loading
Run this to verify config is working before starting the app
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("\n" + "="*70)
print("  TESTING CONFIG IMPORT")
print("="*70)

try:
    from config import Config
    print("\n✓ Config imported successfully")
    
    # Test all required attributes
    print("\nTesting attributes:")
    
    attributes = [
        'SEQUENCE_LENGTH',
        'LSTM_UNITS',
        'DROPOUT_RATE',
        'EPOCHS',
        'BATCH_SIZE',
        'TRAIN_SIZE',
        'PREDICTION_DAYS',
        'MODEL_DIR',
        'DATA_DIR',
        'WATCHLIST_FILE',
        'BASE_DIR',
        'SECRET_KEY',
        'DEBUG',
        'DEMO_MODE'
    ]
    
    all_good = True
    for attr in attributes:
        if hasattr(Config, attr):
            value = getattr(Config, attr)
            print(f"  ✓ {attr:<20} = {value}")
        else:
            print(f"  ✗ {attr:<20} = MISSING!")
            all_good = False
    
    if all_good:
        print("\n" + "="*70)
        print("  ✅ ALL CONFIG ATTRIBUTES PRESENT")
        print("="*70)
        print("\nYou can now run: python app.py")
    else:
        print("\n" + "="*70)
        print("  ❌ SOME ATTRIBUTES MISSING")
        print("="*70)
        print("\nReplace config.py with the fixed version")
    
except ImportError as e:
    print(f"\n✗ Failed to import Config: {e}")
    print("\nMake sure config.py exists in the current directory")
except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n")