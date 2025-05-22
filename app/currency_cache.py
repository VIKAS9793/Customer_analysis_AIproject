"""Currency exchange rate cache service with automatic updates."""
import asyncio
import json
from datetime import datetime, timedelta
import logging
from pathlib import Path
from typing import Dict, Optional
import aiofiles
from app.currency_exchange import CurrencyExchangeService

logger = logging.getLogger(__name__)

class CurrencyRateCache:
    def __init__(self, api_key: str, update_interval: int = 3600):
        """
        Initialize the currency rate cache service.
        
        Args:
            api_key (str): ExchangeRate-API key
            update_interval (int): Update interval in seconds (default: 1 hour)
        """
        self.api_key = api_key
        self.update_interval = update_interval
        self.cache_file = Path("cache/exchange_rates.json")
        self.cache_file.parent.mkdir(exist_ok=True)
        self._cache: Dict = {}
        self._last_update: Optional[datetime] = None
        self._update_task: Optional[asyncio.Task] = None
        self._running = False

    async def start(self):
        """Start the automatic update service."""
        if self._running:
            return
            
        self._running = True
        # Load cached data if available
        await self._load_cache()
        # Start the update loop
        self._update_task = asyncio.create_task(self._update_loop())
        logger.info("Currency rate cache service started")

    async def stop(self):
        """Stop the automatic update service."""
        if not self._running:
            return
            
        self._running = False
        if self._update_task:
            self._update_task.cancel()
            try:
                await self._update_task
            except asyncio.CancelledError:
                pass
        logger.info("Currency rate cache service stopped")

    async def get_rates(self, base_currency: str = "USD") -> Dict:
        """
        Get exchange rates from cache, updating if necessary.
        
        Args:
            base_currency (str): Base currency code
            
        Returns:
            dict: Cached exchange rate data
        """
        if not self._cache or self._needs_update():
            await self._update_rates()
        return self._cache.get(base_currency, {})

    async def _load_cache(self):
        """Load cached rates from file if available."""
        try:
            if self.cache_file.exists():
                async with aiofiles.open(self.cache_file, mode='r') as f:
                    content = await f.read()
                    data = json.loads(content)
                    self._cache = data
                    logger.info("Loaded exchange rates from cache file")
        except Exception as e:
            logger.error(f"Error loading cache file: {str(e)}")

    async def _save_cache(self):
        """Save current rates to cache file."""
        try:
            async with aiofiles.open(self.cache_file, mode='w') as f:
                await f.write(json.dumps(self._cache, indent=2))
            logger.info("Saved exchange rates to cache file")
        except Exception as e:
            logger.error(f"Error saving cache file: {str(e)}")

    def _needs_update(self) -> bool:
        """Check if cache needs to be updated."""
        if not self._last_update:
            return True
        return (datetime.utcnow() - self._last_update).total_seconds() >= self.update_interval

    async def _update_rates(self):
        """Update rates from the API."""
        try:
            async with CurrencyExchangeService(self.api_key) as service:
                # Fetch rates for main currencies
                for base in ["USD", "EUR", "GBP"]:
                    self._cache[base] = await service.get_exchange_rates(base)
                self._last_update = datetime.utcnow()
                await self._save_cache()
                logger.info("Updated exchange rates from API")
        except Exception as e:
            logger.error(f"Error updating exchange rates: {str(e)}")

    async def _update_loop(self):
        """Background loop for automatic updates."""
        while self._running:
            try:
                if self._needs_update():
                    await self._update_rates()
                await asyncio.sleep(60)  # Check every minute
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in update loop: {str(e)}")
                await asyncio.sleep(60)  # Wait before retrying
