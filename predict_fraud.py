import joblib
import pandas as pd

# --- Configuration ---
MODEL_FILENAME = "fraud_detection_model.joblib"

# --- CORRECTED COLUMN LIST ---
# These names now EXACTLY match the names from the training process.
# Notice the quotes around the numbers for 'age'.
EXPECTED_COLUMNS = [
    'step', 'amount', 
    "age_'1'", "age_'2'", "age_'3'", "age_'4'", "age_'5'", "age_'6'", "age_'U'",
    "gender_'F'", "gender_'M'", "gender_'U'"
]

def predict_single_transaction(transaction_data):
    """
    Predicts if a single transaction is fraudulent or not.
    """
    print("🔄 1. Loading the pre-trained model...")
    try:
        model = joblib.load(MODEL_FILENAME)
        print(f"✅ Model '{MODEL_FILENAME}' loaded successfully.")
    except FileNotFoundError:
        return f"❌ ERROR: Model file not found at '{MODEL_FILENAME}'. Please train and save the model first."
    
    print("\n🔄 2. Preparing the new transaction data...")
    
    # --- ENSURE DATA TYPES ARE CORRECT ---
    # Explicitly set the data types to match the training data.
    # 'age' and 'gender' were objects (strings) during training.
    transaction_data_typed = {
        'step': int(transaction_data['step']),
        'amount': float(transaction_data['amount']),
        'age': str(transaction_data['age']),
        'gender': str(transaction_data['gender'])
    }
    
    input_df = pd.DataFrame([transaction_data_typed])

    # One-Hot Encode the categorical features
    input_df_encoded = pd.get_dummies(input_df)
    
    # Align columns with the training data
    final_df = input_df_encoded.reindex(columns=EXPECTED_COLUMNS, fill_value=0)
    
    print("✅ New data prepared for prediction.")
    print("   - Data to be predicted:\n", final_df)

    print("\n🔄 3. Making a prediction...")
    
    prediction_result = model.predict(final_df)
    prediction_proba = model.predict_proba(final_df)

    print("✅ Prediction complete.")

    # 4. Return the result
    if prediction_result[0] == 1:
        fraud_probability = prediction_proba[0][1] * 100
        return f"🚨 RESULT: Fraudulent (Confidence: {fraud_probability:.2f}%)"
    else:
        benign_probability = prediction_proba[0][0] * 100
        return f"👍 RESULT: Benign (Confidence: {benign_probability:.2f}%)"

# --- EXAMPLE OF HOW TO USE THE FUNCTION ---
if __name__ == "__main__":
    
    print("--- Testing Example 1: Suspicious Transaction ---")
    new_transaction_1 = {
        'step': 20,
        'age': '3',      # Age group 36-45
        'gender': 'M',   # Male
        'amount': 2500.00 # High amount
    }
    result_1 = predict_single_transaction(new_transaction_1)
    print(f"\n{result_1}\n")
    
    print("==================================================\n")
    
    print("--- Testing Example 2: Normal Transaction ---")
    new_transaction_2 = {
        'step': 150,
        'age': '2',      # Age group 26-35
        'gender': 'F',   # Female
        'amount': 35.50  # Low amount
    }
    result_2 = predict_single_transaction(new_transaction_2)
    print(f"\n{result_2}\n")
