"""
Model Validation Implementation

This module implements model validation for the FinConnectAI system.
"""

from typing import Dict, Any, List, Optional
import logging
from datetime import datetime
import json
from pathlib import Path
import numpy as np
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.model_selection import cross_val_score

class ModelValidator:
    def __init__(self, config: Dict[str, Any]):
        """Initialize model validator with configuration"""
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Validation configuration
        self.validation_config = {
            "metrics": config.get("metrics", ["accuracy", "precision", "recall", "f1"]),
            "threshold": config.get("validation_threshold", 0.8),
            "cross_validation": config.get("cross_validation", True),
            "cv_folds": config.get("cv_folds", 5)
        }
        
        # Initialize validation history
        self.validation_history = []
        
    def validate_model(self, model_data: Dict[str, Any], validation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate model performance"""
        try:
            # Perform validation
            validation_results = self._perform_validation(model_data, validation_data)
            
            # Check validation criteria
            validation_passed = self._check_validation_criteria(validation_results)
            
            # Update validation history
            self._update_validation_history(validation_results)
            
            return {
                "validation_passed": validation_passed,
                "results": validation_results,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Model validation failed: {str(e)}")
            raise
            
    def _perform_validation(self, model_data: Dict[str, Any], validation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform model validation"""
        results = {}
        
        # Get predictions
        y_true = validation_data.get("labels", [])
        y_pred = self._get_predictions(model_data, validation_data.get("features", []))
        
        # Calculate metrics
        results["metrics"] = self._calculate_metrics(y_true, y_pred)
        
        # Perform cross-validation if enabled
        if self.validation_config["cross_validation"]:
            results["cross_validation"] = self._perform_cross_validation(
                model_data,
                validation_data.get("features", []),
                y_true
            )
            
        return results
        
    def _get_predictions(self, model_data: Dict[str, Any], features: List[Any]) -> List[Any]:
        """Get model predictions"""
        model = model_data.get("model")
        if not model:
            raise ValueError("Model not provided in model_data")
            
        return model.predict(features)
        
    def _calculate_metrics(self, y_true: List[Any], y_pred: List[Any]) -> Dict[str, float]:
        """Calculate validation metrics"""
        metrics = {}
        
        for metric in self.validation_config["metrics"]:
            if metric == "accuracy":
                metrics[metric] = accuracy_score(y_true, y_pred)
            elif metric == "precision":
                metrics[metric] = precision_score(y_true, y_pred, average="weighted")
            elif metric == "recall":
                metrics[metric] = recall_score(y_true, y_pred, average="weighted")
            elif metric == "f1":
                metrics[metric] = f1_score(y_true, y_pred, average="weighted")
                
        return metrics
        
    def _perform_cross_validation(self, model_data: Dict[str, Any], X: List[Any], y: List[Any]) -> Dict[str, Any]:
        """Perform cross-validation"""
        model = model_data.get("model")
        if not model:
            raise ValueError("Model not provided in model_data")
            
        cv_scores = cross_val_score(
            model,
            X,
            y,
            cv=self.validation_config["cv_folds"]
        )
        
        return {
            "scores": cv_scores.tolist(),
            "mean": cv_scores.mean(),
            "std": cv_scores.std(),
            "folds": self.validation_config["cv_folds"]
        }
        
    def _check_validation_criteria(self, validation_results: Dict[str, Any]) -> bool:
        """Check if validation results meet criteria"""
        metrics = validation_results.get("metrics", {})
        threshold = self.validation_config["threshold"]
        
        # Check each metric against threshold
        for metric, value in metrics.items():
            if value < threshold:
                return False
                
        # Check cross-validation if enabled
        if self.validation_config["cross_validation"]:
            cv_results = validation_results.get("cross_validation", {})
            if cv_results.get("mean", 0) < threshold:
                return False
                
        return True
        
    def _update_validation_history(self, validation_results: Dict[str, Any]) -> None:
        """Update validation history"""
        self.validation_history.append({
            "timestamp": datetime.now().isoformat(),
            "results": validation_results
        })
        
        # Maintain history size
        max_history = self.config.get("max_history_size", 1000)
        if len(self.validation_history) > max_history:
            self.validation_history = self.validation_history[-max_history:]
            
    def get_validation_history(self) -> List[Dict[str, Any]]:
        """Get validation history"""
        return self.validation_history
        
    def get_validation_summary(self) -> Dict[str, Any]:
        """Get validation summary statistics"""
        if not self.validation_history:
            return {}
            
        total_validations = len(self.validation_history)
        passed_validations = sum(
            1 for result in self.validation_history
            if self._check_validation_criteria(result["results"])
        )
        
        return {
            "total_validations": total_validations,
            "passed_validations": passed_validations,
            "pass_rate": passed_validations / total_validations if total_validations > 0 else 0,
            "last_validation": self.validation_history[-1] if self.validation_history else None,
            "metrics_summary": self._calculate_metrics_summary()
        }
        
    def _calculate_metrics_summary(self) -> Dict[str, Any]:
        """Calculate summary statistics for validation metrics"""
        summary = {}
        
        for metric in self.validation_config["metrics"]:
            metric_values = [
                result["results"]["metrics"][metric]
                for result in self.validation_history
                if metric in result["results"].get("metrics", {})
            ]
            
            if metric_values:
                summary[metric] = {
                    "mean": np.mean(metric_values),
                    "std": np.std(metric_values),
                    "min": np.min(metric_values),
                    "max": np.max(metric_values)
                }
                
        return summary
        
    def export_validation_report(self, output_path: str) -> str:
        """Export validation report"""
        try:
            report = {
                "summary": self.get_validation_summary(),
                "history": self.get_validation_history(),
                "config": self.validation_config,
                "generated_at": datetime.now().isoformat()
            }
            
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, "w") as f:
                json.dump(report, f, indent=2)
                
            return str(output_path)
        except Exception as e:
            self.logger.error(f"Failed to export validation report: {str(e)}")
            raise
