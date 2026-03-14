from datetime import datetime
from flask import Flask, request, jsonify
import os
import pickle
import pandas as pd
import sqlite3
from flask_cors import CORS

# -------------------------------------------------
# APP CONFIG
# -------------------------------------------------

app = Flask(__name__)
CORS(app)

base_dir = os.path.dirname(os.path.abspath(__file__))

DATASET_PATH = os.path.join(base_dir, "data", "fraud_dataset.csv")
MODEL_DIR = os.path.join(base_dir, "model")

# -------------------------------------------------
# LOAD MODELS
# -------------------------------------------------

logistic_model = pickle.load(open(os.path.join(MODEL_DIR, "logistic_model.pkl"), "rb"))
rf_model = pickle.load(open(os.path.join(MODEL_DIR, "random_forest_model.pkl"), "rb"))
scaler = pickle.load(open(os.path.join(MODEL_DIR, "scaler.pkl"), "rb"))
encoders = pickle.load(open(os.path.join(MODEL_DIR, "encoders.pkl"), "rb"))

# -------------------------------------------------
# DATABASE CONNECTION
# -------------------------------------------------

def get_db():
    return sqlite3.connect("transactions.db")


# -------------------------------------------------
# HOME ROUTE
# -------------------------------------------------

@app.route("/")
def home():
    return "UPI Fraud Detection Backend Running"


# -------------------------------------------------
# PREDICT ROUTE
# -------------------------------------------------

@app.route("/predict", methods=["POST"])
def predict():

    data = request.get_json(force=True)

    user_id = data.get("User_ID")
    amount = float(data.get("Transaction_Amount", 0))
    device = data.get("Device", "Mobile")
    location = data.get("Location", "Unknown")
    transaction_type = data.get("Transaction_Type", "Transfer")
    payment_method = data.get("Payment_Method", "UPI")
    hour = datetime.now().hour

    fraud_pred = 0
    risk_level = "LOW"
    risk_score = 10
    source = "ML_MODEL"

    # -------------------------------
    # STEP 1 : CHECK CSV DATASET
    # -------------------------------
    try:

        df = pd.read_csv(DATASET_PATH)

        match = df[df["User_ID"].astype(str) == str(user_id)]

        if not match.empty:

            fraud_label = int(match.iloc[0]["Fraudulent"])

            fraud_pred = fraud_label
            source = "CSV_DATASET"

            if fraud_label == 1:
                risk_level = "HIGH"
                risk_score = 95
            else:
                risk_level = "LOW"
                risk_score = 10

    except Exception as e:
        print("CSV lookup error:", e)

    # -------------------------------
    # STEP 2 : ML PREDICTION
    # -------------------------------
    if source != "CSV_DATASET":

        input_df = pd.DataFrame([{
            "User_ID": 0,
            "Transaction_Amount": amount,
            "Transaction_Type": transaction_type,
            "Time_of_Transaction": hour,
            "Device_Used": device,
            "Location": location,
            "Previous_Fraudulent_Transactions": 0,
            "Account_Age": 30,
            "Number_of_Transactions_Last_24H": 3,
            "Payment_Method": payment_method
        }])

        for col in encoders:

            val = input_df[col].iloc[0]

            if val not in encoders[col].classes_:
                val = encoders[col].classes_[0]

            input_df[col] = encoders[col].transform([val])

        feature_cols = [
            "User_ID",
            "Transaction_Amount",
            "Transaction_Type",
            "Time_of_Transaction",
            "Device_Used",
            "Location",
            "Previous_Fraudulent_Transactions",
            "Account_Age",
            "Number_of_Transactions_Last_24H",
            "Payment_Method"
        ]

        X = input_df[feature_cols]

        scaled = scaler.transform(X)

        log_prob = logistic_model.predict_proba(scaled)[0][1]
        rf_prob = rf_model.predict_proba(X)[0][1]

        avg_prob = (log_prob + rf_prob) / 2

        risk_score = int(avg_prob * 100)

        if avg_prob >= 0.7:
            risk_level = "HIGH"
        elif avg_prob >= 0.4:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"

        fraud_pred = 1 if avg_prob >= 0.5 else 0

    # -------------------------------
    # STORE TRANSACTION IN DATABASE
    # -------------------------------

    conn = get_db()

    conn.execute(
        """
        INSERT INTO transactions
        (timestamp, user_id, transaction_amount, transaction_type,
        device_used, location, payment_method, fraud_risk_score, risk_level)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            user_id,
            amount,
            transaction_type,
            device,
            location,
            payment_method,
            risk_score,
            risk_level
        )
    )

    conn.commit()
    conn.close()

    return jsonify({
        "fraud_prediction": fraud_pred,
        "risk_level": risk_level,
        "fraud_risk_score": risk_score,
        "source": source
    })


# -------------------------------------------------
# TRANSACTION HISTORY
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
# LOGIN
# -------------------------------------------------

@app.route("/login", methods=["POST"])
def login():

    data = request.get_json(force=True)
    username = data.get("username")

    if not username:
        return jsonify({"error": "Username required"}), 400

    conn = get_db()

    conn.execute(
        "INSERT INTO user_logins (username, login_time) VALUES (?, ?)",
        (username, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    )

    conn.commit()
    conn.close()

    return jsonify({"message": "Login recorded"})


# -------------------------------------------------
# LOGIN HISTORY
# -------------------------------------------------

@app.route("/logins", methods=["GET"])
def get_logins():

    conn = get_db()

    rows = conn.execute(
        "SELECT username, login_time FROM user_logins ORDER BY login_time DESC LIMIT 50"
    ).fetchall()

    conn.close()

    results = []

    for r in rows:
        results.append({
            "username": r[0],
            "login_time": r[1]
        })

    return jsonify({"logins": results})


# -------------------------------------------------
# SIMULATE TEST DATA
# -------------------------------------------------

@app.route("/simulate", methods=["POST"])
def simulate():

    import random

    conn = get_db()

    for _ in range(3):

        risk = random.choice(["LOW", "MEDIUM", "HIGH"])
        score = random.choice([10, 50, 90])

        conn.execute(
            """
            INSERT INTO transactions
            (timestamp, user_id, transaction_amount, transaction_type,
            device_used, location, payment_method, fraud_risk_score, risk_level)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                f"UPI{random.randint(1000,9999)}",
                random.randint(1000,50000),
                "Transfer",
                random.choice(["Mobile","Desktop"]),
                random.choice(["Delhi","Mumbai","Hyderabad"]),
                "UPI",
                score,
                risk
            )
        )

    conn.commit()
    conn.close()

    return jsonify({"message":"Simulation data generated"})


# -------------------------------------------------
# STATS
# -------------------------------------------------

@app.route("/stats", methods=["GET"])
def get_stats():

    conn = get_db()

    total = conn.execute("SELECT COUNT(*) FROM transactions").fetchone()[0]
    low = conn.execute("SELECT COUNT(*) FROM transactions WHERE risk_level='LOW'").fetchone()[0]
    medium = conn.execute("SELECT COUNT(*) FROM transactions WHERE risk_level='MEDIUM'").fetchone()[0]
    high = conn.execute("SELECT COUNT(*) FROM transactions WHERE risk_level='HIGH'").fetchone()[0]

    conn.close()

    return jsonify({
        "total": total,
        "low": low,
        "medium": medium,
        "high": high
    })


# -------------------------------------------------
# RUN SERVER
# -------------------------------------------------

if __name__ == "__main__":
    print("Starting UPI Fraud Detection Backend...")
    app.run(debug=True, port=5001)