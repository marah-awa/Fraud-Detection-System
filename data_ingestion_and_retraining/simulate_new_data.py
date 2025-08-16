# simulate_new_data.py
import pyodbc

# --- Configuration ---
CONN_STR = r'DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost\SQLEXPRESS;DATABASE=FraudDetectionDB;Trusted_Connection=yes;'

def add_batch_of_transactions(number_of_records):
    """Adds a specified number of dummy transactions to the database."""
    print(f"🔄 Attempting to add {number_of_records} new dummy records...")
    try:
        conn = pyodbc.connect(CONN_STR)
        cursor = conn.cursor()

        # A sample transaction to be inserted repeatedly
        # We will change the customer ID to ensure it's unique
        sample_transaction = {
            'step': 900, 'age': '1', 'gender': 'U', 'zipcodeOri': '12345',
            'merchant': 'M_SIMULATED', 'zipMerchant': '12345',
            'category': 'es_simulated', 'amount': 10.0, 'fraud': 0
        }

        sql_insert = """
            INSERT INTO fraud_data (customer, step, age, gender, zipcodeOri, merchant, zipMerchant, category, amount, fraud)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        for i in range(number_of_records):
            # Create a unique customer ID for each new record
            customer_id = f"C_SIM_{i}"
            row_values = (
                customer_id, sample_transaction['step'], sample_transaction['age'],
                sample_transaction['gender'], sample_transaction['zipcodeOri'], sample_transaction['merchant'],
                sample_transaction['zipMerchant'], sample_transaction['category'], sample_transaction['amount'],
                sample_transaction['fraud']
            )
            cursor.execute(sql_insert, row_values)

        conn.commit()
        print(f"✅ Successfully added {number_of_records} new records.")

    except Exception as e:
        print(f"❌ Database Error: {e}")
    finally:
        if 'conn' in locals() and conn:
            conn.close()

# --- Run the simulation ---
if __name__ == "__main__":
    # We'll add 1001 records to be sure we cross the 1000 threshold
    add_batch_of_transactions(1001)

