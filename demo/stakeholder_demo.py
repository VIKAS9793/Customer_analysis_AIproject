"""
Customer Analysis AI - Stakeholder Demo

A comprehensive demo interface for showcasing the capabilities of the Customer Analysis AI system.
"""

import streamlit as st
import json
import pandas as pd
import numpy as np
import time
from datetime import datetime, timedelta
import uuid
import logging
import random

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="Customer Analysis AI - Stakeholder Demo",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load configuration
def load_config():
    """Load the demo configuration."""
    config = {
        "interface": "Streamlit",
        "agents": {
            "fraud_agent": {
                "enabled": True,
                "methods": ["detect_fraud_patterns", "risk_score"],
                "safe": True,
                "llm_used": False,
                "validation": {
                    "schema": "fraud_schema_v1.json",
                    "thresholds": {
                        "max_risk_score": 1.0
                    }
                }
            },
            "kyc_agent": {
                "enabled": True,
                "methods": ["check_kyc_status", "verify_identity"],
                "safe": True,
                "llm_used": False,
                "validation": {
                    "schema": "kyc_schema_v1.json",
                    "fields_required": ["customer_id", "dob"]
                }
            },
            "compliance_agent": {
                "enabled": True,
                "methods": ["run_checks", "generate_report"],
                "llm_used": False,
                "safe": True,
                "validation": {
                    "rules": ["no_future_dates", "valid_country_code"],
                    "schema": "compliance_schema.json"
                }
            },
            "insight_agent": {
                "enabled": True,
                "methods": ["summarize_behavior", "segment_customers"],
                "llm_used": True,
                "validation": {
                    "confidence_threshold": 0.85,
                    "source_required": True
                },
                "llm_constraints": {
                    "system_prompt": "You are an assistant providing summaries only based on validated agent outputs. Do not guess or hallucinate.",
                    "max_tokens": 256,
                    "grounding": "agent_outputs_only"
                }
            }
        },
        "prompt_router": {
            "type": "keyword_match",
            "routing_logic": "map keyword to agent",
            "fallback_agent": "insight_agent"
        },
        "input_validation": {
            "max_length": 300,
            "filter_patterns": ["[{};$]", "drop", "delete", "truncate"],
            "strict_mode": True
        },
        "output_validation": {
            "require_source": True,
            "require_confidence": True,
            "disallow_fabrication": True
        },
        "ui": {
            "framework": "Streamlit",
            "realtime": True,
            "sections": ["Prompt Input", "Agent Output", "Validation Feedback"],
            "logs_enabled": True,
            "session_monitoring": True
        }
    }
    return config

# Initialize session state
def init_session_state():
    """Initialize session state variables."""
    if 'config' not in st.session_state:
        st.session_state.config = load_config()
    
    if 'logs' not in st.session_state:
        st.session_state.logs = []
    
    if 'fraud_history' not in st.session_state:
        st.session_state.fraud_history = []
    
    if 'kyc_history' not in st.session_state:
        st.session_state.kyc_history = []
    
    if 'compliance_history' not in st.session_state:
        st.session_state.compliance_history = []
    
    if 'insight_history' not in st.session_state:
        st.session_state.insight_history = []
    
    if 'active_tab' not in st.session_state:
        st.session_state.active_tab = "Dashboard"

# Add a log entry
def add_log(message, level="INFO"):
    """Add a log entry to the session logs."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.session_state.logs.append({
        "timestamp": timestamp,
        "level": level,
        "message": message
    })
    logger.info(f"{level}: {message}")

# Main application
def main():
    """Main application function."""
    # Initialize session state
    init_session_state()
    
    # Sidebar
    with st.sidebar:
        st.title("Customer Analysis AI")
        st.subheader("Stakeholder Demo")
        
        # Navigation
        st.sidebar.header("Navigation")
        pages = ["Dashboard", "Fraud Detection", "KYC Verification", 
                 "Compliance Checks", "Customer Insights", "System Logs"]
        
        for page in pages:
            if st.sidebar.button(page, key=f"nav_{page}"):
                st.session_state.active_tab = page
        
        # System status
        st.sidebar.header("System Status")
        col1, col2 = st.sidebar.columns(2)
        with col1:
            st.metric("System Health", "98%", "+3%")
        with col2:
            st.metric("Response Time", "120ms", "-15ms")
        
        # Agent status
        st.sidebar.header("Agent Status")
        for agent, config in st.session_state.config["agents"].items():
            if config["enabled"]:
                st.sidebar.success(f"✅ {agent.replace('_', ' ').title()}")
            else:
                st.sidebar.error(f"❌ {agent.replace('_', ' ').title()}")
    
    # Main content
    if st.session_state.active_tab == "Dashboard":
        render_dashboard()
    elif st.session_state.active_tab == "Fraud Detection":
        render_fraud_detection()
    elif st.session_state.active_tab == "KYC Verification":
        render_kyc_verification()
    elif st.session_state.active_tab == "Compliance Checks":
        render_compliance_checks()
    elif st.session_state.active_tab == "Customer Insights":
        render_customer_insights()
    elif st.session_state.active_tab == "System Logs":
        render_system_logs()

# Render dashboard
def render_dashboard():
    """Render the main dashboard."""
    st.header("Customer Analysis AI Dashboard")
    st.subheader("System Overview")
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Fraud Detection Accuracy", "97%", "+2%")
    with col2:
        st.metric("KYC Verification Rate", "99.5%", "+0.5%")
    with col3:
        st.metric("Compliance Score", "98%", "+1%")
    with col4:
        st.metric("Customer Insights Generated", "1,245", "+85")
    
    # Recent activity
    st.subheader("Recent Activity")
    
    # Create sample data if none exists
    if len(st.session_state.fraud_history) == 0:
        generate_sample_data()
    
    # Recent fraud detections
    st.write("### Recent Fraud Detections")
    if st.session_state.fraud_history:
        df_fraud = pd.DataFrame(st.session_state.fraud_history[-5:])
        st.dataframe(df_fraud[["timestamp", "transaction_id", "risk_score", "decision"]])
    
    # Recent KYC verifications
    st.write("### Recent KYC Verifications")
    if st.session_state.kyc_history:
        df_kyc = pd.DataFrame(st.session_state.kyc_history[-5:])
        st.dataframe(df_kyc[["timestamp", "customer_id", "verification_score", "decision"]])
    
    # System performance
    st.subheader("System Performance")
    
    # Create sample performance data
    dates = [datetime.now() - timedelta(days=x) for x in range(14, 0, -1)]
    performance_data = {
        "date": [d.strftime("%Y-%m-%d") for d in dates],
        "response_time": [random.randint(100, 150) for _ in dates],
        "throughput": [random.randint(800, 1200) for _ in dates],
        "error_rate": [random.uniform(0.1, 0.5) for _ in dates]
    }
    
    df_perf = pd.DataFrame(performance_data)
    
    # Plot performance metrics
    col1, col2 = st.columns(2)
    with col1:
        st.line_chart(df_perf.set_index("date")["response_time"], use_container_width=True)
        st.caption("Response Time (ms)")
    
    with col2:
        st.line_chart(df_perf.set_index("date")["throughput"], use_container_width=True)
        st.caption("Throughput (requests/minute)")

# Render fraud detection
def render_fraud_detection():
    """Render the fraud detection interface."""
    st.header("Fraud Detection Agent")
    st.write("Analyze transactions for potential fraud patterns.")
    
    # Input form
    with st.form("fraud_detection_form"):
        st.subheader("Transaction Details")
        
        col1, col2 = st.columns(2)
        with col1:
            transaction_id = st.text_input("Transaction ID", value=f"TXN-{uuid.uuid4().hex[:8].upper()}")
            customer_id = st.text_input("Customer ID", value=f"CUST-{random.randint(10000, 99999)}")
            amount = st.number_input("Amount ($)", min_value=10.0, max_value=10000.0, value=random.uniform(100, 5000))
        
        with col2:
            timestamp = st.date_input("Transaction Date", value=datetime.now())
            location = st.selectbox("Location", ["United States", "United Kingdom", "Canada", "Australia", "India", "Germany", "France", "Japan"])
            device = st.selectbox("Device", ["Mobile App", "Web Browser", "API", "In-Person"])
        
        # Additional fields
        st.subheader("Additional Information")
        col1, col2, col3 = st.columns(3)
        with col1:
            frequency = st.slider("Transaction Frequency (last 30 days)", 0, 20, 5)
        with col2:
            account_age = st.slider("Account Age (days)", 1, 1000, 180)
        with col3:
            previous_flags = st.slider("Previous Flags", 0, 10, 0)
        
        submitted = st.form_submit_button("Analyze Transaction")
    
    # Process form submission
    if submitted:
        with st.spinner("Analyzing transaction for fraud patterns..."):
            # Simulate processing time
            time.sleep(1.5)
            
            # Create transaction data
            transaction_data = {
                "transaction_id": transaction_id,
                "customer_id": customer_id,
                "amount": amount,
                "timestamp": timestamp.strftime("%Y-%m-%d"),
                "location": location,
                "device": device,
                "frequency": frequency,
                "account_age": account_age,
                "previous_flags": previous_flags
            }
            
            # Calculate risk score based on input
            risk_factors = []
            
            # Amount factor
            if amount > 3000:
                risk_factors.append(0.8)
            elif amount > 1000:
                risk_factors.append(0.5)
            else:
                risk_factors.append(0.2)
            
            # Frequency factor
            if frequency > 15:
                risk_factors.append(0.7)
            elif frequency > 10:
                risk_factors.append(0.4)
            else:
                risk_factors.append(0.1)
            
            # Previous flags factor
            if previous_flags > 5:
                risk_factors.append(0.9)
            elif previous_flags > 0:
                risk_factors.append(0.6)
            else:
                risk_factors.append(0.1)
            
            # Calculate overall risk score
            risk_score = sum(risk_factors) / len(risk_factors)
            
            # Determine decision
            if risk_score >= 0.7:
                decision = "FLAG"
                recommended_action = "Send to human review"
            else:
                decision = "APPROVE"
                recommended_action = "Auto-approve"
            
            # Create result
            result = {
                **transaction_data,
                "risk_score": risk_score,
                "decision": decision,
                "recommended_action": recommended_action,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            # Add to history
            st.session_state.fraud_history.append(result)
            
            # Add log
            add_log(f"Fraud analysis completed for transaction {transaction_id} with risk score {risk_score:.2f}")
            
            # Display result
            st.success(f"Analysis completed with risk score: {risk_score:.2f}")
            
            # Result details
            st.subheader("Analysis Results")
            
            col1, col2 = st.columns(2)
            with col1:
                st.write("**Transaction Details**")
                st.json({k: v for k, v in transaction_data.items() if k not in ["timestamp", "risk_score", "decision"]})
            
            with col2:
                st.write("**Risk Assessment**")
                
                # Risk score gauge
                st.write(f"**Risk Score:** {risk_score:.2f}")
                
                # Create a simple gauge visualization
                risk_color = "green" if risk_score < 0.4 else "orange" if risk_score < 0.7 else "red"
                st.progress(risk_score)
                st.markdown(f"<p style='color:{risk_color};font-weight:bold;'>{decision}</p>", unsafe_allow_html=True)
                
                st.write(f"**Recommended Action:** {recommended_action}")
            
            # Risk factors breakdown
            st.subheader("Risk Factors")
            
            risk_factors_data = {
                "Factor": ["Transaction Amount", "Transaction Frequency", "Previous Flags"],
                "Risk Level": [risk_factors[0], risk_factors[1], risk_factors[2]]
            }
            
            df_risk = pd.DataFrame(risk_factors_data)
            
            # Convert risk levels to colors
            def color_risk(val):
                color = "green" if val < 0.4 else "orange" if val < 0.7 else "red"
                return f'background-color: {color}; color: white'
            
            st.dataframe(df_risk.style.applymap(color_risk, subset=["Risk Level"]))
    
    # History
    st.subheader("Recent Fraud Detection History")
    if st.session_state.fraud_history:
        df_history = pd.DataFrame(st.session_state.fraud_history)
        st.dataframe(df_history)
    else:
        st.info("No fraud detection history available.")

# Render KYC verification
def render_kyc_verification():
    """Render the KYC verification interface."""
    st.header("KYC Verification Agent")
    st.write("Verify customer identity and compliance with KYC regulations.")
    
    # Input form
    with st.form("kyc_verification_form"):
        st.subheader("Customer Information")
        
        col1, col2 = st.columns(2)
        with col1:
            customer_id = st.text_input("Customer ID", value=f"CUST-{random.randint(10000, 99999)}")
            full_name = st.text_input("Full Name", value="John Doe")
            dob = st.date_input("Date of Birth", value=datetime.now() - timedelta(days=365*30))
        
        with col2:
            email = st.text_input("Email", value="john.doe@example.com")
            phone = st.text_input("Phone Number", value="+1-555-123-4567")
            country = st.selectbox("Country", ["United States", "United Kingdom", "Canada", "Australia", "India", "Germany", "France", "Japan"])
        
        # ID verification
        st.subheader("ID Verification")
        col1, col2 = st.columns(2)
        with col1:
            id_type = st.selectbox("ID Type", ["Passport", "Driver's License", "National ID", "Other"])
            id_number = st.text_input("ID Number", value=f"ID-{random.randint(100000, 999999)}")
        
        with col2:
            id_verified = st.checkbox("ID Verified", value=True)
            address_verified = st.checkbox("Address Verified", value=True)
            sanctions_check_passed = st.checkbox("Sanctions Check Passed", value=True)
        
        submitted = st.form_submit_button("Verify Customer")
    
    # Process form submission
    if submitted:
        with st.spinner("Verifying customer information..."):
            # Simulate processing time
            time.sleep(1.5)
            
            # Create customer data
            customer_data = {
                "customer_id": customer_id,
                "full_name": full_name,
                "dob": dob.strftime("%Y-%m-%d"),
                "email": email,
                "phone": phone,
                "country": country,
                "id_type": id_type,
                "id_number": id_number,
                "id_verified": id_verified,
                "address_verified": address_verified,
                "sanctions_check_passed": sanctions_check_passed
            }
            
            # Calculate verification score
            checks = []
            
            # ID verification check
            if id_verified:
                checks.append(1.0)
            else:
                checks.append(0.0)
            
            # Address verification check
            if address_verified:
                checks.append(1.0)
            else:
                checks.append(0.0)
            
            # Sanctions check
            if sanctions_check_passed:
                checks.append(1.0)
            else:
                checks.append(0.0)
            
            # Calculate overall verification score
            verification_score = sum(checks) / len(checks)
            
            # Determine decision
            if verification_score >= 0.8:
                decision = "APPROVED"
                recommended_action = "Auto-approve"
            elif verification_score >= 0.6:
                decision = "REVIEW"
                recommended_action = "Send to manual review"
            else:
                decision = "REJECTED"
                recommended_action = "Auto-reject"
            
            # Create result
            result = {
                **customer_data,
                "verification_score": verification_score,
                "decision": decision,
                "recommended_action": recommended_action,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            # Add to history
            st.session_state.kyc_history.append(result)
            
            # Add log
            add_log(f"KYC verification completed for customer {customer_id} with score {verification_score:.2f}")
            
            # Display result
            st.success(f"Verification completed with score: {verification_score:.2f}")
            
            # Result details
            st.subheader("Verification Results")
            
            col1, col2 = st.columns(2)
            with col1:
                st.write("**Customer Details**")
                st.json({k: v for k, v in customer_data.items() if k not in ["id_verified", "address_verified", "sanctions_check_passed"]})
            
            with col2:
                st.write("**Verification Assessment**")
                
                # Verification score gauge
                st.write(f"**Verification Score:** {verification_score:.2f}")
                
                # Create a simple gauge visualization
                verification_color = "green" if verification_score >= 0.8 else "orange" if verification_score >= 0.6 else "red"
                st.progress(verification_score)
                st.markdown(f"<p style='color:{verification_color};font-weight:bold;'>{decision}</p>", unsafe_allow_html=True)
                
                st.write(f"**Recommended Action:** {recommended_action}")
            
            # Verification checks breakdown
            st.subheader("Verification Checks")
            
            verification_checks_data = {
                "Check": ["ID Verification", "Address Verification", "Sanctions Check"],
                "Status": [checks[0], checks[1], checks[2]]
            }
            
            df_checks = pd.DataFrame(verification_checks_data)
            
            # Convert status to colors
            def color_status(val):
                color = "green" if val >= 0.8 else "orange" if val >= 0.6 else "red"
                return f'background-color: {color}; color: white'
            
            st.dataframe(df_checks.style.applymap(color_status, subset=["Status"]))
    
    # History
    st.subheader("Recent KYC Verification History")
    if st.session_state.kyc_history:
        df_history = pd.DataFrame(st.session_state.kyc_history)
        st.dataframe(df_history)
    else:
        st.info("No KYC verification history available.")

# Generate sample data
def generate_sample_data():
    """Generate sample data for the demo."""
    # Generate sample fraud detection data
    for i in range(10):
        transaction_id = f"TXN-{uuid.uuid4().hex[:8].upper()}"
        customer_id = f"CUST-{random.randint(10000, 99999)}"
        amount = random.uniform(100, 5000)
        timestamp = (datetime.now() - timedelta(days=random.randint(0, 30))).strftime("%Y-%m-%d %H:%M:%S")
        location = random.choice(["United States", "United Kingdom", "Canada", "Australia", "India", "Germany", "France", "Japan"])
        device = random.choice(["Mobile App", "Web Browser", "API", "In-Person"])
        frequency = random.randint(1, 20)
        account_age = random.randint(1, 1000)
        previous_flags = random.randint(0, 10)
        
        # Calculate risk score
        risk_factors = [
            0.8 if amount > 3000 else 0.5 if amount > 1000 else 0.2,
            0.7 if frequency > 15 else 0.4 if frequency > 10 else 0.1,
            0.9 if previous_flags > 5 else 0.6 if previous_flags > 0 else 0.1
        ]
        risk_score = sum(risk_factors) / len(risk_factors)
        
        # Determine decision
        if risk_score >= 0.7:
            decision = "FLAG"
            recommended_action = "Send to human review"
        else:
            decision = "APPROVE"
            recommended_action = "Auto-approve"
        
        # Create result
        result = {
            "transaction_id": transaction_id,
            "customer_id": customer_id,
            "amount": amount,
            "timestamp": timestamp,
            "location": location,
            "device": device,
            "frequency": frequency,
            "account_age": account_age,
            "previous_flags": previous_flags,
            "risk_score": risk_score,
            "decision": decision,
            "recommended_action": recommended_action
        }
        
        # Add to history
        st.session_state.fraud_history.append(result)
    
    # Generate sample KYC verification data
    for i in range(10):
        customer_id = f"CUST-{random.randint(10000, 99999)}"
        full_name = f"Customer {i+1}"
        dob = (datetime.now() - timedelta(days=365*random.randint(20, 60))).strftime("%Y-%m-%d")
        email = f"customer{i+1}@example.com"
        phone = f"+1-555-{random.randint(100, 999)}-{random.randint(1000, 9999)}"
        country = random.choice(["United States", "United Kingdom", "Canada", "Australia", "India", "Germany", "France", "Japan"])
        id_type = random.choice(["Passport", "Driver's License", "National ID", "Other"])
        id_number = f"ID-{random.randint(100000, 999999)}"
        
        # Verification checks
        id_verified = random.random() > 0.2
        address_verified = random.random() > 0.2
        sanctions_check_passed = random.random() > 0.1
        
        # Calculate verification score
        checks = [
            1.0 if id_verified else 0.0,
            1.0 if address_verified else 0.0,
            1.0 if sanctions_check_passed else 0.0
        ]
        verification_score = sum(checks) / len(checks)
        
        # Determine decision
        if verification_score >= 0.8:
            decision = "APPROVED"
            recommended_action = "Auto-approve"
        elif verification_score >= 0.6:
            decision = "REVIEW"
            recommended_action = "Send to manual review"
        else:
            decision = "REJECTED"
            recommended_action = "Auto-reject"
        
        # Create result
        result = {
            "customer_id": customer_id,
            "full_name": full_name,
            "dob": dob,
            "email": email,
            "phone": phone,
            "country": country,
            "id_type": id_type,
            "id_number": id_number,
            "id_verified": id_verified,
            "address_verified": address_verified,
            "sanctions_check_passed": sanctions_check_passed,
            "verification_score": verification_score,
            "decision": decision,
            "recommended_action": recommended_action,
            "timestamp": (datetime.now() - timedelta(days=random.randint(0, 30))).strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Add to history
        st.session_state.kyc_history.append(result)

# Run the application
if __name__ == "__main__":
    main()
