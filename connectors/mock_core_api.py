"""
Mock Core Banking API Connector
Simple connector that simulates basic banking operations with mock responses
"""

import json
from datetime import datetime
from typing import Dict, Any, Optional
import random
import time
from pathlib import Path

class CoreBankingConnector:
    """Simple mock connector for core banking operations."""
    
    def __init__(self, log_dir: str = "logs"):
        """Initialize the connector with logging directory."""
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # Simple mock account data
        self._mock_accounts = {
            "1001": {"balance": 5000.00, "status": "active"},
            "1002": {"balance": 2500.00, "status": "active"},
            "1003": {"balance": 0.00, "status": "suspended"}
        }
    
    def get_account_info(self, account_id: str) -> Dict[str, Any]:
        """Mock getting account information."""
        # Simulate random timeout
        if random.random() < 0.1:
            time.sleep(2)
            self._log_response("timeout", "get_account_info", {"error": "Request timed out"})
            raise TimeoutError("Request timed out")
            
        # Simulate successful or error response
        if account_id in self._mock_accounts:
            response = {
                "account_id": account_id,
                "timestamp": datetime.utcnow().isoformat(),
                **self._mock_accounts[account_id]
            }
            self._log_response("success", "get_account_info", response)
            return response
        else:
            error = {"error": "Account not found", "account_id": account_id}
            self._log_response("error", "get_account_info", error)
            raise ValueError("Account not found")
    
    def check_transaction_history(self, account_id: str, days: int = 30) -> Dict[str, Any]:
        """Mock checking recent transaction history."""
        if account_id not in self._mock_accounts:
            error = {"error": "Account not found", "account_id": account_id}
            self._log_response("error", "check_transaction_history", error)
            raise ValueError("Account not found")
            
        # Generate mock transaction history
        mock_history = {
            "account_id": account_id,
            "period_days": days,
            "transaction_count": random.randint(5, 15),
            "total_debit": round(random.uniform(100, 1000), 2),
            "total_credit": round(random.uniform(100, 1000), 2),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        self._log_response("success", "check_transaction_history", mock_history)
        return mock_history
    
    def _log_response(self, status: str, operation: str, data: Dict[str, Any]) -> None:
        """Log API response to JSON file."""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "operation": operation,
            "status": status,
            "data": data
        }
        
        log_file = self.log_dir / "integration_test_log.json"
        
        # Read existing logs
        if log_file.exists():
            with open(log_file) as f:
                try:
                    logs = json.load(f)
                except json.JSONDecodeError:
                    logs = []
        else:
            logs = []
        
        # Append new log
        logs.append(log_entry)
        
        # Write updated logs
        with open(log_file, "w") as f:
            json.dump(logs, f, indent=2)
