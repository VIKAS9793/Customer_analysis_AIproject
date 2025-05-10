"""
Customer Analysis AI - Enhanced Stakeholder Demo

A comprehensive demo interface for showcasing the capabilities of the Customer Analysis AI system
with real-world compliance frameworks and sophisticated checks.
"""

import streamlit as st
import pandas as pd
import numpy as np
import time
from datetime import datetime, timedelta
import uuid
import logging
import random
import json
import sys
import os

# Add the project root to the path to import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import our compliance checks module
from demo.compliance_checks import ComplianceChecker, validate_customer_data, check_pii_data

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
    
    if 'compliance_checker' not in st.session_state:
        st.session_state.compliance_checker = ComplianceChecker()

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
        
        # Compliance frameworks
        st.sidebar.header("Compliance Frameworks")
        frameworks = st.session_state.compliance_checker.get_all_frameworks()
        for name, framework in frameworks.items():
            st.sidebar.info(f"📋 {name}: {framework.version}")
    
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
    
    # Compliance overview
    st.write("### Compliance Overview")
    
    # Create a compliance summary
    frameworks = st.session_state.compliance_checker.get_all_frameworks()
    framework_data = []
    
    for name, framework in frameworks.items():
        # Calculate mock compliance percentage
        compliance_pct = random.uniform(0.85, 0.98)
        framework_data.append({
            "Framework": name,
            "Version": framework.version,
            "Compliance": f"{compliance_pct:.1%}",
            "Status": "Compliant" if compliance_pct > 0.9 else "Partially Compliant"
        })
    
    df_compliance = pd.DataFrame(framework_data)
    st.dataframe(df_compliance)
    
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
            
            # Check for PII data
            pii_results = check_pii_data(transaction_data)
            if pii_results["pii_detected"]:
                st.warning("⚠️ PII data detected in transaction")
                st.json(pii_results)
    
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
                "sanctions_check_passed": sanctions_check_passed,
                "timestamp": datetime.now().isoformat()
            }
            
            # Validate customer data
            is_valid, validation_errors = validate_customer_data(customer_data)
            
            if not is_valid:
                st.error("Customer data validation failed")
                for error in validation_errors:
                    st.error(error)
                return
            
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
            
            # Check for PII data
            pii_results = check_pii_data(customer_data)
            if pii_results["pii_detected"]:
                st.warning("⚠️ PII data detected in customer information")
                st.json(pii_results)
    
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

# Render compliance checks
def render_compliance_checks():
    """Render the enhanced compliance checks interface."""
    st.header("Compliance Checks")
    st.write("Verify compliance with regulatory requirements using real-world frameworks.")
    
    # Framework selection
    st.subheader("Compliance Frameworks")
    frameworks = st.session_state.compliance_checker.get_all_frameworks()
    
    framework_options = list(frameworks.keys())
    selected_frameworks = st.multiselect(
        "Select Frameworks to Check",
        framework_options,
        default=["GDPR", "DPDP"]
    )
    
    # Input form
    with st.form("compliance_form"):
        st.subheader("Data for Compliance Check")
        
        col1, col2 = st.columns(2)
        with col1:
            customer_id = st.text_input("Customer ID", value=f"CUST-{random.randint(10000, 99999)}")
            data_location = st.selectbox("Data Location", ["United States", "European Union", "India", "United Kingdom", "Australia", "Canada", "Japan", "Other"])
            retention_days = st.slider("Data Retention Period (days)", 30, 365, 90)
        
        with col2:
            has_consent = st.checkbox("Customer Consent Obtained", value=True)
            has_encryption = st.checkbox("Data Encryption Enabled", value=True)
            has_key_rotation = st.checkbox("Key Rotation Configured", value=True)
        
        # Additional compliance fields
        st.subheader("Additional Data Fields")
        col1, col2, col3 = st.columns(3)
        with col1:
            has_audit_trail = st.checkbox("Audit Trail Enabled", value=True)
        with col2:
            has_internal_controls = st.checkbox("Internal Controls Documented", value=True)
        with col3:
            has_realtime_reporting = st.checkbox("Real-time Reporting Enabled", value=False)
            
        # PCI DSS specific fields
        st.subheader("Payment Card Information")
        col1, col2 = st.columns(2)
        with col1:
            contains_pci_data = st.checkbox("Contains Payment Card Data", value=False)
        with col2:
            pci_data_masked = st.checkbox("PCI Data Masked", value=True, disabled=not contains_pci_data)
        
        # Purpose statement
        st.subheader("Data Purpose")
        purpose = st.text_area("Purpose Statement", value="Customer analysis for service improvement and fraud detection")
        
        submitted = st.form_submit_button("Run Compliance Check")
    
    # Process form submission
    if submitted:
        with st.spinner("Running comprehensive compliance checks..."):
            # Simulate processing time
            time.sleep(2.0)
            
            # Create compliance data
            compliance_data = {
                "customer_id": customer_id,
                "location": data_location,
                "timestamp": datetime.now().isoformat(),
                "consent": has_consent,
                "encryption_key": "sample_key" if has_encryption else None,
                "key_rotation": has_key_rotation,
                "data_retention_days": retention_days,
                "audit_trail": has_audit_trail,
                "internal_controls": has_internal_controls,
                "realtime_reporting": has_realtime_reporting,
                "contains_pci_data": contains_pci_data,
                "pci_data_masked": pci_data_masked,
                "purpose": purpose,
                "logging_enabled": True
            }
            
            # Validate the data
            is_valid, validation_errors = validate_customer_data(compliance_data)
            
            if not is_valid:
                st.error("Data validation failed")
                for error in validation_errors:
                    st.error(error)
                return
            
            # Run compliance checks using the enhanced framework
            if not selected_frameworks:
                st.warning("Please select at least one compliance framework")
                return
                
            compliance_results = st.session_state.compliance_checker.check_compliance(
                compliance_data, 
                selected_frameworks
            )
            
            # Generate detailed report
            compliance_report = st.session_state.compliance_checker.generate_compliance_report(
                compliance_results
            )
            
            # Create result
            result = {
                **compliance_data,
                "compliance_score": compliance_results["compliance_score"],
                "compliance_status": compliance_results["compliance_status"],
                "compliance_results": compliance_results["framework_results"],
                "compliance_report": compliance_report,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            # Add to history
            st.session_state.compliance_history.append(result)
            
            # Add log
            add_log(f"Compliance check completed for customer {customer_id} with score {compliance_results['compliance_score']:.2f}")
            
            # Display result
            st.success(f"Compliance check completed with score: {compliance_results['compliance_score']:.2f}")
            
            # Result details
            st.subheader("Compliance Results")
            
            # Display compliance score with gauge
            col1, col2 = st.columns([1, 2])
            with col1:
                st.write(f"**Overall Compliance Score:**")
                compliance_color = "green" if compliance_results['compliance_score'] >= 0.9 else "orange" if compliance_results['compliance_score'] >= 0.7 else "red"
                st.markdown(f"<h1 style='text-align: center; color: {compliance_color};'>{compliance_results['compliance_score']:.2f}</h1>", unsafe_allow_html=True)
                st.markdown(f"<h3 style='text-align: center; color: {compliance_color};'>{compliance_results['compliance_status']}</h3>", unsafe_allow_html=True)
            
            with col2:
                # Summary metrics
                summary = compliance_report["summary"]
                st.write("**Compliance Summary**")
                
                metrics_data = {
                    "Metric": ["Total Checks", "Compliant", "Non-Compliant", "Critical Violations", "High Violations", "Medium Violations"],
                    "Value": [
                        summary["total_checks"],
                        summary["compliant_checks"],
                        summary["non_compliant_checks"],
                        summary["critical_violations"],
                        summary["high_violations"],
                        summary["medium_violations"]
                    ]
                }
                
                df_metrics = pd.DataFrame(metrics_data)
                st.dataframe(df_metrics)
            
            # Framework-specific results
            st.subheader("Framework-Specific Results")
            
            tabs = st.tabs(selected_frameworks)
            
            for i, framework_name in enumerate(selected_frameworks):
                with tabs[i]:
                    framework_results = compliance_results["framework_results"].get(framework_name, {})
                    
                    # Create a dataframe for the framework results
                    if framework_results:
                        results_data = []
                        for req_id, result in framework_results.items():
                            results_data.append({
                                "Requirement": req_id,
                                "Compliant": result["compliant"],
                                "Details": result["details"]
                            })
                        
                        if results_data:
                            df_framework = pd.DataFrame(results_data)
                            
                            # Style the dataframe
                            def color_compliance(val):
                                return 'background-color: green; color: white' if val else 'background-color: red; color: white'
                            
                            st.dataframe(df_framework.style.applymap(color_compliance, subset=["Compliant"]))
                    else:
                        st.info(f"No results available for {framework_name}")
            
            # Violations
            if "violations_by_framework" in compliance_report and compliance_report["violations_by_framework"]:
                st.subheader("Compliance Violations")
                
                for framework_name, violations in compliance_report["violations_by_framework"].items():
                    st.write(f"**{framework_name} Violations**")
                    
                    violations_data = []
                    for violation in violations:
                        violations_data.append({
                            "Requirement": f"{violation['requirement_id']}: {violation['description']}",
                            "Severity": violation["severity"],
                            "Details": violation["details"]
                        })
                    
                    if violations_data:
                        df_violations = pd.DataFrame(violations_data)
                        
                        # Style the dataframe
                        def color_severity(val):
                            if val == "critical":
                                return 'background-color: darkred; color: white'
                            elif val == "high":
                                return 'background-color: red; color: white'
                            else:
                                return 'background-color: orange; color: white'
                        
                        st.dataframe(df_violations.style.applymap(color_severity, subset=["Severity"]))
            
            # Check for PII data
            pii_results = check_pii_data(compliance_data)
            if pii_results["pii_detected"]:
                st.warning("⚠️ PII data detected in compliance data")
                st.json(pii_results)
    
    # History
    st.subheader("Recent Compliance Check History")
    if st.session_state.compliance_history:
        # Create a simplified view of compliance history
        history_data = []
        for check in st.session_state.compliance_history:
            history_data.append({
                "timestamp": check["timestamp"],
                "customer_id": check["customer_id"],
                "location": check["location"],
                "compliance_score": check["compliance_score"],
                "compliance_status": check["compliance_status"]
            })
        
        df_history = pd.DataFrame(history_data)
        st.dataframe(df_history)
    else:
        st.info("No compliance check history available.")

# Render customer insights
def render_customer_insights():
    """Render the customer insights interface."""
    st.header("Customer Insights Agent")
    st.write("Generate insights from customer data using AI analysis.")
    
    # Input form
    with st.form("insights_form"):
        st.subheader("Insight Query")
        
        query_type = st.selectbox(
            "Insight Type", 
            ["Customer Satisfaction", "Support Tickets", "Sales Performance", "Product Usage", "Customer Segmentation"]
        )
        
        query = st.text_area(
            "Query", 
            value=f"Analyze {query_type.lower()} patterns and provide key insights"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            data_source = st.multiselect(
                "Data Sources",
                ["customer_data", "sales_data", "support_tickets", "product_usage", "feedback_surveys"],
                default=["customer_data"]
            )
        
        with col2:
            time_period = st.selectbox(
                "Time Period",
                ["Last 7 days", "Last 30 days", "Last 90 days", "Last 12 months", "All time"]
            )
        
        # Filters
        st.subheader("Filters")
        col1, col2, col3 = st.columns(3)
        with col1:
            customer_segment = st.selectbox(
                "Customer Segment",
                ["All Segments", "Enterprise", "SMB", "Consumer", "Government"]
            )
        with col2:
            region = st.selectbox(
                "Region",
                ["All Regions", "North America", "Europe", "Asia Pacific", "Latin America", "Middle East & Africa"]
            )
        with col3:
            min_confidence = st.slider("Minimum Confidence", 0.5, 1.0, 0.85)
        
        submitted = st.form_submit_button("Generate Insights")
    
    # Process form submission
    if submitted:
        with st.spinner("Generating customer insights..."):
            # Simulate processing time
            time.sleep(2.0)
            
            # Create query data
            query_data = {
                "query": query,
                "query_type": query_type,
                "data_sources": data_source,
                "time_period": time_period,
                "filters": {
                    "customer_segment": customer_segment,
                    "region": region,
                    "min_confidence": min_confidence
                }
            }
            
            # Generate insights based on query type
            insights = []
            
            if query_type == "Customer Satisfaction":
                insights.append({
                    "title": "Customer Satisfaction Trends",
                    "description": "Customer satisfaction has increased by 15% over the last quarter, with the highest improvement in the enterprise segment.",
                    "metrics": [
                        {"label": "Overall Satisfaction", "value": "85%", "delta": "+15%"},
                        {"label": "Enterprise Segment", "value": "92%", "delta": "+18%"},
                        {"label": "SMB Segment", "value": "78%", "delta": "+12%"}
                    ],
                    "confidence": 0.92,
                    "data_source": "customer_data"
                })
                
                insights.append({
                    "title": "Satisfaction Drivers",
                    "description": "The top factors driving customer satisfaction are product reliability, customer support response time, and ease of use.",
                    "metrics": [
                        {"label": "Product Reliability", "value": "94%", "delta": "+5%"},
                        {"label": "Support Response", "value": "89%", "delta": "+12%"},
                        {"label": "Ease of Use", "value": "82%", "delta": "+8%"}
                    ],
                    "confidence": 0.88,
                    "data_source": "feedback_surveys"
                })
            
            elif query_type == "Support Tickets":
                insights.append({
                    "title": "Support Ticket Analysis",
                    "description": "The average resolution time for support tickets has decreased by 25% this month. The most common issues are related to account access and integration problems.",
                    "metrics": [
                        {"label": "Avg. Resolution Time", "value": "4.5 hours", "delta": "-25%"},
                        {"label": "Account Issues", "value": "42%", "delta": "+5%"},
                        {"label": "Integration Issues", "value": "35%", "delta": "-3%"}
                    ],
                    "confidence": 0.95,
                    "data_source": "support_tickets"
                })
                
                insights.append({
                    "title": "Support Channel Effectiveness",
                    "description": "Chat support has the highest customer satisfaction rating, followed by email and phone support.",
                    "metrics": [
                        {"label": "Chat Support", "value": "92%", "delta": "+8%"},
                        {"label": "Email Support", "value": "85%", "delta": "+3%"},
                        {"label": "Phone Support", "value": "78%", "delta": "-2%"}
                    ],
                    "confidence": 0.91,
                    "data_source": "support_tickets"
                })
            
            elif query_type == "Sales Performance":
                insights.append({
                    "title": "Sales Performance",
                    "description": "Q2 sales have exceeded targets by 12%, with the strongest performance in the EMEA region. Product upsells have increased by 28% compared to last quarter.",
                    "metrics": [
                        {"label": "Q2 Sales", "value": "$2.8M", "delta": "+12%"},
                        {"label": "EMEA Region", "value": "$1.2M", "delta": "+18%"},
                        {"label": "Upsell Rate", "value": "38%", "delta": "+28%"}
                    ],
                    "confidence": 0.89,
                    "data_source": "sales_data"
                })
                
                insights.append({
                    "title": "Sales Cycle Analysis",
                    "description": "The average sales cycle has decreased by 15 days for enterprise customers. The most effective lead sources are referrals and content marketing.",
                    "metrics": [
                        {"label": "Avg. Sales Cycle", "value": "45 days", "delta": "-15 days"},
                        {"label": "Referral Conversion", "value": "28%", "delta": "+8%"},
                        {"label": "Content Marketing", "value": "22%", "delta": "+5%"}
                    ],
                    "confidence": 0.87,
                    "data_source": "sales_data"
                })
            
            elif query_type == "Product Usage":
                insights.append({
                    "title": "Product Usage Patterns",
                    "description": "Feature adoption has increased across all user segments. The new analytics dashboard has seen a 45% adoption rate in its first month.",
                    "metrics": [
                        {"label": "Feature Adoption", "value": "78%", "delta": "+12%"},
                        {"label": "Analytics Dashboard", "value": "45%", "delta": "New"},
                        {"label": "Daily Active Users", "value": "12.5K", "delta": "+8%"}
                    ],
                    "confidence": 0.93,
                    "data_source": "product_usage"
                })
                
                insights.append({
                    "title": "User Engagement",
                    "description": "User session duration has increased by 15% on average. Mobile app usage has grown by 22% compared to the previous quarter.",
                    "metrics": [
                        {"label": "Session Duration", "value": "18 min", "delta": "+15%"},
                        {"label": "Mobile App Usage", "value": "35%", "delta": "+22%"},
                        {"label": "Feature Interactions", "value": "28/session", "delta": "+5"}
                    ],
                    "confidence": 0.90,
                    "data_source": "product_usage"
                })
            
            elif query_type == "Customer Segmentation":
                insights.append({
                    "title": "Customer Segmentation Analysis",
                    "description": "Enterprise customers show the highest retention rate at 94%, while SMB customers have the fastest growth rate at 28% YoY.",
                    "metrics": [
                        {"label": "Enterprise Retention", "value": "94%", "delta": "+2%"},
                        {"label": "SMB Growth", "value": "28%", "delta": "+8%"},
                        {"label": "Consumer Acquisition", "value": "15%", "delta": "+3%"}
                    ],
                    "confidence": 0.91,
                    "data_source": "customer_data"
                })
                
                insights.append({
                    "title": "Segment Behavior Patterns",
                    "description": "Enterprise customers primarily use advanced features, while SMB customers focus on core functionality and reporting.",
                    "metrics": [
                        {"label": "Enterprise: Advanced", "value": "85%", "delta": "+5%"},
                        {"label": "SMB: Core Features", "value": "92%", "delta": "+3%"},
                        {"label": "SMB: Reporting", "value": "78%", "delta": "+12%"}
                    ],
                    "confidence": 0.88,
                    "data_source": "product_usage"
                })
            
            # Create result
            result = {
                **query_data,
                "insights": insights,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            # Add to history
            st.session_state.insight_history.append(result)
            
            # Add log
            add_log(f"Generated {len(insights)} insights for query: {query_type}")
            
            # Display result
            st.success(f"Generated {len(insights)} insights with high confidence")
            
            # Display insights
            for insight in insights:
                st.subheader(insight["title"])
                
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.write(insight["description"])
                    
                    # Display metrics
                    for metric in insight["metrics"]:
                        col_metric, col_value, col_delta = st.columns([2, 1, 1])
                        with col_metric:
                            st.write(f"**{metric['label']}:**")
                        with col_value:
                            st.write(metric["value"])
                        with col_delta:
                            delta_color = "green" if "+" in metric["delta"] else "red" if "-" in metric["delta"] else "gray"
                            st.markdown(f"<span style='color:{delta_color}'>{metric['delta']}</span>", unsafe_allow_html=True)
                
                with col2:
                    st.write("**Confidence:**")
                    st.progress(insight["confidence"])
                    st.write(f"{insight['confidence']:.2f}")
                    
                    st.write("**Source:**")
                    st.write(insight["data_source"])
                
                st.markdown("---")
    
    # History
    st.subheader("Recent Insight Queries")
    if st.session_state.insight_history:
        for idx, insight_query in enumerate(reversed(st.session_state.insight_history)):
            if idx < 5:  # Show only the 5 most recent queries
                st.write(f"**Query:** {insight_query['query_type']} ({insight_query['timestamp']})")
                st.write(f"**Data Sources:** {', '.join(insight_query['data_sources'])}")
                st.write(f"**Insights Generated:** {len(insight_query['insights'])}")
                st.markdown("---")
    else:
        st.info("No insight query history available.")

# Render system logs
def render_system_logs():
    """Render the system logs interface."""
    st.header("System Logs")
    st.write("View system activity and agent logs.")
    
    # Log filtering
    col1, col2 = st.columns(2)
    with col1:
        log_level = st.selectbox("Log Level", ["All", "INFO", "WARNING", "ERROR"])
    with col2:
        log_search = st.text_input("Search Logs", value="")
    
    # Display logs
    st.subheader("Activity Logs")
    
    if st.session_state.logs:
        # Filter logs
        filtered_logs = st.session_state.logs
        
        if log_level != "All":
            filtered_logs = [log for log in filtered_logs if log["level"] == log_level]
        
        if log_search:
            filtered_logs = [log for log in filtered_logs if log_search.lower() in log["message"].lower()]
        
        # Display logs
        for log in reversed(filtered_logs):
            log_color = "green" if log["level"] == "INFO" else "orange" if log["level"] == "WARNING" else "red"
            st.markdown(f"<p><span style='color:gray'>{log['timestamp']}</span> <span style='color:{log_color};font-weight:bold;'>[{log['level']}]</span> {log['message']}</p>", unsafe_allow_html=True)
    else:
        st.info("No logs available.")
    
    # System metrics
    st.subheader("System Metrics")
    
    # Create sample metrics data
    dates = [datetime.now() - timedelta(hours=x) for x in range(24, 0, -1)]
    metrics_data = {
        "timestamp": [d.strftime("%H:%M") for d in dates],
        "cpu_usage": [random.uniform(10, 80) for _ in dates],
        "memory_usage": [random.uniform(20, 70) for _ in dates],
        "api_requests": [random.randint(10, 100) for _ in dates],
        "response_time": [random.uniform(80, 200) for _ in dates]
    }
    
    df_metrics = pd.DataFrame(metrics_data)
    
    # Display metrics
    col1, col2 = st.columns(2)
    
    with col1:
        st.line_chart(df_metrics.set_index("timestamp")["cpu_usage"], use_container_width=True)
        st.caption("CPU Usage (%)")
        
        st.line_chart(df_metrics.set_index("timestamp")["api_requests"], use_container_width=True)
        st.caption("API Requests (per hour)")
    
    with col2:
        st.line_chart(df_metrics.set_index("timestamp")["memory_usage"], use_container_width=True)
        st.caption("Memory Usage (%)")
        
        st.line_chart(df_metrics.set_index("timestamp")["response_time"], use_container_width=True)
        st.caption("Response Time (ms)")

# Run the application
if __name__ == "__main__":
    main()
