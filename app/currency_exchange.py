"""
Currency exchange rate fetcher using trusted financial data sources.
Uses exchangerate-api.com as the primary source for real-time exchange rates.
"""
import aiohttp
import asyncio
from datetime import datetime
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)

class CurrencyExchangeService:
    def __init__(self, api_key: str):
        """
        Initialize the currency exchange service.
        
        Args:
            api_key (str): Your ExchangeRate-API key
        """
        self.api_key = api_key
        self.base_url = "https://v6.exchangerate-api.com/v6"
        self.session: Optional[aiohttp.ClientSession] = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
            
    async def get_exchange_rates(self, base_currency: str = "USD") -> Dict:
        """
        Fetch real-time exchange rates for the specified base currency.
        
        Args:
            base_currency (str): Base currency code (default: USD)
            
        Returns:
            dict: Exchange rate data in the specified format
        """
        if not self.session:
            raise RuntimeError("Session not initialized. Use async with context manager.")
            
        try:
            url = f"{self.base_url}/{self.api_key}/latest/{base_currency}"
            async with self.session.get(url) as response:
                if response.status != 200:
                    logger.error(f"Failed to fetch exchange rates: {response.status}")
                    raise ValueError(f"API request failed with status {response.status}")
                    
                data = await response.json()
                
                # Format the response according to our specification
                result = {
                    "base_currency": base_currency,
                    "conversion_rates": {
                        "INR": data["conversion_rates"].get("INR"),
                        "EUR": data["conversion_rates"].get("EUR"),
                        "GBP": data["conversion_rates"].get("GBP"),
                        "SGD": data["conversion_rates"].get("SGD")
                    },
                    "source": url,
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                    "trust_score": 0.95  # ExchangeRate-API is a reliable source
                }
                
                # Remove any None values from conversion_rates
                result["conversion_rates"] = {
                    k: v for k, v in result["conversion_rates"].items() if v is not None
                }
                
                return result
                
        except Exception as e:
            logger.error(f"Error fetching exchange rates: {str(e)}")
            raise

async def get_latest_rates(api_key: str, base_currency: str = "USD") -> Dict:
    """
    Convenience function to get latest exchange rates.
    
    Args:
        api_key (str): Your ExchangeRate-API key
        base_currency (str): Base currency code (default: USD)
        
    Returns:
        dict: Exchange rate data
    """
    async with CurrencyExchangeService(api_key) as service:
        return await service.get_exchange_rates(base_currency)
