"""
Minimal Gradio UI for fraud analysis and explainability
"""

import os
import sys
import asyncio
from datetime import datetime
from typing import Any, Dict

import gradio as gr
import requests
import json
from functools import partial

# Add project root to path for imports (flake8 E402 suppressed intentionally)
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # noqa: E402

from app.api_routes import fraud_agent  # noqa: E402
from app.fraud_evaluator import FraudEvaluator  # noqa: E402
from app.models import Currency
from app.currency_cache import CurrencyRateCache  # noqa: E402

# API endpoints
API_BASE_URL = "http://127.0.0.1:8000/api/v1"

# Currency symbols
CURRENCY_SYMBOLS = {
    'USD': '$',
    'EUR': '€',
    'GBP': '£',
    'JPY': '¥',
    'INR': '₹',
    'CNY': '¥',
    'AUD': 'A$',
    'CAD': 'C$'
}

# Initialize currency cache service
currency_cache = CurrencyRateCache(api_key="e4bbd2a2d3e5d91f604a9858")

def format_amount(amount: float, currency: str) -> str:
    """Format amount with appropriate currency symbol"""
    symbol = CURRENCY_SYMBOLS.get(currency, '')
    if currency == 'JPY':  # JPY doesn't use decimals
        return f"{symbol}{amount:,.0f}"
    return f"{symbol}{amount:,.2f}"

async def get_exchange_rate(from_currency: str, to_currency: str) -> float:
    """Get exchange rate between two currencies"""
    rates = await currency_cache.get_rates(from_currency)
    if not rates or 'conversion_rates' not in rates:
        return 1.0
    return rates['conversion_rates'].get(to_currency, 1.0)

def convert_amount(amount: float, from_currency: str, to_currency: str) -> tuple[float, str]:
    """Convert amount between currencies and return formatted string"""
    if from_currency == to_currency:
        return amount, format_amount(amount, to_currency)
        
    # Run async function in sync context
    rate = asyncio.run(get_exchange_rate(from_currency, to_currency))
    converted = amount * rate
    return converted, format_amount(converted, to_currency)

def update_converted_amount(amount: float, from_currency: str, to_currency: str) -> tuple[str, str]:
    """Update the converted amount and exchange rate display"""
    if not amount:
        return "", ""
        
    converted, formatted = convert_amount(amount, from_currency, to_currency)
    rate = asyncio.run(get_exchange_rate(from_currency, to_currency))
    rate_text = f"Exchange Rate: 1 {from_currency} = {rate:.4f} {to_currency}"
    
    return formatted, rate_text

def analyze_transaction(transaction_id, amount, currency, merchant, customer_id, location):
    """Analyze a transaction for potential fraud"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/fraud/analyze",
            json={
                "transaction_id": transaction_id,
                "amount": float(amount),
                "currency": currency,
                "merchant": merchant,
                "customer_id": customer_id,
                "location": location or None
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            # Format the output with available fields
            output = f"Decision: {result.get('decision', 'UNKNOWN')}\n"
            output += f"Confidence: {result.get('confidence', 0) * 100:.1f}%\n\n"
            output += f"Explanation:\n{result.get('explanation', 'No explanation provided')}\n"
            output += f"Risk score: {result.get('risk_score', 0):.2f}\n"
            
            # Include amount and location if available in the request
            if 'amount' in locals() and 'currency' in locals():
                output += f"Amount: {format_amount(amount, currency)}\n"
            if 'location' in locals():
                output += f"Location: {location or 'Unknown'}\n"
                
            output += f"\nRecommended Action:\n{result.get('recommended_action', 'No action recommended')}"
            return output
        else:
            return f"Error: {response.status_code} - {response.text}"
    except Exception as e:
        return f"Error: {str(e)}"


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
    # Header
    gr.Markdown(
        """
        <div style='text-align: center; margin-bottom: 2rem'>
            <h1 style='font-size: 2.5rem; margin: 0.5rem 0; color: teal'>FinConnectAI</h1>
            <p style='font-size: 1.2rem; color: gray'>Real-time Transaction Fraud Detection</p>
        </div>
        """
    )

    with gr.Tab("Transaction Analysis"):
        with gr.Row():
            # Input Panel
            with gr.Column():
                gr.Markdown(
                    "<h3 style='text-align: center; margin-bottom: 1rem'>Transaction Details</h3>"
                )
                transaction_id = gr.Textbox(label="Transaction ID")
                with gr.Row():
                    amount = gr.Number(label="Amount", scale=2)
                    currency = gr.Dropdown(
                        choices=[c.value for c in Currency],
                        value=Currency.USD.value,
                        label="Source Currency",
                        scale=1
                    )
                
                with gr.Row():
                    target_currency = gr.Dropdown(
                        choices=[c.value for c in Currency],
                        value=Currency.INR.value,
                        label="Target Currency",
                        scale=1
                    )
                    converted_amount = gr.Textbox(
                        label="Converted Amount",
                        interactive=False,
                        scale=2
                    )
                
                exchange_rate_text = gr.Textbox(
                    label="Exchange Rate",
                    interactive=False,
                    scale=1
                )
                merchant = gr.Textbox(label="Merchant Name")
                customer_id = gr.Textbox(label="Customer ID")
                location = gr.Textbox(
                    label="Location",
                    placeholder="City, Country (e.g., New York, USA)"
                )
                analyze_btn = gr.Button("🔍 Analyze Transaction")

            # Results Panel
            with gr.Column():
                gr.Markdown(
                    "<h3 style='text-align: center; margin-bottom: 1rem'>Analysis Results</h3>"
                )
                result_text = gr.Textbox(
                    label="Fraud Analysis",
                    lines=10,
                    interactive=False
                )

    with gr.Tab("Performance Metrics"):
        gr.Markdown(
            "<h3 style='text-align: center; margin-bottom: 1rem'>Model Performance Dashboard</h3>"
        )
        metrics_btn = gr.Button("📊 Refresh Metrics")
        metrics_text = gr.Textbox(
            label="Evaluation Metrics",
            lines=12,
            interactive=False
        )

    # Connect components
    analyze_btn.click(
        analyze_transaction,
        inputs=[transaction_id, amount, currency, merchant, customer_id, location],
        outputs=[result_text]
    )
    metrics_btn.click(view_latest_metrics, outputs=[metrics_text])
    
    # Set up currency conversion updates
    amount.change(
        update_converted_amount,
        inputs=[amount, currency, target_currency],
        outputs=[converted_amount, exchange_rate_text]
    )
    currency.change(
        update_converted_amount,
        inputs=[amount, currency, target_currency],
        outputs=[converted_amount, exchange_rate_text]
    )
    target_currency.change(
        update_converted_amount,
        inputs=[amount, currency, target_currency],
        outputs=[converted_amount, exchange_rate_text]
    )
    
if __name__ == "__main__":
    # Start the currency cache in the main thread
    import threading
    
    def start_cache():
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(currency_cache.start())
        except Exception as e:
            print(f"Error in currency cache: {e}")
    
    # Start cache in a daemon thread
    cache_thread = threading.Thread(target=start_cache, daemon=True)
    cache_thread.start()
    
    # Start the Gradio interface
    demo.launch(
        server_name="127.0.0.1",
        share=False
    )
