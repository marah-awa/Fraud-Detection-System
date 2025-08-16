# training_pipeline.py (Big Data Ready Version)

import pandas as pd
import pyodbc
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix
import joblib
from imblearn.over_sampling import SMOTE
import matplotlib.pyplot as plt
import seaborn as sns

def run_training():
    print("[Trainer] --- Starting Model Training Pipeline ---")
    
    # --- Configuration ---
    CONN_STR = r'DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost\SQLEXPRESS;DATABASE=FraudDetectionDB;Trusted_Connection=yes;'
    SQL_QUERY = "SELECT * FROM fraud_data;"
    MODEL_FILENAME = "fraud_detection_model.joblib"
    SAMPLE_SIZE = 150000 # <-- THE FIX: Define a sample size

    conn = None
    try:
        # 1. LOAD DATA
        print(f"[Trainer] 🔄 1. Loading data from SQL Server...")
        conn = pyodbc.connect(CONN_STR)
        df = pd.read_sql(SQL_QUERY, conn)
        print(f"[Trainer] ✅ Data loaded successfully with {len(df)} rows.")

        # === THE FIX: SAMPLE THE DATA IF IT'S TOO LARGE ===
        if len(df) > SAMPLE_SIZE:
            print(f"[Trainer] 🔄 Dataframe is too large ({len(df)} rows). Taking a random sample of {SAMPLE_SIZE} rows.")
            df = df.sample(n=SAMPLE_SIZE, random_state=42)
            print(f"[Trainer] ✅ Sampling complete. New dataframe size: {len(df)} rows.")
        # =================================================

        # 2. FEATURE ENGINEERING & PREPARATION
        print("\n[Trainer] 🔄 2. Preparing data for modeling...")
        # (The rest of the code is the same)
        df_prepared = df.drop(['TransactionID', 'customer', 'merchant', 'zipcodeOri', 'zipMerchant', 'category'], axis=1, errors='ignore')
        
        df_prepared['age'] = pd.Categorical(df_prepared['age'], categories=['0', '1', '2', '3', '4', '5', '6', 'U'])
        df_prepared['gender'] = pd.Categorical(df_prepared['gender'], categories=['E', 'F', 'M', 'U'])

        X = pd.get_dummies(df_prepared.drop('fraud', axis=1), columns=['age', 'gender'], drop_first=True)
        y = df_prepared['fraud']
        print(f"[Trainer] ✅ Data prepared. Feature shape: {X.shape}")

        # 3. HANDLE CLASS IMBALANCE WITH SMOTE
        print("\n[Trainer] 🔄 3. Balancing data using SMOTE...")
        smote = SMOTE(random_state=42)
        X_resampled, y_resampled = smote.fit_resample(X, y)
        print(f"[Trainer] ✅ SMOTE complete. Resampled data shape: {X_resampled.shape}")

        # 4. SPLIT DATA
        print("\n[Trainer] 🔄 4. Splitting data...")
        X_train, X_test, y_train, y_test = train_test_split(X_resampled, y_resampled, test_size=0.3, random_state=42, stratify=y_resampled)
        print("[Trainer] ✅ Data split successfully.")

        # 5. TRAIN MODEL
        print("\n[Trainer] 🔄 5. Training the RandomForestClassifier model...")
        model = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
        model.fit(X_train, y_train)
        print("[Trainer] ✅ Model training complete.")

        # 6. SAVE MODEL
        print(f"\n[Trainer] 🔄 6. Saving the trained model to '{MODEL_FILENAME}'...")
        joblib.dump(model, MODEL_FILENAME)
        print(f"[Trainer] ✅ Model saved successfully.")

        # 7. EVALUATE
        print("\n[Trainer] 🔄 7. Evaluating the model...")
        predictions = model.predict(X_test)
        print("\n--- Model Evaluation Report ---")
        print(classification_report(y_test, predictions, target_names=['Benign (0)', 'Fraud (1)']))
        
        return True # Indicate success

    except Exception as e:
        print(f"❌ AN ERROR OCCURRED during the training pipeline: {e}")
        return False # Indicate failure
    finally:
        if conn:
            conn.close()
            print("\n[Trainer] 🔌 Database connection closed.")

