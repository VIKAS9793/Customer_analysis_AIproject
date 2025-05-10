"""
Rate Limiter System

This module implements enterprise-grade rate limiting for security events.
"""

from typing import Dict, Any, Optional
import logging
from datetime import datetime, timedelta
from collections import defaultdict
import threading

logger = logging.getLogger(__name__)

class RateLimiterError(Exception):
    """Raised when rate limiting operations fail"""
    pass

class RateLimiter:
    """
    Enterprise-grade rate limiter.
    
    Implements OWASP rate limiting recommendations.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize rate limiter.
        
        Args:
            config: Configuration containing:
                - rate_limits: Dictionary of rate limits per action
                - cleanup_interval: Interval for cleaning up old entries
                - max_buckets: Maximum number of rate limit buckets
        """
        self.config = config
        self.rate_limits = config.get("rate_limits", {})
        self.cleanup_interval = timedelta(seconds=config.get("cleanup_interval_seconds", 3600))
        self.max_buckets = config.get("max_buckets", 10000)
        
        # Rate limit tracking
        self.buckets: Dict[str, Dict[str, Any]] = defaultdict(lambda: {
            "count": 0,
            "last_reset": datetime.utcnow(),
            "lock": threading.Lock()
        })
        
        # Cleanup thread
        self.cleanup_thread = threading.Thread(target=self._cleanup_buckets, daemon=True)
        self.cleanup_thread.start()
        
    def initialize_limits(self, limits: Dict[str, Any]) -> None:
        """
        Initialize rate limits from configuration.
        
        Args:
            limits: Dictionary of rate limits in format:
                {
                    "action_name": {
                        "window_seconds": int,
                        "max_requests": int
                    }
                }
        """
        self.rate_limits.update(limits)
        
    def check_limit(self, action: str, identifier: str) -> bool:
        """
        Check if an action is allowed based on rate limits.
        
        Args:
            action: The action being performed
            identifier: Unique identifier for rate limiting (e.g., user_id, ip_address)
            
        Returns:
            True if action is allowed, False otherwise
            
        Raises:
            RateLimiterError: If rate limit configuration is invalid
        """
        try:
            # Get or create bucket
            bucket_key = f"{action}:{identifier}"
            bucket = self.buckets[bucket_key]
            
            with bucket["lock"]:
                # Get rate limit configuration
                limit_config = self.rate_limits.get(action)
                if not limit_config:
                    return True  # No limit configured
                    
                window = timedelta(seconds=limit_config["window_seconds"])
                max_requests = limit_config["max_requests"]
                
                # Check if window has expired
                current_time = datetime.utcnow()
                if current_time - bucket["last_reset"] > window:
                    bucket["count"] = 0
                    bucket["last_reset"] = current_time
                
                # Check if limit is exceeded
                if bucket["count"] >= max_requests:
                    return False
                
                # Increment counter
                bucket["count"] += 1
                return True
                
        except Exception as e:
            logger.error(f"Rate limit check failed: {str(e)}")
            raise RateLimiterError(f"Failed to check rate limit: {str(e)}")
    
    def _cleanup_buckets(self) -> None:
        """Periodically clean up old rate limit buckets."""
        while True:
            try:
                current_time = datetime.utcnow()
                
                # Clean up expired buckets
                for bucket_key, bucket in list(self.buckets.items()):
                    with bucket["lock"]:
                        if current_time - bucket["last_reset"] > self.cleanup_interval:
                            del self.buckets[bucket_key]
                
                # Clean up if we exceed max buckets
                if len(self.buckets) > self.max_buckets:
                    oldest_buckets = sorted(
                        self.buckets.items(),
                        key=lambda x: x[1]["last_reset"]
                    )
                    for bucket_key, _ in oldest_buckets[:len(self.buckets) - self.max_buckets]:
                        del self.buckets[bucket_key]
                
                # Sleep until next cleanup
                time.sleep(self.cleanup_interval.total_seconds())
                
            except Exception as e:
                logger.error(f"Rate limiter cleanup failed: {str(e)}")
                time.sleep(60)  # Wait before retrying
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current rate limiting metrics."""
        metrics = {
            "total_buckets": len(self.buckets),
            "active_buckets": sum(
                1 for bucket in self.buckets.values() 
                if datetime.utcnow() - bucket["last_reset"] < self.cleanup_interval
            ),
            "rate_limits": self.rate_limits,
            "cleanup_interval": self.cleanup_interval.total_seconds(),
            "max_buckets": self.max_buckets
        }
        return metrics
