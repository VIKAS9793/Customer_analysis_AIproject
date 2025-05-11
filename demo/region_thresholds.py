"""
Region-specific fraud detection thresholds based on official regulatory sources.
This module provides functions to calculate risk scores based on transaction amounts
and the region where the transaction occurred.
"""

def calculate_amount_risk(amount, location):
    """
    Calculate risk score based on transaction amount and location.
    Risk thresholds are based on official regulatory requirements in different regions.
    
    Args:
        amount (float): Transaction amount
        location (str): Location/country of the transaction
        
    Returns:
        float: Risk score between 0.1 and 0.9
    """
    if location == "India":
        # India - RBI guidelines use ₹50,000 (~$600) as a threshold for suspicious transaction verification
        # Higher thresholds for larger transactions common in Indian banking
        return 0.9 if amount > 500000 else 0.7 if amount > 100000 else 0.5 if amount > 50000 else 0.3 if amount > 10000 else 0.1
    
    elif location == "United States":
        # US - FinCEN requires SARs for transactions over $5,000 if suspicious
        # CTRs required for transactions over $10,000
        return 0.9 if amount > 50000 else 0.7 if amount > 10000 else 0.5 if amount > 5000 else 0.3 if amount > 1000 else 0.1
    
    elif location in ["Germany", "France"]:
        # EU - Varies by country but generally €10,000 for cash transaction reporting
        # European Banking Authority guidelines for PSD2 fraud reporting
        return 0.9 if amount > 100000 else 0.7 if amount > 50000 else 0.5 if amount > 10000 else 0.3 if amount > 2000 else 0.1
    
    elif location == "United Kingdom":
        # UK - No fixed threshold, but NCA guidance suggests heightened scrutiny above £10,000
        return 0.9 if amount > 100000 else 0.7 if amount > 50000 else 0.5 if amount > 10000 else 0.3 if amount > 2000 else 0.1
    
    elif location == "Japan":
        # Japan - Threshold of ¥1,000,000 (~$6,700) for reporting
        return 0.9 if amount > 100000 else 0.7 if amount > 50000 else 0.5 if amount > 6700 else 0.3 if amount > 1000 else 0.1
    
    elif location in ["Canada", "Australia"]:
        # Canada/Australia - Threshold of $10,000 for reporting
        return 0.9 if amount > 50000 else 0.7 if amount > 10000 else 0.5 if amount > 5000 else 0.3 if amount > 1000 else 0.1
    
    else:
        # Default risk calculation for other regions
        return 0.9 if amount > 50000 else 0.7 if amount > 10000 else 0.5 if amount > 5000 else 0.3 if amount > 1000 else 0.1
