# database_worker.py (Back to Basics Version)
import pyodbc
import json
import time
import os

# --- Configuration ---
CONN_STR = r'DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost\SQLEXPRESS;DATABASE=FraudDetectionDB;Trusted_Connection=yes;'
TRANSACTION_QUEUE_FILE = "transactions_queue.log"

def process_queue():
    if not os.path.exists(TRANSACTION_QUEUE_FILE):
        return # Wait silently if no file

    # Read all lines and then clear the file to avoid re-processing
    with open(TRANSACTION_QUEUE_FILE, 'r+') as f:
        lines = f.readlines()
        f.seek(0)
        f.truncate()

    if not lines:
        return

    print(f"[Worker] Found {len(lines)} new transaction(s). Attempting to process...")
    
    conn = None
    try:
        print("[Worker] Attempting to connect to database...")
        conn = pyodbc.connect(CONN_STR)
        cursor = conn.cursor()
        print("[Worker] Database connection successful.")
        
        success_count = 0
        for line in lines:
            try:
                data = json.loads(line)
                sql = "INSERT INTO fraud_data (customer, step, age, gender, zipcodeOri, merchant, zipMerchant, category, amount, fraud) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
                values = (data['customer'], data['step'], data['age'], data['gender'], data['zipcodeOri'], data['merchant'], data['zipMerchant'], data['category'], data['amount'], data['fraud'])
                cursor.execute(sql, values)
                success_count += 1
            except Exception as e:
                print(f"[Worker] ERROR inserting line: {line.strip()}. Reason: {e}")

        conn.commit()
        print(f"[Worker] Successfully inserted {success_count}/{len(lines)} transactions.")

    except pyodbc.Error as ex:
        print(f"[Worker] FATAL DATABASE ERROR: {ex}")
        # If connection fails, write the lines back to the file so we don't lose them
        with open(TRANSACTION_QUEUE_FILE, 'a') as f:
            f.writelines(lines)
        print("[Worker] Transactions returned to queue file for next attempt.")
    finally:
        if conn:
            conn.close()
            print("[Worker] Database connection closed.")

if __name__ == "__main__":
    print("--- Database Worker Started ---")
    print("Watching for new transactions. Press Ctrl+C to stop.")
    while True:
        process_queue()
        time.sleep(5) # Check every 5 seconds
