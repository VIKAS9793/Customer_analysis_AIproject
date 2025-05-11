"""
Auto Scaler Implementation

This module implements auto-scaling functionality for the FinConnectAI system.
"""

from typing import Dict, Any, List
import logging
import asyncio
from datetime import datetime, timedelta
import statistics

class AutoScaler:
    def __init__(self, config: Dict[str, Any]):
        """Initialize auto scaler with configuration"""
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Scaling thresholds
        self.cpu_threshold = config.get("cpu_threshold", 0.7)
        self.memory_threshold = config.get("memory_threshold", 0.8)
        self.request_threshold = config.get("request_threshold", 1000)
        
        # Scaling limits
        self.min_instances = config.get("min_instances", 2)
        self.max_instances = config.get("max_instances", 10)
        self.cooldown_period = config.get("cooldown_period", 300)  # 5 minutes
        
        # Current state
        self.current_instances = self.min_instances
        self.last_scale_time = datetime.now() - timedelta(seconds=self.cooldown_period)
        self.metrics_history = []
        
    async def monitor_and_scale(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Monitor system metrics and trigger scaling if needed"""
        try:
            # Store metrics history
            self.metrics_history.append(metrics)
            if len(self.metrics_history) > 10:
                self.metrics_history.pop(0)
            
            # Check if scaling is needed
            scale_decision = self._evaluate_scaling_need()
            
            if scale_decision != 0 and self._can_scale():
                await self._perform_scaling(scale_decision)
            
            return {
                "current_instances": self.current_instances,
                "last_scale_time": self.last_scale_time.isoformat(),
                "metrics_evaluation": scale_decision
            }
        except Exception as e:
            self.logger.error(f"Auto-scaling monitoring failed: {str(e)}")
            raise
            
    def _evaluate_scaling_need(self) -> int:
        """Evaluate if scaling is needed based on metrics"""
        if not self.metrics_history:
            return 0
            
        # Calculate average metrics
        avg_cpu = statistics.mean(m["cpu_usage"] for m in self.metrics_history)
        avg_memory = statistics.mean(m["memory_usage"] for m in self.metrics_history)
        avg_requests = statistics.mean(m["requests_per_second"] for m in self.metrics_history)
        
        # Scale up conditions
        if (avg_cpu > self.cpu_threshold or 
            avg_memory > self.memory_threshold or 
            avg_requests > self.request_threshold):
            return 1
            
        # Scale down conditions
        if (avg_cpu < self.cpu_threshold/2 and 
            avg_memory < self.memory_threshold/2 and 
            avg_requests < self.request_threshold/2):
            return -1
            
        return 0
            
    def _can_scale(self) -> bool:
        """Check if scaling is allowed"""
        # Check cooldown period
        if (datetime.now() - self.last_scale_time).total_seconds() < self.cooldown_period:
            return False
            
        return True
            
    async def _perform_scaling(self, scale_direction: int) -> None:
        """Perform the actual scaling operation"""
        try:
            new_instances = self.current_instances + scale_direction
            
            # Ensure within limits
            new_instances = max(self.min_instances, min(new_instances, self.max_instances))
            
            if new_instances != self.current_instances:
                # Implement actual scaling logic here
                self.current_instances = new_instances
                self.last_scale_time = datetime.now()
                
                self.logger.info(f"Scaled {'up' if scale_direction > 0 else 'down'} to {new_instances} instances")
        except Exception as e:
            self.logger.error(f"Scaling operation failed: {str(e)}")
            raise
            
    async def get_scaling_status(self) -> Dict[str, Any]:
        """Get current scaling status"""
        return {
            "current_instances": self.current_instances,
            "min_instances": self.min_instances,
            "max_instances": self.max_instances,
            "last_scale_time": self.last_scale_time.isoformat(),
            "cooldown_remaining": max(0, self.cooldown_period - 
                (datetime.now() - self.last_scale_time).total_seconds())
        }
