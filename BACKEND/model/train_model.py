import pandas as pd
import pickle
import os
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.impute import SimpleImputer

# -------------------------------
# Load dataset
# -------------------------------
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
csv_path = os.path.join(base_dir, "data", "fraud_dataset.csv")
data = pd.read_csv(csv_path)

# Drop unnecessary columns
data = data.drop("Transaction_ID", axis=1)

# Separate numeric and categorical columns
numeric_cols = ['User_ID', 'Transaction_Amount', 'Time_of_Transaction', 'Previous_Fraudulent_Transactions', 'Account_Age', 'Number_of_Transactions_Last_24H']
categorical_cols = ['Transaction_Type', 'Device_Used', 'Location', 'Payment_Method']

# Impute missing values
num_imputer = SimpleImputer(strategy='mean')
data[numeric_cols] = num_imputer.fit_transform(data[numeric_cols])

cat_imputer = SimpleImputer(strategy='most_frequent')
data[categorical_cols] = cat_imputer.fit_transform(data[categorical_cols])

# Encode categorical variables
encoders = {}
for col in categorical_cols:
    le = LabelEncoder()
    data[col] = le.fit_transform(data[col])
    encoders[col] = le

# Target column
y = data["Fraudulent"]

# Feature columns
X = data.drop("Fraudulent", axis=1)

# Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# -------------------------------
# Scaling for Logistic Regression
# -------------------------------
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# -------------------------------
# Logistic Regression Model
# -------------------------------
logistic_model = LogisticRegression(max_iter=1000)
logistic_model.fit(X_train_scaled, y_train)

# -------------------------------
# Random Forest Model
# -------------------------------
rf_model = RandomForestClassifier(
    n_estimators=200,
    max_depth=10,
    random_state=42
)

rf_model.fit(X_train, y_train)

# -------------------------------
# Save Models
# -------------------------------
with open("logistic_model.pkl", "wb") as f:
    pickle.dump(logistic_model, f)

with open("random_forest_model.pkl", "wb") as f:
    pickle.dump(rf_model, f)

with open("scaler.pkl", "wb") as f:
    pickle.dump(scaler, f)

with open("encoders.pkl", "wb") as f:
    pickle.dump(encoders, f)

print("✅ Logistic Regression and Random Forest trained successfully!")