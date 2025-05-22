"""
Minimal Gradio UI for fraud analysis and explainability
"""

import os
import sys
from datetime import datetime
from typing import Any, Dict

import gradio as gr

# Add project root to path for imports (flake8 E402 suppressed intentionally)
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # noqa: E402

from app.api_routes import fraud_agent  # noqa: E402
from app.fraud_evaluator import FraudEvaluator  # noqa: E402


def analyze_transaction(
    transaction_id: str, amount: float, merchant: str, customer_id: str
) -> Dict[str, Any]:
    """Analyze a single transaction for fraud."""
    transaction = {
        "transaction_id": transaction_id,
        "amount": amount,
        "merchant": merchant,
        "customer_id": customer_id,
        "timestamp": datetime.utcnow().isoformat(),
    }

    result = fraud_agent.analyze_transaction(transaction)

    # Format explanation for display
    explanation = result["explanation"]
    confidence = f"{result['confidence'] * 100:.1f}%"
    decision = result["decision"].upper()
    action = result["recommended_action"]

    return (
        f"Decision: {decision}\n"
        f"Confidence: {confidence}\n\n"
        f"Explanation:\n"
        f"{explanation}\n\n"
        f"Recommended Action:\n"
        f"{action}"
    )


def view_latest_metrics() -> str:
    """Display the latest evaluation metrics."""
    evaluator = FraudEvaluator()
    report = evaluator.get_latest_report()

    if not report:
        return "No evaluation reports available yet."

    metrics = report["metrics"]
    return (
        f"Latest Fraud Detection Metrics:\n\n"
        f"Precision: {metrics['precision']:.2%}\n"
        f"Recall: {metrics['recall']:.2%}\n"
        f"F1 Score: {metrics['f1_score']:.2%}\n"
        f"Accuracy: {metrics['accuracy']:.2%}\n\n"
        f"True Positives: {metrics['true_positives']}\n"
        f"False Positives: {metrics['false_positives']}\n"
        f"True Negatives: {metrics['true_negatives']}\n"
        f"False Negatives: {metrics['false_negatives']}\n\n"
        f"Last Updated: {report['metadata']['timestamp']}"
    )


# Create Gradio interface
with gr.Blocks(title="FinConnectAI Fraud Analysis") as demo:
    gr.Markdown("## Transaction Fraud Analysis")

    with gr.Row():
        with gr.Column():
            # Input fields
            transaction_id = gr.Textbox(label="Transaction ID")
            amount = gr.Number(label="Amount")
            merchant = gr.Textbox(label="Merchant Name")
            customer_id = gr.Textbox(label="Customer ID")

            analyze_btn = gr.Button("Analyze Transaction")

        with gr.Column():
            # Analysis output
            result_text = gr.Textbox(label="Analysis Result", lines=10, interactive=False)

    gr.Markdown("## Model Performance Metrics")
    metrics_btn = gr.Button("View Latest Metrics")
    metrics_text = gr.Textbox(label="Evaluation Metrics", lines=12, interactive=False)

    # Connect components
    analyze_btn.click(
        analyze_transaction,
        inputs=[transaction_id, amount, merchant, customer_id],
        outputs=result_text,
    )

    metrics_btn.click(view_latest_metrics, inputs=None, outputs=metrics_text)


if __name__ == "__main__":
    demo.launch(
        server_name="127.0.0.1",
        server_port=7863,
        share=False,  # Don't expose publicly
        pwa=True  # Enable Progressive Web App support
    )
