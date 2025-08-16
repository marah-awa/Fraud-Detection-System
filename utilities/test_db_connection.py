# 3_utilities/test_db_connection.py

import pyodbc
import sys

# --- Configuration ---
# Note: You might need to adjust this if you run the script from the root folder.
# For now, we assume it's run directly.
CONN_STR = r'DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost\SQLEXPRESS;DATABASE=FraudDetectionDB;Trusted_Connection=yes;'

def check_db_connection():
    """
    Attempts to connect to the SQL Server database and prints the status.
    """
    print("--- Database Connection Test Utility ---")
    print(f"Attempting to connect to the database...")
    
    try:
        # Attempt to connect with a short timeout
        conn = pyodbc.connect(CONN_STR, timeout=5)
        
        print("\n" + "="*50)
        print("✅✅✅ SUCCESS! Connection to the database was successful.")
        print("="*50 + "\n")
        
        # Optional: Print some details about the connection
        cursor = conn.cursor()
        print(f"SQL Server Version: {cursor.execute('SELECT @@VERSION;').fetchone()[0][:30]}...")
        print(f"Current Database: {cursor.execute('SELECT DB_NAME();').fetchone()[0]}")
        
        conn.close()
        print("\nConnection closed successfully.")
        return True

    except pyodbc.Error as ex:
        # Handle specific pyodbc errors
        sqlstate = ex.args[0]
        print("\n" + "!"*50)
        print("❌❌❌ FAILURE! Could not connect to the database.")
        print("!"*50 + "\n")
        print(f"Error Details: {ex}")
        print(f"SQLSTATE: {sqlstate}")
        print("\nCommon Troubleshooting Steps:")
        print("1. Is the SQL Server service running? Check services.msc.")
        print("2. Is the server name 'localhost\\SQLEXPRESS' correct?")
        print("3. Is the database name 'FraudDetectionDB' correct and does it exist?")
        print("4. Is the ODBC Driver 'ODBC Driver 17 for SQL Server' installed?")
        return False
        
    except Exception as e:
        # Handle other potential errors
        print("\n" + "!"*50)
        print("❌❌❌ AN UNEXPECTED ERROR OCCURRED.")
        print("!"*50 + "\n")
        print(f"Error Details: {e}")
        return False

if __name__ == "__main__":
    # This allows the script to be run directly from the command line
    check_db_connection()
