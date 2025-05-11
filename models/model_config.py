"""
AI Model Configuration

This module contains configuration for the fraud detection AI models.
"""

MODEL_CONFIG = {
    "primary": {
        "provider": "anthropic",
        "model": "claude-3.7-sonnet",
        "parameters": {
            "temperature": 0.2,
            "max_tokens": 1000000,
            "top_p": 0.9,
            "top_k": 50
        },
        "algorithms": [
            "anomaly_detection",
            "pattern_recognition",
            "regression_analysis"
        ]
    },
    "backup": {
        "provider": "openai",
        "model": "gpt-4.5",
        "parameters": {
            "temperature": 0.2,
            "max_tokens": 1000000,
            "top_p": 0.9,
            "top_k": 50
        },
        "algorithms": [
            "anomaly_detection",
            "pattern_recognition",
            "regression_analysis"
        ]
    },
    "validation": {
        "metrics": {
            "accuracy": 0.95,
            "precision": 0.90,
            "recall": 0.90,
            "f1_score": 0.92
        },
        "bias_threshold": 0.1,
        "drift_threshold": 0.05
    }
}

def get_model_config(model_type: str = "primary") -> dict:
    """Get configuration for specified model type"""
    return MODEL_CONFIG.get(model_type, MODEL_CONFIG["primary"])

def get_validation_metrics() -> dict:
    """Get validation metrics configuration"""
    return MODEL_CONFIG["validation"]["metrics"]

def get_bias_threshold() -> float:
    """Get bias detection threshold"""
    return MODEL_CONFIG["validation"]["bias_threshold"]

def get_drift_threshold() -> float:
    """Get model drift threshold"""
    return MODEL_CONFIG["validation"]["drift_threshold"]
