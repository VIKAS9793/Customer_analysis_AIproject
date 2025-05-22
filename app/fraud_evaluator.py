"""
Fraud Detection Evaluation Module - Generates performance metrics for fraud detection outputs
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List


class FraudEvaluator:
    """Evaluates fraud detection model performance using standard metrics."""

    def __init__(self, output_dir: str = "logs"):
        """Initialize the evaluator.

        Args:
            output_dir: Directory to store evaluation reports
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

    def evaluate_predictions(
        self, synthetic_data: List[Dict[str, Any]], model_output: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Evaluate model predictions against ground truth.

        Args:
            synthetic_data: List of ground truth data points with actual fraud labels
            model_output: List of model predictions with confidence scores

        Returns:
            Dict containing evaluation metrics
        """
        if len(synthetic_data) != len(model_output):
            raise ValueError("Number of predictions must match number of ground truth samples")

        # Calculate confusion matrix
        tp = fp = tn = fn = 0

        for truth, pred in zip(synthetic_data, model_output):
            actual_fraud = truth.get("is_fraud", False)
            predicted_fraud = pred.get("decision") == "fraud"

            if actual_fraud and predicted_fraud:
                tp += 1
            elif actual_fraud and not predicted_fraud:
                fn += 1
            elif not actual_fraud and predicted_fraud:
                fp += 1
            else:
                tn += 1

        # Calculate metrics
        total = tp + fp + tn + fn
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1_score = (
            2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        )

        # Create evaluation report
        report = {
            "metrics": {
                "true_positives": tp,
                "false_positives": fp,
                "true_negatives": tn,
                "false_negatives": fn,
                "precision": precision,
                "recall": recall,
                "f1_score": f1_score,
                "accuracy": (tp + tn) / total if total > 0 else 0,
            },
            "metadata": {
                "total_samples": total,
                "timestamp": datetime.utcnow().isoformat(),
                "evaluation_type": "fraud_detection",
            },
        }

        # Save report
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        report_path = self.output_dir / f"eval_report_{timestamp}.json"

        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)

        return report

    def get_latest_report(self) -> Dict[str, Any]:
        """Retrieve the most recent evaluation report.

        Returns:
            Dict containing the latest evaluation metrics
        """
        reports = list(self.output_dir.glob("eval_report_*.json"))
        if not reports:
            return {}

        latest_report = max(reports, key=lambda x: x.stat().st_mtime)
        with open(latest_report) as f:
            return json.load(f)
