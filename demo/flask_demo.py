"""
FinConnectAI - Flask Demo

A lightweight Flask-based demo interface for showcasing the capabilities 
of the FinConnectAI system to stakeholders.
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for
import os
import json
import random
# Import the region-specific thresholds module
from region_thresholds import calculate_amount_risk
from datetime import datetime, timedelta
import uuid
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__, static_url_path='/static', static_folder='.')
app.secret_key = "finconnectai_demo_secret_key"

# In-memory storage for demo data
demo_data = {
    "fraud_history": [],
    "kyc_history": [],
    "compliance_history": [],
    "insights_history": [],
    "logs": []
}

# Add a log entry
def add_log(message, level="INFO"):
    """Add a log entry to the demo logs."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    demo_data["logs"].append({
        "timestamp": timestamp,
        "level": level,
        "message": message
    })
    logger.info(f"{level}: {message}")

# Routes
@app.route('/')
def index():
    """Render the main dashboard."""
    # Generate sample data if none exists
    if len(demo_data["fraud_history"]) == 0:
        generate_sample_data()
    
    return render_template('index.html', 
                          fraud_history=demo_data["fraud_history"][-5:],
                          kyc_history=demo_data["kyc_history"][-5:])

@app.route('/fraud', methods=['GET', 'POST'])
def fraud_detection():
    """Render the fraud detection page."""
    # Default values
    transaction_id = f"TXN-{uuid.uuid4().hex[:8].upper()}"
    customer_id = f"CUST-{random.randint(10000, 99999)}"
    amount = 25000.0  # Increased default amount for better fraud detection testing
    location = "United States"
    device = "Web Browser"
    frequency = 5
    account_age = 180
    previous_flags = 0
    result = None
    
    # Available options
    locations = ["United States", "United Kingdom", "Canada", "Australia", "India", "Germany", "France", "Japan"]
    devices = ["Mobile App", "Web Browser", "API", "In-Person"]
    
    # Set currency based on location
    currency_mapping = {
        "United States": {"symbol": "$", "code": "USD"},
        "United Kingdom": {"symbol": "£", "code": "GBP"},
        "Canada": {"symbol": "$", "code": "CAD"},
        "Australia": {"symbol": "$", "code": "AUD"},
        "India": {"symbol": "₹", "code": "INR"},
        "Germany": {"symbol": "€", "code": "EUR"},
        "France": {"symbol": "€", "code": "EUR"},
        "Japan": {"symbol": "¥", "code": "JPY"}
    }
    
    # Default currency
    currency = currency_mapping.get(location, {"symbol": "$", "code": "USD"})
    
    # Process form submission
    if request.method == 'POST':
        # Get form data
        transaction_id = request.form.get('transaction_id', transaction_id)
        customer_id = request.form.get('customer_id', customer_id)
        amount = float(request.form.get('amount', amount))
        location = request.form.get('location', location)
        device = request.form.get('device', device)
        frequency = int(request.form.get('frequency', frequency))
        account_age = int(request.form.get('account_age', account_age))
        previous_flags = int(request.form.get('previous_flags', previous_flags))
        
        # Update currency based on selected location
        currency = currency_mapping.get(location, {"symbol": "$", "code": "USD"})
        
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
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
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
        demo_data["fraud_history"].append(result)
        
        # Add log
        add_log(f"Fraud analysis completed for transaction {transaction_id} with risk score {risk_score:.2f}")
    
    return render_template('fraud.html',
                          transaction_id=transaction_id,
                          customer_id=customer_id,
                          amount=amount,
                          location=location,
                          device=device,
                          frequency=frequency,
                          account_age=account_age,
                          previous_flags=previous_flags,
                          locations=locations,
                          currency_symbol=currency["symbol"],
                          currency_code=currency["code"],
                          devices=devices,
                          result=result,
                          history=demo_data["fraud_history"][-10:])

@app.route('/kyc', methods=['GET', 'POST'])
def kyc_verification():
    """Render the KYC verification page."""
    # Default values
    customer_id = f"CUST-{random.randint(10000, 99999)}"
    full_name = "John Doe"
    dob = "1990-01-01"
    email = "john.doe@example.com"
    phone = "+1-555-123-4567"
    country = "United States"
    id_type = "Passport"
    id_number = f"ID-{random.randint(100000, 999999)}"
    result = None
    
    # Available options
    countries = ["United States", "United Kingdom", "Canada", "Australia", "India", "Germany", "France", "Japan"]
    id_types = ["Passport", "Driver's License", "National ID", "Other"]
    
    # Process form submission
    if request.method == 'POST':
        # Get form data
        customer_id = request.form.get('customer_id', customer_id)
        full_name = request.form.get('full_name', full_name)
        dob = request.form.get('dob', dob)
        email = request.form.get('email', email)
        phone = request.form.get('phone', phone)
        country = request.form.get('country', country)
        id_type = request.form.get('id_type', id_type)
        id_number = request.form.get('id_number', id_number)
        
        # Verification checks (simulated)
        id_verified = random.random() > 0.2
        address_verified = random.random() > 0.2
        face_match = random.random() > 0.2
        document_authentic = random.random() > 0.2
        pep_check = random.random() > 0.1
        sanctions_check = random.random() > 0.1
        
        # Calculate verification score
        verification_factors = [
            1.0 if id_verified else 0.0,
            1.0 if address_verified else 0.0,
            1.0 if face_match else 0.0,
            1.0 if document_authentic else 0.0,
            0.0 if not pep_check else 1.0,
            0.0 if not sanctions_check else 1.0
        ]
        verification_score = sum(verification_factors) / len(verification_factors)
        
        # Determine decision
        if verification_score >= 0.8:
            decision = "VERIFIED"
            recommended_action = "Auto-approve"
        elif verification_score >= 0.6:
            decision = "REVIEW"
            recommended_action = "Manual review required"
        else:
            decision = "REJECTED"
            recommended_action = "Request additional documentation"
        
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
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "id_verified": id_verified,
            "address_verified": address_verified,
            "face_match": face_match,
            "document_authentic": document_authentic,
            "pep_check": pep_check,
            "sanctions_check": sanctions_check,
            "verification_score": verification_score,
            "decision": decision,
            "recommended_action": recommended_action
        }
        
        # Add to history
        demo_data["kyc_history"].append(result)
        
        # Add log
        add_log(f"KYC verification completed for customer {customer_id} with verification score {verification_score:.2f}")
    
    return render_template('kyc.html',
                          customer_id=customer_id,
                          full_name=full_name,
                          dob=dob,
                          email=email,
                          phone=phone,
                          country=country,
                          id_type=id_type,
                          id_number=id_number,
                          countries=countries,
                          id_types=id_types,
                          result=result,
                          history=demo_data["kyc_history"][-10:])

@app.route('/compliance', methods=['GET', 'POST'])
def compliance_checks():
    """Render the compliance checks page."""
    # Default values
    data_source = "Customer Database"
    region = "India (North)"  # Default to India for Indian market focus
    data_type = "Personal Information"
    frameworks = ["GDPR", "DPDP Act 2023", "SOX", "PCI DSS", "RBI Data Protection", "IRDAI Guidelines", "SEBI Guidelines"]
    selected_frameworks = ["DPDP Act 2023", "RBI Data Protection"]  # Default to Indian frameworks
    result = None
    
    # Available options
    data_sources = ["Customer Database", "Transaction Records", "Marketing Database", "Employee Records"]
    regions = ["United States", "European Union", "India (North)", "India (South)", "India (East)", "India (West)", "India (Central)", "United Kingdom", "Australia", "Canada", "Japan"]
    data_types = ["Personal Information", "Financial Data", "Health Records", "Biometric Data", "Location Data", "Aadhaar Data", "PAN Card Information"]
    all_frameworks = ["GDPR", "DPDP Act 2023", "SOX", "PCI DSS", "HIPAA", "CCPA", "GLBA", "RBI Data Protection", "IRDAI Guidelines", "SEBI Guidelines"]
    
    # Process form submission
    if request.method == 'POST':
        # Get form data
        data_source = request.form.get('data_source', data_source)
        region = request.form.get('region', region)
        data_type = request.form.get('data_type', data_type)
        selected_frameworks = request.form.getlist('frameworks')
        
        # If no frameworks selected, suggest appropriate ones based on region
        if not selected_frameworks:
            if region.startswith("India"):
                selected_frameworks = ["DPDP Act 2023", "RBI Data Protection"]
                # Add specific industry frameworks based on data type
                if data_type == "Financial Data":
                    selected_frameworks.append("SEBI Guidelines")
                if data_type == "Health Records":
                    selected_frameworks.append("IRDAI Guidelines")
            elif region == "European Union" or region == "United Kingdom":
                selected_frameworks = ["GDPR"]
            elif region == "United States":
                selected_frameworks = ["CCPA", "GLBA"]
                if data_type == "Health Records":
                    selected_frameworks.append("HIPAA")
            else:
                # Default selection for other regions
                selected_frameworks = ["GDPR", "DPDP Act 2023"]
        
        # Simulated compliance checks
        compliance_results = {}
        overall_score = 0.0
        
        # Apply regional adjustments for India
        is_india_region = any(region.startswith("India") for region in [region])
        
        for framework in selected_frameworks:
            # Generate random compliance score between 0.7 and 1.0
            # Adjust scores for Indian regions and frameworks
            base_score = random.uniform(0.7, 1.0)
            
            # Boost scores for Indian frameworks in Indian regions
            if is_india_region and framework in ["DPDP Act 2023", "RBI Data Protection", "IRDAI Guidelines", "SEBI Guidelines"]:
                score = min(1.0, base_score + 0.05)  # Slight boost for local compliance
            else:
                score = base_score
                
            overall_score += score
            
            # Determine compliance status based on score
            if score >= 0.9:
                status = "Compliant"
                recommendations = ["Maintain current practices", "Regular audits recommended"]
            elif score >= 0.8:
                status = "Mostly Compliant"
                recommendations = ["Minor improvements needed", "Update documentation"]
            else:
                status = "Partially Compliant"
                recommendations = ["Significant improvements needed", "Review data handling procedures"]
            
            # Generate random findings
            findings = []
            if framework == "GDPR":
                if random.random() > 0.7:
                    findings.append("Data retention periods not clearly defined")
                if random.random() > 0.8:
                    findings.append("Consent mechanisms need improvement")
                if is_india_region and random.random() > 0.6:
                    findings.append("Cross-border data transfer mechanisms need review")
            
            elif framework == "DPDP Act 2023":
                if random.random() > 0.7:
                    findings.append("Data localization requirements not fully met")
                if random.random() > 0.8:
                    findings.append("Security safeguards need enhancement")
                if random.random() > 0.75:
                    findings.append("Consent framework needs to be updated per 2023 requirements")
                if random.random() > 0.8:
                    findings.append("Data Principal rights implementation incomplete")
            
            elif framework == "RBI Data Protection":
                if random.random() > 0.7:
                    findings.append("Payment data storage compliance needs improvement")
                if random.random() > 0.8:
                    findings.append("Audit mechanisms for financial data access incomplete")
                if random.random() > 0.75:
                    findings.append("Customer financial data encryption standards need upgrade")
            
            elif framework == "IRDAI Guidelines":
                if random.random() > 0.7:
                    findings.append("Insurance data protection measures need enhancement")
                if random.random() > 0.8:
                    findings.append("Customer consent for health data usage needs review")
                if random.random() > 0.75:
                    findings.append("Data retention policies for insurance records need updating")
            
            elif framework == "SEBI Guidelines":
                if random.random() > 0.7:
                    findings.append("Investment data protection protocols need strengthening")
                if random.random() > 0.8:
                    findings.append("Market data handling procedures need review")
                if random.random() > 0.75:
                    findings.append("Investor data access controls need enhancement")
            
            elif framework == "SOX":
                if random.random() > 0.7:
                    findings.append("Audit trail gaps identified")
                if random.random() > 0.8:
                    findings.append("Internal controls need strengthening")
            
            elif framework == "PCI DSS":
                if random.random() > 0.7:
                    findings.append("Encryption standards not consistently applied")
                if random.random() > 0.8:
                    findings.append("Access control mechanisms need review")
            
            # Add framework results
            compliance_results[framework] = {
                "score": score,
                "status": status,
                "findings": findings,
                "recommendations": recommendations
            }
        
        # Calculate overall compliance score
        if selected_frameworks:
            overall_score /= len(selected_frameworks)
        
        # Create result
        result = {
            "data_source": data_source,
            "region": region,
            "data_type": data_type,
            "frameworks": selected_frameworks,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "overall_score": overall_score,
            "framework_results": compliance_results
        }
        
        # Add to history
        demo_data["compliance_history"].append(result)
        
        # Add log
        add_log(f"Compliance check completed for {data_source} with overall score {overall_score:.2f}")
    
    return render_template('compliance.html',
                          data_source=data_source,
                          region=region,
                          data_type=data_type,
                          selected_frameworks=selected_frameworks,
                          data_sources=data_sources,
                          regions=regions,
                          data_types=data_types,
                          all_frameworks=all_frameworks,
                          result=result,
                          history=demo_data["compliance_history"][-10:])

@app.route('/insights', methods=['GET', 'POST'])
def customer_insights():
    """Render the customer insights page."""
    try:
        # Default values
        customer_segment = "All Customers"
        time_period = "Last 30 Days"
        analysis_type = "Spending Patterns"
        region = "India (North)"
        query = ""
        result = None
        
        # Available options
        segments = ["All Customers", "High Value", "New Customers", "At Risk", "Dormant Accounts", "Premium Tier", "Tier 1 Cities", "Tier 2 Cities", "Rural Customers"]
        time_periods = ["Last 7 Days", "Last 30 Days", "Last 90 Days", "Last 12 Months", "Year to Date", "Festival Season", "Monsoon Season"]
        analysis_types = ["Spending Patterns", "Demographic Analysis", "Churn Prediction", "Lifetime Value", "Product Affinity", "Regional Preferences", "Digital Adoption"]
        regions = ["All Regions", "India (North)", "India (South)", "India (East)", "India (West)", "India (Central)", "United States", "European Union", "United Kingdom", "Asia Pacific"]
        
        # Process form submission
        if request.method == 'POST':
            # Get form data
            customer_segment = request.form.get('customer_segment', customer_segment)
            time_period = request.form.get('time_period', time_period)
            analysis_type = request.form.get('analysis_type', analysis_type)
            region = request.form.get('region', region)
            query = request.form.get('query', query)

            # Initialize insights and charts
            insights = []
            charts = {}
            
            # Determine region-specific settings
            is_india_region = "India" in region or region == "All Regions"
            
            # Set currency based on region
            if "India" in region:
                currency = "₹"
                currency_name = "INR"
            elif "United States" in region:
                currency = "$"
                currency_name = "USD"
            elif "European Union" in region:
                currency = "€"
                currency_name = "EUR"
            elif "United Kingdom" in region:
                currency = "£"
                currency_name = "GBP"
            elif "Asia Pacific" in region and not is_india_region:
                currency = "$"
                currency_name = "USD"
            else:
                # Default
                currency = "$"
                currency_name = "USD"
            
            # Generate insights based on analysis type and region
            if analysis_type == "Spending Patterns":
                if is_india_region:
                    insights = [
                        "UPI transactions increased by 45% compared to previous period",
                        "Festival season spending is 78% higher than regular months",
                        f"Average transaction value increased by {currency}850 compared to last quarter",
                        "Mobile payments now account for 72% of all transactions",
                        "Tier 2 cities showing 65% growth in digital payment adoption",
                        "Credit card usage decreased by 18% as UPI adoption increased"
                    ]
                else:
                    insights = [
                        f"Average transaction value increased to {currency}78.50 compared to previous period",
                        f"Weekend spending is 35% higher ({currency}125 vs {currency}92 average transaction)",
                        "Mobile transactions account for 65% of all purchases",
                        f"Subscription-based purchases have grown by 28% to {currency}42.30 per month"
                    ]
                charts = {
                    "spending_by_category": {
                        "categories": ["E-commerce", "Food Delivery", "Travel", "Entertainment", "Utilities", "Education"],
                        "values": [35, 25, 15, 12, 8, 5]
                    },
                    "spending_trend": {
                        "months": ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
                        "values": [1200, 1350, 1100, 1450, 1300, 1500]
                    }
                }
            elif analysis_type == "Demographic Analysis":
                if is_india_region:
                    insights = [
                        "Highest customer growth in 25-34 age bracket (28% increase in tier 2 cities)",
                        "Female customers increased by 32% in digital payment adoption",
                        "Tier 1 cities account for 42% of total customer base, with tier 2 growing rapidly at 36%",
                        "Customers with UPI-linked accounts show 45% higher engagement",
                        "Rural customer acquisition increased by 58% through assisted digital channels"
                    ]
                else:
                    # Non-Indian regions
                    insights = [
                        "Highest customer growth in 25-34 age bracket (22% increase)",
                        "Female customers increased by 18% compared to previous period",
                        "Urban customers account for 65% of total customer base",
                        "Customers with graduate degrees show 15% higher engagement"
                    ]
                    charts = {
                        "age_distribution": {
                            "groups": ["18-24", "25-34", "35-44", "45-54", "55+"],
                            "values": [15, 35, 25, 15, 10]
                        },
                        "location_distribution": {
                            "regions": ["Urban", "Suburban", "Rural"],
                            "values": [65, 25, 10]
                        }
                    }
        elif analysis_type == "Churn Prediction":
            if "India" in region:
                insights = [
                    "Predicted churn rate for Indian customers next quarter: 5.7%",
                    "Customers using only basic services are 2.8x more likely to churn",
                    "Digital payment adoption correlates with 45% lower churn in India",
                    "Tier 2/3 city customers show 30% higher churn risk",
                    "First 45 days of engagement critical for Indian customer retention",
                    "Mobile-only customers have 25% lower churn than web-only users in India"
                ]
            else:
                insights = [
                    "Predicted churn rate for next quarter: 4.2%",
                    "Customers with support tickets are 3x more likely to churn",
                    "Price sensitivity highest among customers < 6 months old",
                    "Engagement in first 30 days correlates with 65% lower churn"
                ]
            if "India" in region:
                charts = {
                    "churn_factors": {
                        "factors": ["Service Quality", "Digital Experience", "Competitor", "Price", "Product Range", "Other"],
                        "values": [45, 20, 15, 10, 7, 3]
                    },
                    "churn_prediction": {
                        "segments": ["Low Risk", "Medium Risk", "High Risk"],
                        "values": [70, 20, 10]
                    }
                }
            else:
                charts = {
                    "churn_factors": {
                        "factors": ["Price", "Support", "Competitor", "Usage", "Other"],
                        "values": [40, 25, 20, 10, 5]
                    },
                    "churn_prediction": {
                        "segments": ["Low Risk", "Medium Risk", "High Risk"],
                        "values": [75, 15, 10]
                    }
                }
        elif analysis_type == "Lifetime Value":
            if "India" in region:
                insights = [
                    f"Average customer LTV in India: {currency}95,000",
                    "Top 10% of Indian customers generate 52% of revenue",
                    f"Customers acquired through digital channels have 30% higher LTV ({currency}123,500 vs {currency}95,000)",
                    "UPI payment users have 2.8x higher engagement rate",
                    f"Multi-product customers have 3.5x higher LTV in Indian market ({currency}332,500)"
                ]
            else:
                insights = [
                    f"Average customer LTV: {currency}1,250",
                    "Top 10% of customers generate 45% of revenue",
                    f"Customers acquired through referrals have 25% higher LTV ({currency}1,562)",
                    f"Multi-product customers have 3.2x higher LTV ({currency}4,000)"
                ]
            charts = {
                "ltv_by_channel": {
                    "channels": ["Organic", "Paid", "Referral", "Partner", "Social"],
                    "values": [950, 850, 1200, 1100, 900]
                },
                "ltv_growth": {
                    "years": ["Year 1", "Year 2", "Year 3", "Year 4", "Year 5"],
                    "values": [300, 550, 750, 950, 1250]
                }
            }
        elif analysis_type == "Product Affinity":
            insights = [
                "Customers who purchase Product A are 75% likely to purchase Product B",
                "Bundle offers increase average order value by 28%",
                "Seasonal product affinity patterns identified for Q4",
                "Complementary product recommendations drive 15% of sales"
            ]
            charts = {
                "product_combinations": {
                    "pairs": ["A+B", "B+C", "A+D", "C+E", "B+E"],
                    "values": [45, 30, 25, 20, 15]
                },
                "recommendation_impact": {
                    "metrics": ["Conversion", "AOV", "Repeat Purchase", "Engagement"],
                    "values": [25, 28, 15, 35]
                }
            }
        
        # Handle custom query if provided
        if query:
            # Add query-specific insights at the beginning of the list
            insights.insert(0, f"Custom query results for: '{query}'")
            
            # Add more specific insights based on the query and region
            if "churn" in query.lower():
                if is_india_region:
                    insights.append("Customer churn in India is primarily driven by pricing sensitivity (42%) and competitor offers (38%)")
                    insights.append("Tier 2 cities show 28% higher churn rates compared to metro areas")
                    insights.append("Customers without UPI adoption are 3.5x more likely to churn")
                else:
                    insights.append("Customer churn is primarily driven by service quality (35%) and pricing (32%)")
                    insights.append("First-year customers have 45% higher churn risk")
            elif "spending" in query.lower() or "transactions" in query.lower():
                if is_india_region:
                    insights.append("UPI transactions account for 68% of digital payments in India regions")
                    insights.append("Festival season spending increases by 85% compared to regular months")
                    insights.append("Mobile payments growing at 42% YoY in tier 2/3 cities")
                else:
                    insights.append("Credit card transactions dominate spending patterns (72%)")
                    insights.append("Contactless payments increased by 58% in the last quarter")
            elif "demographic" in query.lower() or "segment" in query.lower():
                if is_india_region:
                    insights.append("25-34 age group represents the fastest growing segment in Indian markets (32% YoY)")
                    insights.append("Female customers in urban India increased financial product adoption by 48%")
                else:
                    insights.append("Millennial customers (25-40) represent 45% of the total customer base")
                    insights.append("Urban customers spend 35% more than rural customers on average")
            
            # Add a general conclusion
            insights.append("Natural language query processing identified these key trends related to your question")
        
        # Create result - ensure all values are JSON serializable
        # Convert any non-serializable objects to strings
        def ensure_serializable(obj):
            if isinstance(obj, (str, int, float, bool, type(None))):
                return obj
            elif isinstance(obj, (list, tuple)):
                return [ensure_serializable(item) for item in obj]
            elif isinstance(obj, dict):
                return {str(k): ensure_serializable(v) for k, v in obj.items()}
            else:
                return str(obj)
        
        # Create the result dictionary with serializable values
        result = {
            "customer_segment": str(customer_segment),
            "time_period": str(time_period),
            "analysis_type": str(analysis_type),
            "region": str(region),
            "query": str(query) if query else "",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "insights": ensure_serializable(insights),
            "charts": ensure_serializable(charts),
            "currency": currency,
            "currency_name": currency_name
        }
        
        # Add to history
        if "insights_history" not in demo_data:
            demo_data["insights_history"] = []
        demo_data["insights_history"].append(result)
        
        # Add log
        add_log(f"Customer insights generated for {customer_segment} in {region} with analysis type {analysis_type}")
    
        return render_template('insights.html',
                           customer_segment=customer_segment,
                           time_period=time_period,
                           analysis_type=analysis_type,
                           region=region,
                           query=query,
                           segments=segments,
                           time_periods=time_periods,
                           analysis_types=analysis_types,
                           regions=regions,
                           result=result,
                           history=demo_data.get("insights_history", [])[-10:] if "insights_history" in demo_data else [])
    except Exception as e:
        # Log the error
        add_log(f"ERROR in customer_insights: {str(e)}", level="ERROR")
        
        # Return a template with error message but with all options available
        segments = ["All Customers", "High Value", "New Customers", "At Risk", "Dormant Accounts", "Premium Tier", "Tier 1 Cities", "Tier 2 Cities", "Rural Customers"]
        time_periods = ["Last 7 Days", "Last 30 Days", "Last 90 Days", "Last 12 Months", "Year to Date", "Festival Season", "Monsoon Season"]
        analysis_types = ["Spending Patterns", "Demographic Analysis", "Churn Prediction", "Lifetime Value", "Product Affinity", "Regional Preferences", "Digital Adoption"]
        regions = ["All Regions", "India (North)", "India (South)", "India (East)", "India (West)", "India (Central)", "United States", "European Union", "United Kingdom", "Asia Pacific"]
        
        return render_template('insights.html',
                           customer_segment="All Customers",
                           time_period="Last 30 Days",
                           analysis_type="Spending Patterns",
                           region="India (North)",
                           query="",
                           segments=segments,
                           time_periods=time_periods,
                           analysis_types=analysis_types,
                           regions=regions,
                           result=None,
                           error_message=f"An error occurred: {str(e)}",
                           history=[])

# Generate sample data
def generate_sample_data():
    """Generate sample data for the demo."""
    # Generate sample fraud detection data
    for i in range(10):
        transaction_id = f"TXN-{uuid.uuid4().hex[:8].upper()}"
        customer_id = f"CUST-{random.randint(10000, 99999)}"
        amount = random.uniform(100, 5000)
        timestamp = (datetime.now() - timedelta(days=random.randint(0, 30))).strftime("%Y-%m-%d %H:%M:%S")
        location = random.choice(["India (North)", "India (South)", "India (East)", "India (West)", "India (Central)", "United States", "United Kingdom", "Canada", "Australia", "Germany", "France", "Japan"])
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
        demo_data["fraud_history"].append(result)
    
    # Generate sample KYC verification data
    for i in range(10):
        customer_id = f"CUST-{random.randint(10000, 99999)}"
        full_name = f"Customer {i+1}"
        dob = (datetime.now() - timedelta(days=365*random.randint(20, 60))).strftime("%Y-%m-%d")
        email = f"customer{i+1}@example.com"
        phone = f"+1-555-{random.randint(100, 999)}-{random.randint(1000, 9999)}"
        country = random.choice(["India (North)", "India (South)", "India (East)", "India (West)", "India (Central)", "United States", "United Kingdom", "Canada", "Australia", "Germany", "France", "Japan"])
        # Choose ID type based on country
        if "India" in country:
            id_type = random.choice(["Aadhaar Card", "PAN Card", "Voter ID", "Passport", "Driver's License"])
        else:
            id_type = random.choice(["Passport", "Driver's License", "National ID", "Social Security Number", "Other"])
        # Generate appropriate ID number format based on ID type
        if id_type == "Aadhaar Card":
            # Aadhaar is a 12-digit number (verified from UIDAI official site)
            # Format: XXXX XXXX XXXX (spaces for readability)
            id_number = f"{random.randint(1000, 9999)} {random.randint(1000, 9999)} {random.randint(1000, 9999)}"
        elif id_type == "PAN Card":
            # PAN is a 10-character alphanumeric (verified from Income Tax Department)
            # Format: AAAPL1234C
            # First 3 chars are letters, 4th is P for personal, 5th is first letter of last name, 
            # 6-9 are digits, 10th is a check letter
            id_number = f"{random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')}{random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')}{random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')}P{random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')}{random.randint(1000, 9999)}{random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')}"
        elif id_type == "Voter ID":
            # Voter ID (EPIC) format from Election Commission of India
            # Format: 3 letters (state/UT code) followed by 7 digits
            state_codes = ["DL", "MH", "UP", "TN", "KA", "GJ", "WB", "RJ", "AP"]
            id_number = f"{random.choice(state_codes)}{random.randint(1000000, 9999999)}"
        else:
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
        demo_data["kyc_history"].append(result)

# Run the application
if __name__ == "__main__":
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    
    # Add log
    add_log("Flask demo application started")
    
    # Run Flask app
    app.run(debug=True, port=5000)
