import sqlite3

conn = sqlite3.connect("transactions.db")

# create transactions table with comprehensive schema
conn.execute("""
CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT,
    user_id TEXT,
    transaction_amount REAL,
    transaction_type TEXT,
    device_used TEXT,
    location TEXT,
    payment_method TEXT,
    fraud_risk_score REAL,
    risk_level TEXT
)
""")

# create table to log user login events
conn.execute("""
CREATE TABLE IF NOT EXISTS user_logins (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    login_time TEXT
)
""")

conn.commit()
conn.close()

print("Database created (transactions + user_logins)")