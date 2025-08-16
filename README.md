# Real-Time Fraud Detection System

## 1. Project Overview

This project implements a comprehensive, end-to-end machine learning system designed to detect fraudulent financial transactions in real-time. The system goes beyond a simple prediction model by incorporating a full data and model lifecycle, including:

-   A **RESTful API** to receive new transactions and predict their legitimacy.
-   A robust mechanism to **log all incoming transactions** into a SQL Server database.
-   An **automated retraining pipeline** that periodically updates the model with new data, ensuring its performance improves over time as new patterns emerge.

The core of the system is a `RandomForestClassifier` model, which is trained on a dataset balanced with the SMOTE technique to handle the inherent class imbalance found in fraud detection scenarios.

---

## 2. Project Structure

The project is organized into modular components to ensure clarity, maintainability, and separation of concerns.

```
/
├── .gitignore
├── README.md
├── requirements.txt
│
├── 1_data_ingestion_and_retraining/
│   ├── training_pipeline.py
│   ├── retrain_manager.py
│   └── simulate_new_data.py
│
├── 2_prediction_service/
│   ├── main.py
│   ├── database_worker.py
│   └── fraud_detection_model.joblib
│
└── 3_utilities/
    └── test_db_connection.py
```

-   **`1_data_ingestion_and_retraining/`**: Contains all scripts related to the initial data handling, model training, and the continuous learning cycle.
-   **`2_prediction_service/`**: Holds the real-time components, including the API server and the background database worker. The pre-trained model is also stored here.
-   **`3_utilities/`**: Includes helper scripts for diagnostics and testing, such as verifying the database connection.
-   **`requirements.txt`**: A list of all Python dependencies required to run the project.
-   **`fraud_detection_model.joblib`**: The serialized, pre-trained machine learning model, ready for use by the prediction service.

---

## 3. Module Guide & How to Run

### A. Initial Setup

1.  **Prerequisites**: Ensure you have a running SQL Server instance and have created the necessary database and table structure.

2.  **Environment Setup**: Create a Python virtual environment and install all required dependencies.
    ```bash
    # Create and activate the virtual environment
    python -m venv venv
    .\venv\Scripts\activate

    # Install dependencies from the requirements file
    python -m pip install -r requirements.txt
    ```

### B. First-Time Model Training

-   **Responsible Script**: `training_pipeline.py`
-   **Description**: This script handles the entire model creation process. It loads the complete dataset from SQL Server, preprocesses the data, balances the classes using SMOTE to prevent bias towards the majority class, trains a `RandomForestClassifier`, evaluates its performance, and saves the final model object to `fraud_detection_model.joblib`.
-   **How to Run**: This script is not meant to be run directly. It is called by the `retrain_manager.py`.

### C. Running the Real-Time Prediction Service

The prediction service is composed of two components that must run simultaneously in separate terminals.

1.  **The API Server:**
    -   **Responsible Script**: `main.py`
    -   **Description**: This script launches a Uvicorn web server that exposes a `/predict` endpoint. When it receives a transaction via an HTTP POST request, it loads the trained model, predicts the transaction's status, and places the transaction data into a queue file (`transactions_queue.log`) for asynchronous database insertion.
    -   **How to Run (in Terminal 1):**
        ```bash
        # Navigate to the project root and activate the venv
        cd path\to\your\project
        .\venv\Scripts\activate

        # Run the Uvicorn server
        python -m uvicorn 2_prediction_service.main:app --reload
        ```

2.  **The Database Worker:**
    -   **Responsible Script**: `database_worker.py`
    -   **Description**: This script runs as a background process, continuously monitoring the queue file. When new transactions appear, it reads them, inserts them into the SQL Server database in a robust manner, and then clears them from the queue. This decouples the database write operation from the API response, ensuring the API remains fast and responsive.
    -   **How to Run (in Terminal 2):**
        ```bash
        # Navigate to the project root and activate the venv
        cd path\to\your\project
        .\venv\Scripts\activate

        # Run the worker
        python 2_prediction_service/database_worker.py
        ```

### D. The Automated Retraining Mechanism

This system is designed to learn from new data over time.

1.  **Simulating New Data (for demonstration):**
    -   **Responsible Script**: `simulate_new_data.py`
    -   **Description**: A utility script that generates 1,001 fake transactions and adds them to the queue, mimicking the arrival of new data in a production environment.
    -   **How to Run:**
        ```bash
        python 1_data_ingestion_and_retraining/simulate_new_data.py
        ```

2.  **The Retraining Manager:**
    -   **Responsible Script**: `retrain_manager.py`
    -   **Description**: This is the core of the continuous learning system. When executed, it checks the total number of records in the database against a log of the last training count. If the number of new records exceeds a predefined threshold (e.g., 1000), it automatically triggers the `training_pipeline.py` script. This retrains the model on the entire, updated dataset and overwrites the old `fraud_detection_model.joblib` file with the new, improved version.
    -   **How to Run:**
        ```bash
        python 1_data_ingestion_and_retraining/retrain_manager.py
        ```

---

## 4. Results & Performance

The trained model demonstrates excellent performance, achieving an **accuracy and F1-score of over 94%** on the test set. The system architecture is robust, modular, and scalable, providing a solid foundation for a real-world fraud detection application. The automated retraining loop ensures that the model's accuracy will not degrade over time and can adapt to new, emerging fraud patterns.

---

## 5. Dockerization (Optional)

This repository also includes a `Dockerfile` to allow for easy containerization of the prediction service. This is useful for deploying the application in a consistent and isolated environment, eliminating "it works on my machine" problems.

### How to Build and Run the Docker Container:

1.  **Build the image:**
    ```bash
    docker build -t fraud-api .
    ```

2.  **Run the container:**
    ```bash
    docker run -p 8000:8000 fraud-api
    ```

