"""
Fraud Detection Evaluation Module - Generates performance metrics for fraud detection outputs
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from statistics import mean, stdev
from math import sqrt


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
        fraud_amounts = []
        fraud_confidences = []
        legitimate_amounts = []
        legitimate_confidences = []
        total_fraud = 0
        total_legitimate = 0

        for truth, pred in zip(synthetic_data, model_output):
            actual_fraud = truth.get("is_fraud", False)
            predicted_fraud = pred.get("decision") == "fraud"
            confidence = pred.get("confidence", 0.5)
            amount = truth.get("amount", 0)

            if actual_fraud:
                fraud_amounts.append(amount)
                total_fraud += 1
            else:
                legitimate_amounts.append(amount)
                total_legitimate += 1

            if predicted_fraud:
                fraud_confidences.append(confidence)
            else:
                legitimate_confidences.append(confidence)

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
        accuracy = (tp + tn) / total if total > 0 else 0

        # Calculate business-oriented metrics
        fraud_rate = (tp + fn) / total if total > 0 else 0
        fraud_capture_rate = tp / (tp + fn) if (tp + fn) > 0 else 0
        false_positive_rate = fp / (fp + tn) if (fp + tn) > 0 else 0
        false_negative_rate = fn / (fn + tp) if (fn + tp) > 0 else 0

        # Calculate monetary impact metrics
        total_fraud_amount = sum(fraud_amounts) if fraud_amounts else 0
        missed_fraud_amount = 0
        
        # Calculate missed fraud amount by summing amounts where fraud was not detected
        for i, tx in enumerate(synthetic_data):
            if tx.get("is_fraud") and model_output[i].get("decision") != "fraud":
                missed_fraud_amount += tx.get("amount", 0)
        
        fraud_loss_rate = missed_fraud_amount / total_fraud_amount if total_fraud_amount > 0 else 0

        # Calculate confidence statistics
        fraud_confidence_avg = mean(fraud_confidences) if fraud_confidences else 0
        fraud_confidence_std = stdev(fraud_confidences) if len(fraud_confidences) > 1 else 0
        legitimate_confidence_avg = mean(legitimate_confidences) if legitimate_confidences else 0
        legitimate_confidence_std = stdev(legitimate_confidences) if len(legitimate_confidences) > 1 else 0

        # Calculate AUC-PR (approximation)
        def calculate_auc_pr():
            if total_fraud == 0:
                return 0
                
            # Sort by confidence (higher confidence first)
            sorted_data = sorted(
                [(pred.get("confidence", 0.5), truth.get("is_fraud", False)) 
                 for truth, pred in zip(synthetic_data, model_output)],
                key=lambda x: -x[0]
            )
            
            # Initialize precision and recall arrays
            precisions = [1.0]
            recalls = [0.0]
            tp_count = 0
            fp_count = 0
            
            # Calculate precision-recall curve
            for _, is_fraud in sorted_data:
                if is_fraud:
                    tp_count += 1
                else:
                    fp_count += 1
                
                if tp_count > 0:
                    precision = tp_count / (tp_count + fp_count)
                    recall = tp_count / total_fraud
                    precisions.append(precision)
                    recalls.append(recall)
            
            # Calculate AUC using trapezoidal rule
            auc = 0
            for i in range(1, len(precisions)):
                auc += (recalls[i] - recalls[i-1]) * precisions[i]
            
            return auc
            
            precisions = []
            recalls = []
            tp_count = 0
            fp_count = 0
            
            for _, is_fraud in sorted_data:
                if is_fraud:
                    tp_count += 1
                else:
                    fp_count += 1
                
                if tp_count > 0:
                    precisions.append(tp_count / (tp_count + fp_count))
                    recalls.append(tp_count / total_fraud)
            
            if not precisions or not recalls:
                return 0
            
            auc = 0
            for i in range(1, len(precisions)):
                auc += (recalls[i] - recalls[i-1]) * precisions[i]
            
            return auc

        auc_pr = calculate_auc_pr()

        # Calculate AUC-ROC
        def calculate_auc_roc():
            if total_fraud == 0 or total_legitimate == 0:
                return 0
                
            # Sort by confidence
            sorted_data = sorted(
                [(pred.get("confidence", 0.5), truth.get("is_fraud", False)) 
                 for truth, pred in zip(synthetic_data, model_output)],
                key=lambda x: -x[0]
            )
            
            fpr = []
            tpr = []
            tp_count = 0
            fp_count = 0
            
            for _, is_fraud in sorted_data:
                if is_fraud:
                    tp_count += 1
                else:
                    fp_count += 1
                
                if tp_count > 0 or fp_count > 0:
                    fpr.append(fp_count / total_legitimate)
                    tpr.append(tp_count / total_fraud)
            
            if not fpr or not tpr:
                return 0
            
            auc = 0
            for i in range(1, len(fpr)):
                auc += (fpr[i] - fpr[i-1]) * tpr[i]
            
            return auc

        auc_roc = calculate_auc_roc()

        # Create evaluation report with all metrics initialized to 0
        metrics = {
            # Basic metrics
            "true_positives": tp,
            "false_positives": fp,
            "true_negatives": tn,
            "false_negatives": fn,
            "precision": precision,
            "recall": recall,
            "f1_score": f1_score,
            "accuracy": accuracy,
            
            # Business-oriented metrics
            "fraud_rate": fraud_rate,
            "fraud_capture_rate": fraud_capture_rate,
            "false_positive_rate": false_positive_rate,
            "false_negative_rate": false_negative_rate,
            "fraud_loss_rate": fraud_loss_rate,
            
            # Monetary metrics
            "total_fraud_amount": total_fraud_amount,
            "missed_fraud_amount": missed_fraud_amount,
            
            # Confidence metrics
            "fraud_confidence_avg": fraud_confidence_avg,
            "fraud_confidence_std": fraud_confidence_std,
            "legitimate_confidence_avg": legitimate_confidence_avg,
            "legitimate_confidence_std": legitimate_confidence_std,
            
            # AUC metrics
            "auc_pr": auc_pr,
            "auc_roc": auc_roc
        }
        
        # Create report with metadata
        report = {
            "metrics": metrics,
            "metadata": {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "total_samples": total,
                "fraud_samples": total_fraud,
                "legitimate_samples": total_legitimate
            }
        }
        
        # Save report to file with proper naming
        timestamp = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')
        report_file = self.output_dir / f"eval_report_{timestamp}.json"
        
        # Ensure directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Write report
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
        
        return report

        # Ensure all metrics are present, even if they're 0
        for metric in [
            "true_positives", "false_positives", "true_negatives", "false_negatives",
            "precision", "recall", "f1_score", "accuracy",
            "fraud_rate", "fraud_capture_rate", "false_positive_rate", "false_negative_rate",
            "fraud_loss_rate", "total_fraud_amount", "missed_fraud_amount",
            "fraud_confidence_avg", "fraud_confidence_std",
            "legitimate_confidence_avg", "legitimate_confidence_std",
            "auc_pr", "auc_roc"
        ]:
            if metric not in metrics:
                metrics[metric] = 0

        # Create evaluation report
        report = {
            "metrics": metrics,
            "metadata": {
                "total_samples": total,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "evaluation_type": "fraud_detection",
                "fraud_cases": tp + fn,
                "legitimate_cases": tn + fp
            }
        }

        # Create evaluation report
        report = {
            "metrics": {
                # Basic metrics
                "true_positives": tp,
                "false_positives": fp,
                "true_negatives": tn,
                "false_negatives": fn,
                "precision": precision,
                "recall": recall,
                "f1_score": f1_score,
                "accuracy": accuracy,
                
                # Business-oriented metrics
                "fraud_rate": fraud_rate,
                "fraud_capture_rate": fraud_capture_rate,
                "false_positive_rate": false_positive_rate,
                "false_negative_rate": false_negative_rate,
                "fraud_loss_rate": fraud_loss_rate,
                
                # Monetary metrics
                "total_fraud_amount": total_fraud_amount,
                "missed_fraud_amount": missed_fraud_amount,
                
                # Confidence metrics
                "fraud_confidence_avg": fraud_confidence_avg,
                "fraud_confidence_std": fraud_confidence_std,
                "legitimate_confidence_avg": legitimate_confidence_avg,
                "legitimate_confidence_std": legitimate_confidence_std,
                
                # AUC metrics
                "auc_pr": auc_pr
            },
            "metadata": {
                "total_samples": total,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "evaluation_type": "fraud_detection",
                "fraud_cases": tp + fn,
                "legitimate_cases": tn + fp
            },
        }

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
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "evaluation_type": "fraud_detection",
            },
        }

        # Save report
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
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
