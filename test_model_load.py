# test_model_load.py

import joblib
import pandas as pd # We need pandas as scikit-learn models often depend on it
import sklearn # We need to import sklearn itself

MODEL_FILENAME = "fraud_detection_model.joblib"

print("--- Model Load Test Script ---")
print(f"🔄 Attempting to load model from: {MODEL_FILENAME}")

try:
    # This is the line we are testing
    model = joblib.load(MODEL_FILENAME)
    
    # If it succeeds, print information about the model
    print("\n✅✅✅ SUCCESS! Model loaded successfully! ✅✅✅")
    print("\n--- Model Information ---")
    print(f"Model Type: {type(model)}")
    
    # Check for some attributes to be sure it's a valid model
    if hasattr(model, 'n_estimators'):
        print(f"Number of Estimators: {model.n_estimators}")
    if hasattr(model, 'feature_names_in_'):
        print(f"Number of Features Expected: {len(model.feature_names_in_)}")
    
except Exception as e:
    print("\n❌❌❌ FAILURE! An error occurred while loading the model. ❌❌❌")
    print(f"\n--- Error Details ---")
    print(f"Error Type: {type(e)}")
    print(f"Error Message: {e}")
    # This will print the full traceback for detailed debugging
    import traceback
    traceback.print_exc()

print("\n--- End of Test Script ---")
