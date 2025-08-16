# main.py (Final Corrected Version with Categorical Types)

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import joblib
import pandas as pd
import json
import os

# --- Pydantic Model ---
class Transaction(BaseModel):
    customer: str; step: int; age: str; gender: str; zipcodeOri: str
    merchant: str; zipMerchant: str; category: str; amount: float

app = FastAPI(title="Fraud Detection API")

# --- Configuration ---
MODEL_FILENAME = "fraud_detection_model.joblib"
# We no longer need EXPECTED_COLUMNS, but we'll keep it for reference
EXPECTED_COLUMNS = ['step', 'amount', "age_'1'", "age_'2'", "age_'3'", "age_'4'", "age_'5'", "age_'6'", "age_'U'", "gender_'F'", "gender_'M'", "gender_'U'"]
TRANSACTION_QUEUE_FILE = "transactions_queue.log"

model = None

def load_model():
    global model
    if model is None:
        print("[API] Model is not loaded. Attempting to load...")
        if not os.path.exists(MODEL_FILENAME):
            print(f"[API] FATAL ERROR: Model file '{MODEL_FILENAME}' not found!")
            raise HTTPException(status_code=500, detail=f"Model file not found: {MODEL_FILENAME}")
        try:
            model = joblib.load(MODEL_FILENAME)
            print("[API] Model loaded successfully.")
        except Exception as e:
            print(f"[API] FATAL ERROR: Could not load model. Reason: {e}")
            raise HTTPException(status_code=500, detail=f"Could not load model: {e}")

@app.on_event("startup")
def startup_event():
    print("[API] Server is starting up...")
    load_model()

@app.post("/predict")
def predict(transaction: Transaction):
    if not model:
        print("[API] ERROR: Predict called but model is not available.")
        raise HTTPException(status_code=500, detail="Model is not available, check server logs.")

    try:
        # --- Prediction Logic (THE FIX IS HERE) ---
        transaction_dict = transaction.model_dump()
        input_df = pd.DataFrame([transaction_dict])

        # === THE FIX: Define all possible categories before encoding ===
        # This ensures that all possible dummy columns are always created.
        input_df['age'] = pd.Categorical(input_df['age'], categories=['0', '1', '2', '3', '4', '5', '6', 'U'])
        input_df['gender'] = pd.Categorical(input_df['gender'], categories=['E', 'F', 'M', 'U'])
        # ==============================================================

        # Now, get_dummies will create all columns, filling missing ones with 0
        final_df = pd.get_dummies(input_df, columns=['age', 'gender'], drop_first=True)
        
        # Align columns just in case, to be perfectly safe
        final_df = final_df.reindex(columns=model.feature_names_in_, fill_value=0)

        prediction_result = model.predict(final_df)
        is_fraud = int(prediction_result[0])
        
        # --- Save to Queue File ---
        transaction_to_log = transaction.model_dump()
        transaction_to_log['fraud'] = is_fraud
        
        with open(TRANSACTION_QUEUE_FILE, 'a') as f:
            f.write(json.dumps(transaction_to_log) + '\n')
        
        return {"prediction": "Fraudulent" if is_fraud == 1 else "Benign"}

    except Exception as e:
        import traceback
        print(f"[API] ERROR during prediction: {e}")
        traceback.print_exc() # Print full error for debugging
        raise HTTPException(status_code=500, detail=f"An error occurred during prediction: {e}")
