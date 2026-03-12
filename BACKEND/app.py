from datetime import datetime
from flask import Flask, request, jsonify
import os
import pickle
import pandas as pd
import sqlite3
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# ensure database is initialized at import time (useful for tests and
# anything that imports the app module directly)
if not os.path.exists("transactions.db"):
    try:
        import create_db  # creates tables if needed
    except Exception:
        pass

# -------------------------------------------------
# LOAD MODELS
# -------------------------------------------------
base_dir = os.path.dirname(os.path.abspath(__file__))
model_dir = os.path.join(base_dir, "model")

logistic_model = pickle.load(open(os.path.join(model_dir, "logistic_model.pkl"), "rb"))
rf_model = pickle.load(open(os.path.join(model_dir, "random_forest_model.pkl"), "rb"))
scaler = pickle.load(open(os.path.join(model_dir, "scaler.pkl"), "rb"))
encoders = pickle.load(open(os.path.join(model_dir, "encoders.pkl"), "rb"))

# -------------------------------------------------
# DATABASE CONNECTION
# -------------------------------------------------
def get_db():
    return sqlite3.connect("transactions.db")


# -------------------------------------------------
# PREDICT ROUTE
# -------------------------------------------------
@app.route("/predict", methods=["POST"])
def predict():

    data = request.get_json(force=True)

    # Map frontend fields to training data columns
    # User_ID in training data is numeric; try to coerce, fall back to 0
    uid_raw = data.get("User_ID", 0)
    try:
        uid_val = int(uid_raw)
    except Exception:
        uid_val = 0
    input_df = pd.DataFrame([{
        "User_ID": uid_val,
        "Transaction_Amount": float(data.get("Transaction_Amount", 0)),
        "Transaction_Type": "Transfer",  # default
        "Time_of_Transaction": 12.0,  # default time
        "Device_Used": data.get("Device", "Mobile"),
        "Location": data.get("Location", "Unknown"),
        "Previous_Fraudulent_Transactions": 0,  # default
        "Account_Age": 30,  # default
        "Number_of_Transactions_Last_24H": 5,  # default
        "Payment_Method": data.get("Payment_Method", "UPI")
    }])

    # Fill any missing values
    input_df = input_df.fillna(0)

    # Encode categorical variables using trained encoders
    categorical_cols = ['Transaction_Type', 'Device_Used', 'Location', 'Payment_Method']
    for col in encoders:
        val = input_df[col].iloc[0]

        if val not in encoders[col].classes_:
            val = encoders[col].classes_[0]

        input_df[col] = encoders[col].transform([val])

    # Select features in the same order as training data
    feature_cols = ["User_ID", "Transaction_Amount", "Transaction_Type", "Time_of_Transaction", 
                   "Device_Used", "Location", "Previous_Fraudulent_Transactions", "Account_Age", 
                   "Number_of_Transactions_Last_24H", "Payment_Method"]
    
    input_data = input_df[feature_cols]

    # Scale for logistic regression
    scaled_input = scaler.transform(input_data)

    # Make predictions
    log_pred = logistic_model.predict(scaled_input)[0]
    rf_pred = rf_model.predict(input_data)[0]

    # Majority voting
    final_pred = int((log_pred + rf_pred) >= 1)

    if final_pred == 1:
        risk_level = "HIGH"
        risk_score = 95
    else:
        risk_level = "LOW"
        risk_score = 15

    # -------------------------------------------------
    # STORE TRANSACTION IN DATABASE
    # -------------------------------------------------
    conn = get_db()

    conn.execute(
        """
        INSERT INTO transactions
        (timestamp, user_id, transaction_amount, transaction_type, device_used, location, payment_method, fraud_risk_score, risk_level)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            data.get("User_ID", "N/A"),
            data.get("Transaction_Amount", 0),
            data.get("Transaction_Type", "Transfer"),
            data.get("Device", "N/A"),
            data.get("Location", "N/A"),
            data.get("Payment_Method", "N/A"),
            risk_score,
            risk_level
        )
    )

    conn.commit()
    conn.close()

    return jsonify({
        "fraud_prediction": final_pred,
        "risk_level": risk_level,
        "fraud_risk_score": risk_score
    })


# -------------------------------------------------
# GET TRANSACTION HISTORY
# -------------------------------------------------
@app.route("/transactions", methods=["GET"])
def get_transactions():

    conn = get_db()

    rows = conn.execute(
        "SELECT * FROM transactions ORDER BY timestamp DESC"
    ).fetchall()

    conn.close()

    results = []

    for r in rows:
        results.append({
            "timestamp": r[1],
            "user_id": r[2],
            "transaction_amount": r[3],
            "transaction_type": r[4],
            "device_used": r[5],
            "location": r[6],
            "payment_method": r[7],
            "fraud_risk_score": r[8],
            "risk_level": r[9]
        })

    return jsonify({"transactions": results})


# -------------------------------------------------
# HOME
# -------------------------------------------------
@app.route("/")
def home():
    return "UPI Fraud Detection Backend Running"


# -------------------------------------------------
# LOGIN ENDPOINT
# -------------------------------------------------
@app.route("/login", methods=["POST"])
def login():
    data = request.get_json(force=True)
    username = data.get("username", "")
    
    if not username:
        return jsonify({"error": "Username required"}), 400
    
    conn = get_db()
    conn.execute(
        "INSERT INTO user_logins (username, login_time) VALUES (?, ?)",
        (username, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    )
    conn.commit()
    conn.close()
    
    return jsonify({"message": "Login recorded", "username": username})


# -------------------------------------------------
# GET LOGIN HISTORY
# -------------------------------------------------
@app.route("/logins", methods=["GET"])
def get_logins():
    conn = get_db()
    rows = conn.execute(
        "SELECT username, login_time FROM user_logins ORDER BY login_time DESC LIMIT 50"
    ).fetchall()
    conn.close()
    
    logins = [{"username": r[0], "login_time": r[1]} for r in rows]
    
    return jsonify({"logins": logins})


# -------------------------------------------------
# SIMULATION ENDPOINT (test data generation)
# -------------------------------------------------
@app.route("/simulate", methods=["POST"])
def simulate():
    import random
    
    conn = get_db()
    
    # Generate 3 random test transactions
    for _ in range(3):
        risk = random.choice(["LOW", "MEDIUM", "HIGH"])
        score = random.choice([15, 45, 85]) if risk == "LOW" else (random.choice([35, 55]) if risk == "MEDIUM" else 95)
        
        conn.execute(
            """
            INSERT INTO transactions
            (timestamp, user_id, transaction_amount, transaction_type, device_used, location, payment_method, fraud_risk_score, risk_level)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                f"UPI{random.randint(1000, 9999)}",
                random.randint(1000, 50000),
                "Transfer",
                random.choice(["Mobile", "Web", "Desktop"]),
                random.choice(["Delhi", "Mumbai", "Bangalore", "Hyderabad"]),
                "UPI",
                score,
                risk
            )
        )
    
    conn.commit()
    conn.close()
    
    return jsonify({"message": "Simulation data generated"})


# -------------------------------------------------
# GET STATISTICS
# -------------------------------------------------
@app.route("/stats", methods=["GET"])
def get_stats():
    conn = get_db()
    
    total_result = conn.execute("SELECT COUNT(*) FROM transactions").fetchone()
    total_transactions = total_result[0] if total_result else 0
    
    fraud_result = conn.execute("SELECT COUNT(*) FROM transactions WHERE risk_level = 'HIGH'").fetchone()
    fraud_transactions = fraud_result[0] if fraud_result else 0
    
    safe_result = conn.execute("SELECT COUNT(*) FROM transactions WHERE risk_level = 'LOW'").fetchone()
    safe_transactions = safe_result[0] if safe_result else 0
    
    conn.close()
    
    return jsonify({
        "total_transactions": total_transactions,
        "fraud_transactions": fraud_transactions,
        "safe_transactions": safe_transactions
    })


# -------------------------------------------------
# RUN SERVER
# -------------------------------------------------
if __name__ == "__main__":
    print("Starting UPI Fraud Detection Backend...")
    app.run(debug=True, port=5001)