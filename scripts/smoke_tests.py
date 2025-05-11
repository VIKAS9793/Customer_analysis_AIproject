"""
Smoke Tests for FinConnectAI System

This script runs basic smoke tests after deployment to verify system functionality.
"""

import os
import sys
import json
import logging
import requests
import time
from typing import Dict, Any, List
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SmokeTests:
    def __init__(self, config_path: str = "config/smoke_tests.json"):
        """Initialize smoke tests with configuration"""
        self.config = self._load_config(config_path)
        self.results = []
        
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load smoke test configuration"""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load config: {str(e)}")
            return {
                "api_endpoint": os.getenv("API_ENDPOINT", "http://localhost:8000"),
                "timeout": 30,
                "retries": 3,
                "tests": {
                    "health_check": True,
                    "model_inference": True,
                    "data_processing": True,
                    "monitoring": True
                }
            }
            
    def run_all_tests(self) -> bool:
        """Run all smoke tests"""
        try:
            logger.info("Starting smoke tests...")
            
            # Run enabled tests
            if self.config["tests"].get("health_check", True):
                self._test_health_check()
                
            if self.config["tests"].get("model_inference", True):
                self._test_model_inference()
                
            if self.config["tests"].get("data_processing", True):
                self._test_data_processing()
                
            if self.config["tests"].get("monitoring", True):
                self._test_monitoring()
                
            # Check results
            success = all(result["status"] == "passed" for result in self.results)
            self._log_results()
            
            return success
        except Exception as e:
            logger.error(f"Smoke tests failed: {str(e)}")
            return False
            
    def _test_health_check(self) -> None:
        """Test system health check endpoint"""
        endpoint = f"{self.config['api_endpoint']}/health"
        
        try:
            response = self._make_request("GET", endpoint)
            
            if response.status_code == 200 and response.json().get("status") == "healthy":
                self._add_result("health_check", "passed")
            else:
                self._add_result("health_check", "failed", "Unexpected health check response")
        except Exception as e:
            self._add_result("health_check", "failed", str(e))
            
    def _test_model_inference(self) -> None:
        """Test model inference functionality"""
        endpoint = f"{self.config['api_endpoint']}/predict"
        test_data = {
            "customer_id": "test_customer",
            "features": {
                "age": 30,
                "income": 50000,
                "purchase_history": [100, 200, 300]
            }
        }
        
        try:
            response = self._make_request("POST", endpoint, json=test_data)
            
            if response.status_code == 200 and "prediction" in response.json():
                self._add_result("model_inference", "passed")
            else:
                self._add_result("model_inference", "failed", "Invalid prediction response")
        except Exception as e:
            self._add_result("model_inference", "failed", str(e))
            
    def _test_data_processing(self) -> None:
        """Test data processing functionality"""
        endpoint = f"{self.config['api_endpoint']}/process"
        test_data = {
            "data_type": "customer",
            "records": [
                {"id": "1", "name": "Test User", "age": 30},
                {"id": "2", "name": "Test User 2", "age": 40}
            ]
        }
        
        try:
            response = self._make_request("POST", endpoint, json=test_data)
            
            if response.status_code == 200 and "processed_records" in response.json():
                self._add_result("data_processing", "passed")
            else:
                self._add_result("data_processing", "failed", "Invalid processing response")
        except Exception as e:
            self._add_result("data_processing", "failed", str(e))
            
    def _test_monitoring(self) -> None:
        """Test monitoring functionality"""
        endpoint = f"{self.config['api_endpoint']}/metrics"
        
        try:
            response = self._make_request("GET", endpoint)
            
            if response.status_code == 200 and "metrics" in response.json():
                self._add_result("monitoring", "passed")
            else:
                self._add_result("monitoring", "failed", "Invalid monitoring response")
        except Exception as e:
            self._add_result("monitoring", "failed", str(e))
            
    def _make_request(self, method: str, url: str, **kwargs) -> requests.Response:
        """Make HTTP request with retries"""
        retries = self.config.get("retries", 3)
        timeout = self.config.get("timeout", 30)
        
        for attempt in range(retries):
            try:
                response = requests.request(
                    method,
                    url,
                    timeout=timeout,
                    **kwargs
                )
                response.raise_for_status()
                return response
            except Exception as e:
                if attempt == retries - 1:
                    raise
                time.sleep(2 ** attempt)  # Exponential backoff
                
    def _add_result(self, test_name: str, status: str, message: str = "") -> None:
        """Add test result"""
        self.results.append({
            "test": test_name,
            "status": status,
            "message": message,
            "timestamp": time.time()
        })
        
    def _log_results(self) -> None:
        """Log test results"""
        logger.info("Smoke test results:")
        for result in self.results:
            status_msg = (
                f"✓ {result['test']} - PASSED"
                if result['status'] == 'passed'
                else f"✗ {result['test']} - FAILED: {result['message']}"
            )
            logger.info(status_msg)
            
    def export_results(self, output_path: str) -> None:
        """Export test results to file"""
        try:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, "w") as f:
                json.dump({
                    "results": self.results,
                    "summary": {
                        "total": len(self.results),
                        "passed": sum(1 for r in self.results if r["status"] == "passed"),
                        "failed": sum(1 for r in self.results if r["status"] == "failed")
                    }
                }, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to export results: {str(e)}")
            
def main():
    """Main entry point for smoke tests"""
    try:
        smoke_tests = SmokeTests()
        success = smoke_tests.run_all_tests()
        
        # Export results
        smoke_tests.export_results("logs/smoke_test_results.json")
        
        # Exit with appropriate status code
        sys.exit(0 if success else 1)
    except Exception as e:
        logger.error(f"Smoke tests failed: {str(e)}")
        sys.exit(1)
        
if __name__ == "__main__":
    main()
