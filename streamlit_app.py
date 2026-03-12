import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime

# Page config
st.set_page_config(
    page_title="SecurePay AI - UPI Fraud Detection",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        background: linear-gradient(135deg, #020617 0%, #0f1a35 100%);
        color: #e5e7eb;
    }
    .stTabs [data-baseweb="tab-list"] button {
        color: #00ffcc !important;
    }
    .stButton > button {
        background: linear-gradient(135deg, #0284c7, #38bdf8) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 10px 25px !important;
        font-weight: bold !important;
    }
    .stButton > button:hover {
        box-shadow: 0 0 20px rgba(56, 189, 248, 0.6) !important;
    }
    h1, h2, h3 {
        color: #00ffcc !important;
        text-shadow: 0 0 10px rgba(0, 255, 204, 0.3);
    }
    .metric-card {
        background: rgba(15, 26, 53, 0.9);
        border-left: 4px solid #00ffcc;
        padding: 20px;
        border-radius: 8px;
        box-shadow: 0 4px 15px rgba(0, 255, 204, 0.1);
    }
    </style>
""", unsafe_allow_html=True)

# Backend URL
BACKEND_URL = "http://localhost:5001"

# Title and Header
st.markdown("# 🛡️ SecurePay AI - UPI Fraud Detection System")
st.markdown("### Real-Time AI-Powered Fraud Detection for Digital Payments")

# Sidebar
with st.sidebar:
    st.markdown("### ⚙️ Configuration")
    backend_status = st.empty()
    check_backend = st.button("🔄 Check Backend Status")
    
    if check_backend:
        try:
            resp = requests.get(f"{BACKEND_URL}/", timeout=2)
            if resp.status_code == 200:
                backend_status.success("✅ Backend Connected")
        except:
            backend_status.error("❌ Backend Offline")

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["🔍 Check Fraud", "📊 Dashboard", "💾 Transaction History", "👤 Login History"])

# ===================== TAB 1: CHECK FRAUD =====================
with tab1:
    st.markdown("## Check Transaction Fraud Risk")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Transaction Details")
        user_id = st.text_input("👤 User ID", value="U12345")
        amount = st.number_input("💰 Transaction Amount (₹)", min_value=0.0, value=15000.0, step=100.0)
        device = st.selectbox("📱 Device Used", ["Mobile", "Desktop", "Tablet"])
        
    with col2:
        st.subheader("")
        location = st.text_input("📍 Location", value="Delhi")
        transaction_type = st.selectbox("🔄 Transaction Type", ["Transfer", "Payment", "Withdrawal"])
        payment_method = st.selectbox("💳 Payment Method", ["UPI", "Net Banking", "Credit Card"])
    
    # Check Button
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        check_button = st.button("✓ Check Fraud Risk", key="check_fraud", use_container_width=True)
    
    # Result Display
    if check_button:
        try:
            payload = {
                "User_ID": user_id,
                "Transaction_Amount": float(amount),
                "Device": device,
                "Location": location,
                "Transaction_Type": transaction_type,
                "Time_of_Transaction": datetime.now().hour,
                "Payment_Method": payment_method
            }
            
            with st.spinner("🔄 Analyzing transaction..."):
                response = requests.post(f"{BACKEND_URL}/predict", json=payload, timeout=5)
            
            if response.status_code == 200:
                result = response.json()
                
                st.markdown("---")
                st.markdown("## 📈 Analysis Results")
                
                # Risk badge
                risk_level = result.get("risk_level", "UNKNOWN")
                fraud_score = result.get("fraud_risk_score", 0)
                fraud_pred = result.get("fraud_prediction", 0)
                
                if risk_level == "LOW":
                    badge_color = "🟢"
                    status_color = "green"
                elif risk_level == "MEDIUM":
                    badge_color = "🟡"
                    status_color = "orange"
                else:
                    badge_color = "🔴"
                    status_color = "red"
                
                # Display metrics
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Risk Level", f"{badge_color} {risk_level}")
                
                with col2:
                    st.metric("Fraud Score", f"{int(fraud_score)}%")
                
                with col3:
                    status_text = "HIGH RISK" if fraud_pred == 1 else "LOW RISK"
                    st.metric("ML Prediction", status_text)
                
                with col4:
                    st.metric("Amount", f"₹{amount:,.0f}")
                
                # Risk meter visualization
                fig = go.Figure(data=[
                    go.Bar(
                        x=[fraud_score],
                        y=["Risk Score"],
                        orientation='h',
                        marker=dict(
                            color=[fraud_score],
                            colorscale='RdYlGn_r',
                            line=dict(color='#00ffcc', width=2)
                        ),
                        text=f"{int(fraud_score)}%",
                        textposition='inside',
                    )
                ])
                fig.update_layout(
                    xaxis=dict(range=[0, 100]),
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    title="Fraud Risk Meter",
                    margin=dict(l=20, r=20, t=40, b=20)
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Reasoning
                st.markdown("### 🔍 Fraud Detection Reasoning")
                reasons = []
                
                if fraud_pred == 1:
                    reasons.append("⚠️ ML Model flagged as HIGH RISK")
                else:
                    reasons.append("✅ ML Model indicates LOW RISK")
                
                if fraud_score > 70:
                    reasons.append("🔴 High fraud probability detected")
                elif fraud_score > 30:
                    reasons.append("🟡 Moderate fraud indicators present")
                else:
                    reasons.append("🟢 Transaction appears legitimate")
                
                if amount > 100000:
                    reasons.append("💰 Large transaction amount flagged")
                
                hour = datetime.now().hour
                if hour < 5 or hour > 23:
                    reasons.append("⏰ Transaction at unusual time")
                
                for reason in reasons:
                    st.info(reason)
                
                # Success message for low risk
                if risk_level == "LOW":
                    st.success("✅ Transaction appears safe. Proceed with confidence!")
                elif risk_level == "MEDIUM":
                    st.warning("⚠️ Please verify this transaction. Additional review recommended.")
                else:
                    st.error("🚨 HIGH RISK FRAUD DETECTED! Transaction blocked for security.")
            
            else:
                st.error(f"❌ Backend error: {response.status_code}")
        
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

# ===================== TAB 2: DASHBOARD =====================
with tab2:
    st.markdown("## 📊 Real-Time Analytics Dashboard")
    
    try:
        # Fetch statistics
        stats_resp = requests.get(f"{BACKEND_URL}/stats", timeout=5)
        trans_resp = requests.get(f"{BACKEND_URL}/transactions", timeout=5)
        
        if stats_resp.status_code == 200 and trans_resp.status_code == 200:
            stats = stats_resp.json()
            transactions = trans_resp.json().get("transactions", [])
            
            # Convert to DataFrame
            if transactions:
                df = pd.DataFrame(transactions)
            
            # Metrics Row
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Transactions", stats.get("total", 0), delta=None)
            with col2:
                st.metric("Low Risk", stats.get("low", 0), delta=None)
            with col3:
                st.metric("Medium Risk", stats.get("medium", 0), delta=None)
            with col4:
                st.metric("High Risk", stats.get("high", 0), delta=None)
            
            st.markdown("---")
            
            # Charts
            col1, col2 = st.columns(2)
            
            # Risk Distribution Pie Chart
            if transactions:
                risk_counts = {"LOW": 0, "MEDIUM": 0, "HIGH": 0}
                for tx in transactions:
                    level = tx.get("risk_level", "LOW")
                    if level in risk_counts:
                        risk_counts[level] += 1
                
                fig_pie = go.Figure(data=[go.Pie(
                    labels=list(risk_counts.keys()),
                    values=list(risk_counts.values()),
                    marker=dict(colors=['#00e676', '#ffca28', '#ff5252']),
                    hole=0.3
                )])
                fig_pie.update_layout(
                    title="Risk Distribution",
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#e5e7eb')
                )
                
                with col1:
                    st.plotly_chart(fig_pie, use_container_width=True)
            
            # Score Distribution
            if transactions and 'fraud_risk_score' in transactions[0]:
                scores = [tx.get('fraud_risk_score', 0) for tx in transactions]
                
                fig_hist = go.Figure(data=[
                    go.Histogram(x=scores, nbinsx=20, marker_color='#00ffcc', opacity=0.7)
                ])
                fig_hist.update_layout(
                    title="Score Distribution",
                    xaxis_title="Fraud Risk Score",
                    yaxis_title="Count",
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#e5e7eb')
                )
                
                with col2:
                    st.plotly_chart(fig_hist, use_container_width=True)
            
            # Simulate button
            st.markdown("---")
            col1, col2 = st.columns([1, 3])
            with col1:
                if st.button("🎲 Generate Test Data"):
                    with st.spinner("Generating test transactions..."):
                        try:
                            sim_resp = requests.post(f"{BACKEND_URL}/simulate", json={}, timeout=5)
                            if sim_resp.status_code == 200:
                                st.success("✅ Test data generated!")
                                st.rerun()
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
        
        else:
            st.error("Could not fetch dashboard data")
    
    except Exception as e:
        st.error(f"Dashboard error: {str(e)}")

# ===================== TAB 3: TRANSACTION HISTORY =====================
with tab3:
    st.markdown("## 💾 Transaction History")
    
    try:
        trans_resp = requests.get(f"{BACKEND_URL}/transactions", timeout=5)
        
        if trans_resp.status_code == 200:
            transactions = trans_resp.json().get("transactions", [])
            
            if transactions:
                df = pd.DataFrame(transactions)
                
                # Filter options
                col1, col2, col3 = st.columns(3)
                with col1:
                    risk_filter = st.multiselect(
                        "Filter by Risk Level",
                        ["LOW", "MEDIUM", "HIGH"],
                        default=["LOW", "MEDIUM", "HIGH"]
                    )
                
                # Filter DataFrame
                if risk_filter:
                    df_filtered = df[df['risk_level'].isin(risk_filter)]
                else:
                    df_filtered = df
                
                st.dataframe(df_filtered, use_container_width=True, height=400)
                
                st.markdown(f"**Total Records: {len(df_filtered)}**")
            
            else:
                st.info("📭 No transactions yet. Use 'Check Fraud' to add transactions.")
        
        else:
            st.error("Could not fetch transaction history")
    
    except Exception as e:
        st.error(f"Error: {str(e)}")

# ===================== TAB 4: LOGIN HISTORY =====================
with tab4:
    st.markdown("## 👤 User Login History")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        username = st.text_input("👤 Enter Username", value="user123")
    
    with col2:
        st.markdown("")  # Spacing
        login_button = st.button("🔐 Login", use_container_width=True)
    
    if login_button:
        try:
            payload = {"username": username}
            with st.spinner("Logging in..."):
                resp = requests.post(f"{BACKEND_URL}/login", json=payload, timeout=5)
            
            if resp.status_code == 200:
                st.success(f"✅ Welcome {username}!")
            else:
                st.error("Login failed")
        
        except Exception as e:
            st.error(f"Error: {str(e)}")
    
    st.markdown("---")
    st.markdown("### Login Records")
    
    try:
        logins_resp = requests.get(f"{BACKEND_URL}/logins", timeout=5)
        
        if logins_resp.status_code == 200:
            logins = logins_resp.json().get("logins", [])
            
            if logins:
                df_logins = pd.DataFrame(logins)
                st.dataframe(df_logins, use_container_width=True, height=300)
                st.markdown(f"**Total Logins: {len(df_logins)}**")
            
            else:
                st.info("📭 No login records yet.")
        
        else:
            st.error("Could not fetch login history")
    
    except Exception as e:
        st.error(f"Error: {str(e)}")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #00ffcc; font-size: 0.9rem;'>
    © 2026 SecurePay AI — UPI Fraud Detection System | Powered by Streamlit + Flask
    </div>
    """,
    unsafe_allow_html=True
)
