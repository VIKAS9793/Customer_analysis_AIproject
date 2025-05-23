import pytest
import json
import os
from pathlib import Path
from datetime import datetime


class TestRunner:
    """Test runner for systematically running and comparing fraud detection models."""
    
    def __init__(self, output_dir: str = "test_results"):
        """Initialize test runner.
        
        Args:
            output_dir: Directory to store test results
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
    def run_all_tests(self) -> dict:
        """Run all test cases and collect results.
        
        Returns:
            Dictionary containing test results
        """
        # Run pytest and capture output
        pytest.main(["-v", "--junitxml=test_results.xml"])
        
        # Load results from XML
        results = self._load_test_results()
        return results
    
    def compare_models(self, model1_results: dict, model2_results: dict) -> dict:
        """Compare two models based on test results.
        
        Args:
            model1_results: Results from first model
            model2_results: Results from second model
            
        Returns:
            Dictionary containing comparison metrics
        """
        comparison = {
            "metrics_comparison": {},
            "performance_comparison": {}
        }
        
        # Compare metrics
        for metric in model1_results["metrics"]:
            if metric in model2_results["metrics"]:
                m1 = model1_results["metrics"][metric]
                m2 = model2_results["metrics"][metric]
                comparison["metrics_comparison"][metric] = {
                    "model1": m1,
                    "model2": m2,
                    "difference": m1 - m2
                }
        
        # Compare performance
        comparison["performance_comparison"] = {
            "test_time": {
                "model1": model1_results.get("test_time", 0),
                "model2": model2_results.get("test_time", 0)
            }
        }
        
        return comparison
    
    def _load_test_results(self) -> dict:
        """Load test results from XML file.
        
        Returns:
            Dictionary containing test results
        """
        results_file = self.output_dir / "test_results.xml"
        if not results_file.exists():
            return {}
            
        # Parse XML and convert to dict
        # This is a simplified version - in production you'd use an XML parser
        with open(results_file, "r") as f:
            content = f.read()
            # Convert XML to dict using a proper parser
            return json.loads(content)
    
    def generate_report(self, results: dict, comparison: dict) -> None:
        """Generate a comprehensive test report.
        
        Args:
            results: Test results
            comparison: Model comparison results
        """
        report = {
            "timestamp": datetime.now().isoformat(),
            "test_results": results,
            "model_comparison": comparison,
            "summary": self._generate_summary(results, comparison)
        }
        
        # Save report
        report_path = self.output_dir / f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)
    
    def _generate_summary(self, results: dict, comparison: dict) -> dict:
        """Generate a summary of test results.
        
        Args:
            results: Test results
            comparison: Model comparison results
            
        Returns:
            Summary dictionary
        """
        summary = {
            "total_tests": len(results.get("tests", [])),
            "passed_tests": len([t for t in results.get("tests", []) if t.get("status") == "passed"]),
            "failed_tests": len([t for t in results.get("tests", []) if t.get("status") == "failed"]),
            "key_metrics": {},
            "recommendations": []
        }
        
        # Add key metrics
        for metric in ["precision", "recall", "f1_score", "auc_roc", "auc_pr"]:
            if metric in results.get("metrics", {}):
                summary["key_metrics"][metric] = results["metrics"][metric]
        
        # Add recommendations based on results
        if summary["failed_tests"] > 0:
            summary["recommendations"].append("Investigate failed test cases")
        
        return summary

if __name__ == "__main__":
    runner = TestRunner()
    results = runner.run_all_tests()
    print("Test results:", json.dumps(results, indent=2))
