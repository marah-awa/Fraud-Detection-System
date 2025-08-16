# main.py (Safer Version - Writes to a file)

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import joblib
import pandas as pd
import json # Import json library

# --- Pydantic Model ---
class Transaction(BaseModel):
    customer: str; step: int; age: str; gender: str; zipcodeOri: str
    merchant: str; zipMerchant: str; category: str; amount: float

app = FastAPI(title="Fraud Detection API")

# --- Load Model ---
MODEL_FILENAME = "fraud_detection_model.joblib"
try:
    model = joblib.load(MODEL_FILENAME)
    print(f"✅ Model '{MODEL_FILENAME}' loaded successfully.")
except Exception as e:
    model = None; print(f"❌ FATAL: Could not load model. Reason: {e}")

EXPECTED_COLUMNS = [
    'step', 'amount', "age_'1'", "age_'2'", "age_'3'", "age_'4'", 
    "age_'5'", "age_'6'", "age_'U'", "gender_'F'", "gender_'M'", "gender_'U'"
]

# --- The file that will act as our queue ---
TRANSACTION_QUEUE_FILE = "transactions_queue.log"

@app.post("/predict")
def predict(transaction: Transaction):
    if not model:
        raise HTTPException(status_code=500, detail="Model is not loaded.")

    # 1. PREDICTION LOGIC (No changes here)
    transaction_dict = transaction.model_dump()
    input_df = pd.DataFrame([transaction_dict])
    input_df_encoded = pd.get_dummies(input_df)
    final_df = input_df_encoded.reindex(columns=EXPECTED_COLUMNS, fill_value=0)
    prediction_result = model.predict(final_df)
    is_fraud = int(prediction_result[0])
    
    # 2. SAVE TO THE QUEUE FILE (INSTEAD OF DATABASE)
    # =================================================================
    transaction_to_log = transaction.model_dump()
    transaction_to_log['fraud'] = is_fraud # Add the prediction result
    
    try:
        # Open the file in 'append' mode and write the transaction as a single JSON line
        with open(TRANSACTION_QUEUE_FILE, 'a') as f:
            f.write(json.dumps(transaction_to_log) + '\n')
        saved_to_queue = True
    except Exception as e:
        print(f"⚠️ WARNING: Could not write to queue file. Reason: {e}")
        saved_to_queue = False
    # =================================================================

    # 3. RETURN RESPONSE
    return {
        "prediction": "Fraudulent" if is_fraud == 1 else "Benign",
        "is_fraud": is_fraud,
        "status": "Transaction has been queued for database insertion." if saved_to_queue else "Failed to queue transaction."
    }
