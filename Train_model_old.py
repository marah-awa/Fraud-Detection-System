import pyodbc
import pandas as pd
from imblearn.over_sampling import SMOTE
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix
import seaborn as sns
import matplotlib.pyplot as plt
import joblib # <-- 1. Import the joblib library

# --- Configuration ---
CONN_STR = r'DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost\SQLEXPRESS;DATABASE=FraudDetectionDB;Trusted_Connection=yes;'
SQL_QUERY = "SELECT * FROM fraud_data;"
MODEL_FILENAME = "fraud_detection_model.joblib" # <-- 2. Define the model filename

try:
    # 1. LOAD DATA
    print("🔄 1. Loading data from SQL Server...")
    conn = pyodbc.connect(CONN_STR)
    df = pd.read_sql(SQL_QUERY, conn)
    print(f"✅ Data loaded successfully with {len(df)} rows.")

    # 2. FEATURE ENGINEERING & PREPARATION
    print("\n🔄 2. Preparing data for modeling...")
    df_prepared = df.drop(['TransactionID', 'customer', 'merchant', 'zipcodeOri', 'zipMerchant', 'category'], axis=1, errors='ignore')
    low_cardinality_cols = [col for col in df_prepared.columns if df_prepared[col].dtype == 'object' and df_prepared[col].nunique() < 10]
    X = pd.get_dummies(df_prepared.drop('fraud', axis=1), columns=low_cardinality_cols, drop_first=True)
    y = df_prepared['fraud']
    print(f"✅ Data prepared. Feature shape: {X.shape}")

    # 3. HANDLE CLASS IMBALANCE WITH SMOTE
    print("\n🔄 3. Balancing data using SMOTE...")
    smote = SMOTE(random_state=42)
    X_resampled, y_resampled = smote.fit_resample(X, y)
    print(f"✅ SMOTE complete. Resampled data shape: {X_resampled.shape}")

    # 4. SPLIT DATA INTO TRAINING AND TESTING SETS
    print("\n🔄 4. Splitting data into training and testing sets...")
    X_train, X_test, y_train, y_test = train_test_split(X_resampled, y_resampled, test_size=0.3, random_state=42, stratify=y_resampled)
    print("✅ Data split successfully.")

    # 5. TRAIN THE RANDOM FOREST MODEL
    print("\n🔄 5. Training the RandomForestClassifier model...")
    model = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
    model.fit(X_train, y_train)
    print("✅ Model training complete.")

    # 6. SAVE THE TRAINED MODEL
    # =================================================================
    print(f"\n🔄 6. Saving the trained model to '{MODEL_FILENAME}'...")
    joblib.dump(model, MODEL_FILENAME) # <-- 3. Use joblib.dump to save the model object
    print(f"✅ Model saved successfully.")
    # =================================================================

    # 7. EVALUATE THE MODEL
    print("\n🔄 7. Evaluating the model on the unseen test set...")
    predictions = model.predict(X_test)
    print("\n--- Model Evaluation Report ---")
    print("\nClassification Report:")
    print(classification_report(y_test, predictions, target_names=['Benign (0)', 'Fraud (1)']))
    print("\nConfusion Matrix:")
    cm = confusion_matrix(y_test, predictions)
    print(cm)
    
    # Visualize the confusion matrix
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=['Benign', 'Fraud'], yticklabels=['Benign', 'Fraud'])
    plt.title('Confusion Matrix')
    plt.ylabel('Actual Class')
    plt.xlabel('Predicted Class')
    plt.show()
    
    print("\n-----------------------------")

except Exception as e:
    print(f"❌ AN ERROR OCCURRED: {e}")
finally:
    if 'conn' in locals() and conn:
        conn.close()
        print("\n🔌 Database connection closed.")
