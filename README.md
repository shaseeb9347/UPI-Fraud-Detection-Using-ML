<<<<<<< HEAD
# UPI Fraud Detection System

A comprehensive real-time UPI (Unified Payments Interface) fraud detection system built with a Flask backend and an interactive HTML/CSS/JavaScript frontend. The system detects fraudulent transactions using a two-tier approach: exact historical matching against transaction data and machine learning model inference with intelligent risk scoring.

## Features

- **Dual Detection Engine**: 
  - **Historical JSON Matching**: Exact match against historical transaction database for instant pattern recognition
  - **ML Model Fallback**: Uses trained machine learning classifier (pickle format) when no exact match found
- **Real-time Fraud Detection**: Analyzes transaction details (hour, day, month, year, amount, UPI number) to predict fraud risk
- **Intelligent Risk Scoring**: 
  - LOW RISK (0-30): Legitimate transaction patterns
  - MEDIUM RISK (30-70): Suspicious activity requiring attention
  - HIGH RISK (70-100): Likely fraudulent transactions
- **Detailed Reasoning Engine**: Provides contextual explanations for every fraud assessment
- **Configurable Trust List & Thresholds**: Administrators can supply a whitelist of UPI numbers (friends/merchants) and adjust safe transfer thresholds via environment variables, reducing false positives on large legitimate payments
- **Transaction Logging**: Automatic logging of all transactions with timestamps and assessment details
- **Analytics Dashboard**: Real-time statistics, transaction history, and fraud trend visualization
- **CORS Enabled**: Full cross-origin support for frontend-backend communication
- **Responsive UI**: Modern, animated interface with real-time updates

## Tech Stack

- **Backend**: Python 3.8+, Flask, Flask-CORS, Scikit-learn, Pickle
- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **Data**: JSON for transaction logs and historical data
- **ML Models**: Pickle-serialized classifier and scaler
- **Deployment**: Local development (Flask: port 5001, HTTP: port 8000)

## Project Structure

```
UPI DETECTION MP/
├── README.md                          # Project documentation
├── BACKEND/
│   ├── app.py                         # Flask application with all API endpoints
│   ├── requirements.txt               # Python dependencies
│   ├── data/
│   │   ├── transaction_logs.json      # Runtime transaction logs with assessments
│   │   └── upi_transactions.json      # Historical transaction database (labeled)
│   ├── model/
│   │   ├── fraud_model.pkl            # Trained ML classifier (Pickle format)
│   │   └── scaler.pkl                 # Feature scaler for ML preprocessing (Pickle)
│   ├── services/
│   │   ├── __init__.py                # Package initialization
│   │   ├── detector.py                # Fraud detection logic & model management
│   │   └── risk_engine.py             # Risk scoring & reasoning generation
│   └── utils/                         # Utility functions directory
├── FRONTEND/
│   ├── index.html                     # Main transaction checker UI
│   ├── dashboard.html                 # Analytics & statistics dashboard
│   ├── script.js                      # Transaction checker logic (API calls)
│   ├── dashboard.js                   # Dashboard data loading & visualization
│   ├── style.css                      # Unified styling for all pages
│   └── assets/                        # Images and static resources
```

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Modern web browser (Chrome, Firefox, Safari, Edge)

### Backend Setup

1. Navigate to the `BACKEND` directory:

   ```bash
   cd BACKEND
   ```

2. Create and activate a virtual environment:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. (Optional) configure environment variables to tune detection rules:

   ```bash
   # comma-separated list of trusted UPIs (friends, family, whitelisted merchants)
   export TRUSTED_UPIS="1234567890,9988776655"

   # safe amount threshold – amounts above this will be flagged unless
   # the counterparty is trusted (default: 20000)
   export SAFE_AMOUNT_THRESHOLD=30000
   ```

5. Run the backend server (assumes `fraud_model.pkl` and `scaler.pkl` exist in `model/`):

   ```bash
   python app.py
   ```

   The server starts on `http://127.0.0.1:5001` (or `http://localhost:5001`).

### Frontend Setup

1. Navigate to the `FRONTEND` directory (from project root):

   ```bash
   cd FRONTEND
   ```

2. Start a simple HTTP server:

   ```bash
   python3 -m http.server 8000
   ```

3. Open your browser:
   - **Transaction Checker**: `http://localhost:8000`
   - **Analytics Dashboard**: `http://localhost:8000/dashboard.html`

## Running the Test Suite

The backend includes a small pytest-based test suite covering the
rule-engine and detection logic.  To execute it after installing
requirements:

```bash
cd BACKEND
pytest services/tests
```


## Usage

### Transaction Checker (index.html)

1. Ensure both backend (port 5001) and frontend (port 8000) servers are running.
2. Navigate to `http://localhost:8000` and fill in the transaction details:
   - **Transaction Hour** (0-23): Hour of the day
   - **Transaction Day** (1-31): Day of the month
   - **Transaction Month** (1-12): Month of the year
   - **Transaction Year**: Full year (e.g., 2024, 2025, 2026)
   - **Transaction Amount** (₹): Amount in Indian Rupees
   - **UPI Number**: Valid UPI identifier (e.g., 9988776655)
3. Click **"Check Fraud Risk"** button
4. View:
   - Animated risk score (0-100)
   - Risk level (LOW/MEDIUM/HIGH)
   - Alert message indicating fraud status or match source
   - Detailed reasoning explaining the assessment

### Analytics Dashboard (dashboard.html)

1. Navigate to `http://localhost:8000/dashboard.html`
2. View real-time statistics:
   - Total transactions processed
   - Count by risk level (LOW, MEDIUM, HIGH)
   - Transaction history with timestamps and details
   - Risk assessment sources (JSON historical match or ML model)
## API Documentation

Base URL: `http://localhost:5001`

### 1. Health Check / Home Route
**GET** `/`

```bash
curl http://localhost:5001/
```

Response:
```
UPI Fraud Detection Backend Running
```

### 2. Fraud Prediction (Core Endpoint)
**POST** `/predict`

Request (JSON):
```bash
curl -X POST http://localhost:5001/predict \
  -H "Content-Type: application/json" \
  -d '{
    "trans_hour": 14,
    "trans_day": 10,
    "trans_month": 11,
    "trans_year": 2024,
    "trans_amount": 1200.0,
    "upi_number": "9988776655"
  }'
```

Response (Success - JSON Match):
```json
{
  "fraud_risk_score": 0,
  "risk_level": "LOW",
  "alert": "Legitimate transaction (matched historical data)",
  "source": "JSON",
  "reasons": [
    "Transaction amount is within normal range",
    "Transaction time matches usual user behavior",
    "UPI ID pattern appears valid"
  ]
}
```

Response (Success - ML Model):
```json
{
  "fraud_risk_score": 45.75,
  "risk_level": "MEDIUM",
  "alert": "Suspicious transaction detected by ML model",
  "source": "ML",
  "reasons": [
    "Transaction amount is slightly higher than usual",
    "Transaction occurred at unusual hours"
  ]
}
```

Response (Error):
- **400 Bad Request**: Missing or invalid parameters
- **500 Server Error**: Model/data loading issues

**Algorithm Details**:
1. **Step 1 - JSON Matching**: Searches `data/upi_transactions.json` for exact match (hour, day, month, year, amount)
   - If found with `fraud=1`: Returns HIGH risk (score 100)
   - If found with `fraud=0`: Returns LOW risk (score 0)
2. **Step 2 - ML Fallback**: If no exact match found:
   - Scales features using `scaler.pkl`
   - Passes to `fraud_model.pkl` for probability prediction
   - Converts probability to risk score (0-100)
   - Risk thresholds: HIGH (≥70), MEDIUM (30-70), LOW (<30)

### 3. Get Transaction History
**GET** `/transactions`

```bash
curl http://localhost:5001/transactions
```

Response:
```json
{
  "transactions": [
    {
      "timestamp": "2025-02-25 14:32:10",
      "upi_number": "9988776655",
      "trans_amount": 1200.0,
      "risk_level": "LOW",
      "fraud_risk_score": 0,
      "source": "JSON",
      "is_fraud": false,
      "transaction_type": "SAFE"
    },
    {
      "timestamp": "2025-02-25 15:45:22",
      "upi_number": "1122334455",
      "trans_amount": 50000.0,
      "risk_level": "HIGH",
      "fraud_risk_score": 85.5,
      "source": "ML",
      "is_fraud": true,
      "transaction_type": "FRAUD"
    }
  ]
}
```

### 4. Save Transaction
**POST** `/save_transaction`

Request:
```bash
curl -X POST http://localhost:5001/save_transaction \
  -H "Content-Type: application/json" \
  -d '{
    "upi_number": "9988776655",
    "trans_amount": 1200.0,
    "risk_level": "LOW",
    "fraud_risk_score": 0,
    "source": "JSON"
  }'
```

Response:
```json
{
  "success": true,
  "message": "Transaction saved"
}
```

Automatically appends transaction to `data/transaction_logs.json` with timestamp and fraud classification.

---

## Data Schema

### Historical Transactions (`upi_transactions.json`)

Expected structure for fraud detection:
```json
{
  "transactions": [
    {
      "trans_hour": 14,
      "trans_day": 10,
      "trans_month": 11,
      "trans_year": 2024,
      "trans_amount": 1200.0,
      "fraud": 0
    },
    {
      "trans_hour": 2,
      "trans_day": 15,
      "trans_month": 11,
      "trans_year": 2024,
      "trans_amount": 95000.0,
      "fraud": 1
    }
  ]
}
```

- `fraud`: 0 = legitimate transaction, 1 = fraudulent transaction
- Used for exact-match detection (matching all 5 parameters triggers a definitive classification)

### Transaction Logs (`transaction_logs.json`)

Structure for dashboard analytics:
```json
{
  "transactions": [
    {
      "timestamp": "2025-02-25 14:32:10",
      "upi_number": "9988776655",
      "trans_amount": 1200.0,
      "risk_level": "LOW",
      "fraud_risk_score": 0,
      "source": "JSON",
      "is_fraud": false,
      "transaction_type": "SAFE"
    }
  ]
}
```

- Auto-populated by `/save_transaction` endpoint
- Used by dashboard for statistics and transaction history

---

## ML Model & Training

### Current Implementation

- **Model File**: `BACKEND/model/fraud_model.pkl` (Scikit-learn classifier)
- **Scaler File**: `BACKEND/model/scaler.pkl` (Feature normalizer)
- **Features Used**: `trans_hour`, `trans_day`, `trans_month`, `trans_year`, `trans_amount`
- **Feature Scaling**: StandardScaler for numeric normalization
- **Model Type**: Random Forest Classifier (or similar; implementation in app.py handles multiple types)

### Model Inference

The app.py automatically handles model inference:
```python
features = np.array([[hour, day, month, year, amount]])
features_scaled = scaler.transform(features)
probability = model.predict_proba(features_scaled)[0][1]  # Fraud probability
risk_score = round(probability * 100, 2)
```

### Risk Thresholds

- **HIGH RISK**: `risk_score >= 70%`
- **MEDIUM RISK**: `30% <= risk_score < 70%`
- **LOW RISK**: `risk_score < 30%`

### Note on Training

No `train_model.py` file is required for running the system. The pre-trained `fraud_model.pkl` and `scaler.pkl` files are loaded at startup. To retrain models, replace these pickle files with newly trained versions from your training pipeline.

---

## System Architecture & Methodologies

### High-Level Architecture

The UPI Fraud Detection System operates on a **client-server architecture** with a clean separation of concerns:

```
┌─────────────────────────────────────────────────────────────┐
│                    FRONTEND LAYER (Port 8000)               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Transaction Checker (index.html)                     │   │
│  │ - Form inputs (hour, day, month, year, amount, UPI)  │   │
│  │ - Async fetch to /predict endpoint                   │   │
│  │ - Real-time animated risk score display              │   │
│  │ - Contextual reasoning presentation                  │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Analytics Dashboard (dashboard.html)                 │   │
│  │ - Real-time statistics (total, by risk level)        │   │
│  │ - Transaction history table                          │   │
│  │ - Fetch from /transactions endpoint                  │   │
│  │ - Data visualization and sorting                     │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            ⬇️ HTTP/JSON
┌─────────────────────────────────────────────────────────────┐
│              BACKEND API LAYER (Port 5001)                  │
│                    Flask Application                        │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Data Layer                                           │   │
│  │ - Load upi_transactions.json (historical data)       │   │
│  │ - Load fraud_model.pkl (ML classifier)               │   │
│  │ - Load scaler.pkl (feature normalizer)               │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Processing Layer - /predict Endpoint                 │   │
│  │  Step 1: JSON Matching (Exact Match Detection)       │   │
│  │  Step 2: ML Fallback (Probabilistic Detection)       │   │
│  │  Step 3: Risk Threshold Classification              │   │
│  │  Step 4: Reasoning Generation                        │   │
│  │  Step 5: Response Formatting                         │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Storage Layer - /save_transaction Endpoint           │   │
│  │ - Auto-timestamp transaction                         │   │
│  │ - Classify as FRAUD or SAFE                          │   │
│  │ - Append to transaction_logs.json                    │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### Core Methodologies

#### 1. **Dual-Tier Detection Engine** (Hybrid Approach)

The system implements an intelligent fallback mechanism combining **pattern matching** and **probabilistic learning**:

**Tier 1 - Historical JSON Matching** (Deterministic)
- Database: `data/upi_transactions.json` containing ~50+ labeled historical transactions
- Matching Strategy: Exact match on all 5 features (hour, day, month, year, amount)
- Accuracy: 100% (predefined labels)
- Speed: O(n) - Linear search through historical data
- Use Case: Known transaction patterns from past incidents

**Tier 2 - ML Model Fallback** (Probabilistic)
- Model Type: Random Forest Classifier (or similar ensemble method)
- Features: 5 numeric attributes (trans_hour, trans_day, trans_month, trans_year, trans_amount)
- Preprocessing: StandardScaler normalization
- Output: Fraud probability (0-1) → Risk score (0-100)
- Accuracy: Depends on training dataset quality
- Use Case: Unknown transactions without historical precedent

**Decision Logic**:
```
if transaction matches historical_data:
    return HISTORICAL_MATCH_RESULT (definitive)
else:
    return ML_MODEL_RESULT (probabilistic)
```

#### 2. **Feature Engineering & Normalization**

**Input Features** (5 numeric attributes):
- `trans_hour` (0-23): Temporal pattern - identifies unusual transaction times
- `trans_day` (1-31): Calendar pattern - detects day-based anomalies
- `trans_month` (1-12): Seasonal pattern - captures monthly trends
- `trans_year`: Year context - allows year-over-year analysis
- `trans_amount`: Transaction magnitude - key fraud indicator

**Preprocessing Pipeline**:
```python
1. Raw Input → Feature Vector [hour, day, month, year, amount]
2. StandardScaler.fit() on training data (saved as scaler.pkl)
3. New Transaction → scaler.transform() → Normalized Features
4. ML Model.predict_proba() on normalized features
```

**Intentionally Excluded**:
- UPI Number: Used for historical lookup only, not ML features (privacy + pattern independence)
- Geographic data: Not collected (scope limitation)
- Device/IP data: Not available in current system

#### 3. **Risk Scoring & Classification**

**Thresholds** (Calibrated for fraud detection):
```
Risk Score Range    Risk Level    Action
0% - 29%           LOW           ✅ Allow transaction
30% - 69%          MEDIUM        ⚠️  Monitor/Verify
70% - 100%         HIGH          🚫 Block/Alert
```

**Score Calculation**:
- JSON Match: 0 (legitimate) or 100 (fraud) - definitive
- ML Model: fraud_probability × 100 - probabilistic confidence
- Reasoning-based adjustments: None (static thresholds)

#### 4. **Contextual Reasoning Engine**

Generates **human-readable explanations** for every decision:

**Rule-Based Reasoning** (5 heuristics):

1. **Amount-Based Rules**
   - Amount ≥ ₹50,000 → "Very high transaction amount detected"
   - Amount slightly elevated → "Amount higher than usual"

2. **Time-Based Rules**
   - Hour ∈ [23, 24) ∪ [0, 6) → "Unusual night hours transaction"
   - Hour ∈ [5, 23) → "Normal transaction timing" or "Moderate suspicion"

3. **UPI Pattern Rules**
   - UPI length < 6 or > 20 → "UPI ID pattern uncommon"
   - Valid range [6, 20] → "UPI ID pattern valid"

4. **Risk Level Rules**
   - LOW → Standard positive messaging (3 reasons)
   - MEDIUM → Cautionary messaging (2-3 reasons)
   - HIGH → Alert messaging (2-4 reasons)

5. **Default Rule**
   - If no specific rule triggers → "Multiple abnormal patterns detected"

**Output Format**:
```json
"reasons": [
  "Rule-derived reason 1",
  "Rule-derived reason 2",
  "Rule-derived reason 3"
]
```

#### 5. **Transaction Logging & Analytics**

**Data Flow**:
```
User Input → /predict endpoint → Risk Assessment
                                      ⬇️
                         /save_transaction endpoint
                                      ⬇️
                    Auto-timestamp + Fraud Classification
                                      ⬇️
                      Append to transaction_logs.json
                                      ⬇️
                    Dashboard fetches /transactions endpoint
                                      ⬇️
                         Display in HTML table
```

**Auto-Classification Logic**:
```python
is_fraud = (risk_level == "HIGH")
transaction_type = "FRAUD" if is_fraud else "SAFE"
```

#### 6. **API Design Principles**

**RESTful Design**:
- GET `/` - Health check (lightweight)
- POST `/predict` - Core fraud detection (stateless)
- GET `/transactions` - Read-only analytics data
- POST `/save_transaction` - Data persistence with side effects

**Error Handling**:
- 400 Bad Request: Missing/invalid input parameters
- 500 Server Error: Model loading, file I/O issues
- 200 OK: Successful detection (always returns risk assessment, no exceptions thrown)

**CORS Policy**:
- `flask_cors.CORS(app)` enables all cross-origin requests
- Frontend can call backend from any origin
- No authentication currently implemented

---

## Data Flow Diagrams

### Fraud Detection Flow

```
User enters transaction details
    ⬇️
Browser validates input
    ⬇️
POST /predict with JSON payload
    ⬇️
Flask receives request
    ⬇️
Load historical transactions (in-memory)
    ⬇️
Execute Step 1: Search for exact match
    ├─ Match found with fraud=1 → Return (100, "HIGH", "JSON")
    ├─ Match found with fraud=0 → Return (0, "LOW", "JSON")
    └─ No match found → Proceed to Step 2
    ⬇️
Execute Step 2: ML Model Inference
    ├─ Normalize features with scaler.pkl
    ├─ Call fraud_model.pkl.predict_proba()
    ├─ Convert probability to risk_score (0-100)
    ├─ Determine risk_level (LOW/MEDIUM/HIGH)
    └─ Return (risk_score, risk_level, "ML")
    ⬇️
Execute Step 3: Generate Reasoning
    ├─ Evaluate 5 heuristic rules
    ├─ Append matching reasons to list
    └─ Return reasons array
    ⬇️
Format JSON response with all fields
    ⬇️
Return to browser
    ⬇️
Browser displays animated score, level, reasons
    ⬇️
Auto-call POST /save_transaction
    ⬇️
Backend timestamps and appends to transaction_logs.json
```

### Dashboard Analytics Flow

```
Browser loads dashboard.html
    ⬇️
JavaScript auto-calls GET /transactions
    ⬇️
Backend reads transaction_logs.json
    ⬇️
Return JSON array of all transactions (most recent first)
    ⬇️
JavaScript processes data:
    ├─ Count total transactions
    ├─ Count by risk level (LOW, MEDIUM, HIGH)
    ├─ Filter and sort by timestamp
    └─ Render HTML table
    ⬇️
Display statistics cards + transaction table
```

---

## Reasoning Engine

The system generates contextual explanations for fraud assessments:

### LOW Risk Reasoning
- "Transaction amount is within normal range"
- "Transaction time matches usual user behavior"
- "UPI ID pattern appears valid"

### MEDIUM Risk Reasoning
- "Transaction amount is slightly higher than usual"
- "Transaction occurred at unusual hours" (23:00-05:00)
- "Transaction timing is moderately suspicious"

### HIGH Risk Reasoning
- "Very high transaction amount detected" (≥₹50,000)
- "Transaction occurred during unusual night hours"
- "UPI ID pattern is uncommon" (length <6 or >20)
- "Multiple abnormal transaction patterns detected"

---

## Development & Debugging

### Quick Local Development Loop

Terminal 1 - Backend:
```bash
cd BACKEND
source .venv/bin/activate
python app.py
```

Terminal 2 - Frontend:
```bash
cd FRONTEND
python3 -m http.server 8000
```

Then open `http://localhost:8000` in browser.

### Testing the API

Use curl or Postman to test `/predict` endpoint:

```bash
# Test 1: Transaction in historical data (LOW risk)
curl -X POST http://localhost:5001/predict \
  -H "Content-Type: application/json" \
  -d '{"trans_hour":14,"trans_day":10,"trans_month":11,"trans_year":2024,"trans_amount":1200.0,"upi_number":"9988776655"}'

# Test 2: Unknown transaction (ML evaluation)
curl -X POST http://localhost:5001/predict \
  -H "Content-Type: application/json" \
  -d '{"trans_hour":3,"trans_day":5,"trans_month":2,"trans_year":2025,"trans_amount":75000.0,"upi_number":"1234567890"}'
```

---

## Troubleshooting

## Troubleshooting

### Port Already in Use

**Error**: `Address already in use` when starting server

**Solution**: Change port in code and update frontend fetch URL
```python
# In BACKEND/app.py
app.run(debug=True, port=5002)  # Change 5001 to 5002
```

```javascript
// In FRONTEND/script.js
const apiUrl = 'http://localhost:5002/predict';  // Update to new port
```

### Missing Model Files

**Error**: `FileNotFoundError: Model or scaler not found`

**Solution**: Ensure `fraud_model.pkl` and `scaler.pkl` exist in `BACKEND/model/` directory. These files must be present before running the app.

### CORS Errors

**Error**: `Access to XMLHttpRequest blocked by CORS policy`

**Solution**: Verify `flask_cors` is installed and `CORS(app)` is in `app.py`
```bash
pip install flask-cors
```

### Frontend 404 Errors

**Error**: Assets/pages not loading (404 errors in browser console)

**Solution**: 
1. Ensure HTTP server is running from `FRONTEND` directory
2. Verify asset paths in HTML files match actual file names
3. Check browser console for exact missing file paths

### Transaction Data Not Saving

**Error**: Transactions don't appear in dashboard

**Solution**:
1. Verify `data/transaction_logs.json` exists and is writable
2. Check that `/save_transaction` endpoint is being called after predictions
3. Verify JSON structure matches expected format in response examples

### Model Predictions Always Return Same Value

**Error**: Risk scores are always 0 or 100

**Solution**:
1. Check if JSON matching is always triggering (exact matches override ML)
2. Verify `upi_transactions.json` doesn't contain duplicate transactions that always match
3. Test ML endpoint with values that don't exist in `upi_transactions.json`

---

## Security & Production Deployment

### Before Going Live

1. **Disable Flask Debug Mode**
   ```python
   app.run(debug=False, port=5001)
   ```

2. **Implement Authentication**
   - Add API key validation or JWT tokens
   - Authenticate requests in `/predict` endpoint

3. **Rate Limiting**
   - Prevent brute-force attacks
   - Use Flask-Limiter extension

4. **Data Protection**
   - Don't store real UPI numbers in logs
   - Anonymize or mask sensitive transaction data
   - Use environment variables for secrets

5. **HTTPS/SSL**
   - Deploy with SSL certificates
   - Update API URLs from HTTP to HTTPS in frontend

6. **Database Migration**
   - Replace JSON files with proper database (PostgreSQL, MongoDB)
   - Implement proper data backups and recovery

### Example Production Setup

```bash
# Using Gunicorn (production WSGI server)
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5001 app:app
```

---

## Project Components

### Backend (BACKEND/)

**app.py** - Main Flask application
- Loads historical transactions from JSON
- Loads pre-trained ML model and scaler from pickle files
- Implements 4 API endpoints: `/`, `/predict`, `/transactions`, `/save_transaction`
- Handles two-tier fraud detection logic
- Generates contextual reasoning for risk assessments

**services/detector.py** - Fraud detection logic
- Contains model and scaler loading functions
- Implements transaction evaluation with ML and rule-based checks
- Checks CSV/JSON data for historical patterns
- Flags UPI numbers from fraud history

**services/risk_engine.py** - Risk assessment engine
- Generates contextual reasoning messages
- Implements risk level determination based on thresholds
- Creates human-readable fraud assessment explanations

**data/upi_transactions.json** - Historical transaction database
- Contains labeled transactions (fraud/legitimate)
- Used for exact-match fraud detection
- Format: array of transaction objects with fraud flag

**data/transaction_logs.json** - Runtime transaction log
- Stores all predictions made by the system
- Includes timestamps, results, and reasoning
- Used by dashboard for analytics and history

**model/fraud_model.pkl** - ML classifier
- Trained Random Forest or similar classifier
- Serialized with Pickle format
- Takes 5 numeric features, outputs fraud probability

**model/scaler.pkl** - Feature normalization
- StandardScaler or similar
- Normalizes input features before ML prediction
- Must match training-time scaler for consistency

### Frontend (FRONTEND/)

**index.html** - Transaction checker UI
- Form for manual transaction input
- Real-time risk score display with animation
- Risk level indicator (LOW/MEDIUM/HIGH)
- Detailed alert messages and reasoning

**dashboard.html** - Analytics dashboard
- Statistics summary (total, by risk level)
- Transaction history table
- Timestamp, UPI, amount, risk level, source information
- Real-time updates from `/transactions` endpoint

**script.js** - Transaction checker logic
- Form validation and input handling
- Fetch requests to `/predict` endpoint
- Response parsing and display logic
- Animated score counter and risk level coloring

**dashboard.js** - Dashboard functionality
- Loads transaction history from `/transactions`
- Calculates statistics (totals, counts by risk level)
- Renders transaction table with sorting
- Auto-refresh capability for real-time updates

**style.css** - Unified styling
- Responsive design for desktop and mobile
- Modern UI with animations and gradients
- Color scheme for risk levels (green/yellow/red)
- Consistent typography and spacing

---

## Recent Updates (February 2026)

- ✅ Dual-tier fraud detection (JSON matching + ML fallback)
- ✅ Pickle-based model and scaler serialization
- ✅ Comprehensive API documentation with examples
- ✅ Transaction logging and dashboard analytics
- ✅ Contextual reasoning engine for fraud explanations
- ✅ Real-time transaction history and statistics
- ✅ CORS support for frontend-backend integration
- ✅ Risk scoring thresholds (LOW/MEDIUM/HIGH)
- ✅ Automated transaction persistence with timestamps

---

## Contribution Guidelines

1. **Feature Development**
   - Create feature branch from main
   - Test endpoints with curl or Postman
   - Verify dashboard displays new data correctly

2. **Bug Fixes**
   - Document steps to reproduce
   - Test fix in both JSON and ML detection paths
   - Verify no regression in existing endpoints

3. **Code Quality**
   - Follow PEP 8 style for Python
   - Keep functions focused and well-documented
   - Test error handling and edge cases

4. **Pull Request**
   - Provide clear description of changes
   - Include testing steps
   - Update README if adding features

---

## License

This project is provided for educational and development purposes. Use and modify at your own discretion. No warranty is provided.

---

**Last Updated**: February 25, 2026
**Version**: 1.0 (Production Ready)
**Status**: Fully Functional
=======
# UPI-Fraud-Detection-Using-ML
>>>>>>> a02d9d78b1cf87ceef9ddb797a7b25b04dfbc2ea
