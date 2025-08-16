# retrain_manager.py

import os
import pyodbc
from training_pipeline import run_training 

# --- Configuration ---
CONN_STR = r'DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost\SQLEXPRESS;DATABASE=FraudDetectionDB;Trusted_Connection=yes;'
SQL_QUERY = "SELECT * FROM fraud_data;"
MODEL_FILENAME = "fraud_detection_model.joblib"
RETRAIN_THRESHOLD = 1000
LAST_COUNT_FILE = "last_training_count.txt"

def get_current_db_count():
    """Gets the current number of rows in the fraud_data table."""
    try:
        conn = pyodbc.connect(CONN_STR)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM fraud_data")
        count = cursor.fetchone()[0]
        return count
    except Exception as e:
        print(f"Error getting DB count: {e}")
        return 0
    finally:
        if 'conn' in locals() and conn:
            conn.close()

def get_last_training_count():
    """Reads the number of rows from the last successful training run."""
    if not os.path.exists(LAST_COUNT_FILE):
        return 0
    try:
        with open(LAST_COUNT_FILE, 'r') as f:
            return int(f.read().strip())
    except:
        return 0

def update_last_training_count(count):
    """Saves the new row count after a successful training run."""
    with open(LAST_COUNT_FILE, 'w') as f:
        f.write(str(count))
    print(f"✅ Updated last training count to {count}.")

# --- Main Orchestrator Logic ---
if __name__ == "__main__":
    print("--- Retraining Manager Started ---")
    
    current_count = get_current_db_count()
    last_count = get_last_training_count()
    
    print(f"📊 Current records in DB: {current_count}")
    print(f"📈 Last training was at:   {last_count} records")
    
    new_records = current_count - last_count
    print(f"🆕 New records since last training: {new_records}")
    
    if new_records >= RETRAIN_THRESHOLD:
        print(f"\n❗️ Threshold of {RETRAIN_THRESHOLD} met. Initiating retraining...")
        
        # 2. Call the imported function
        training_successful = run_training()
        
        if training_successful:
            update_last_training_count(current_count)
        else:
            print("❌ Retraining failed. The count file will not be updated.")
            
    else:
        print("\n✅ No need to retrain at this time. System is up-to-date.")
        
    print("\n--- Retraining Manager Finished ---")
