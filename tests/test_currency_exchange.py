"""Tests for the currency exchange functionality."""
import pytest
import os
from dotenv import load_dotenv
from app.currency_exchange import get_latest_rates

# Load environment variables
load_dotenv()

@pytest.mark.asyncio
async def test_get_latest_rates():
    """Test fetching latest exchange rates."""
    api_key = os.getenv("EXCHANGE_RATE_API_KEY")
    if not api_key:
        pytest.skip("EXCHANGE_RATE_API_KEY not set in environment variables")
        
    rates = await get_latest_rates(api_key)
    
    # Verify the response structure
    assert isinstance(rates, dict)
    assert "base_currency" in rates
    assert "conversion_rates" in rates
    assert "timestamp" in rates
    assert "trust_score" in rates
    assert "source" in rates
    
    # Verify we have the required currency pairs
    conversion_rates = rates["conversion_rates"]
    required_currencies = {"INR", "EUR", "GBP", "SGD"}
    assert all(currency in conversion_rates for currency in required_currencies)
    
    # Verify the values are reasonable
    assert all(isinstance(rate, (int, float)) for rate in conversion_rates.values())
    assert all(rate > 0 for rate in conversion_rates.values())
    
    # Test with EUR as base currency
    eur_rates = await get_latest_rates(api_key, "EUR")
    assert eur_rates["base_currency"] == "EUR"
