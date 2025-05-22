"""
FastAPI routes for FinConnectAI fraud detection endpoints
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

# Configure logging
logger = logging.getLogger(__name__)

from agents.fraud_agent import FraudAgent
from app.fraud_evaluator import FraudEvaluator
from app.models import Currency


class Transaction(BaseModel):
    transaction_id: str = Field(description="Unique identifier for the transaction")
    amount: float = Field(gt=0, description="Transaction amount")
    merchant: str = Field(description="Name of the merchant")
    customer_id: str = Field(description="Customer identifier")
    currency: Currency = Field(default=Currency.USD, description="Transaction currency")
    location: Optional[str] = Field(default=None, description="Transaction location")
    timestamp: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat(),
        description="Transaction timestamp in ISO format",
    )


class FraudAnalysisResponse(BaseModel):
    decision: str = Field(description="Fraud decision: 'REJECT', 'REVIEW', or 'APPROVE'")
    confidence: float = Field(ge=0, le=1, description="Confidence score between 0 and 1")
    explanation: str = Field(description="Human-readable explanation of the decision")
    risk_score: float = Field(ge=0, le=1, description="Risk score between 0 and 1")
    recommended_action: str = Field(description="Recommended action based on analysis")
    timestamp: str = Field(description="Analysis timestamp in ISO format")


class EvaluationMetrics(BaseModel):
    true_positives: int = Field(ge=0, description="Number of correctly identified fraud cases")
    false_positives: int = Field(
        ge=0, description="Number of legitimate transactions flagged as fraud"
    )
    true_negatives: int = Field(
        ge=0, description="Number of correctly identified legitimate transactions"
    )
    false_negatives: int = Field(ge=0, description="Number of fraud cases missed")
    precision: float = Field(ge=0, le=1, description="Precision score (0-1)")
    recall: float = Field(ge=0, le=1, description="Recall score (0-1)")
    f1_score: float = Field(ge=0, le=1, description="F1 score (0-1)")
    accuracy: float = Field(ge=0, le=1, description="Accuracy score (0-1)")


class EvaluationReport(BaseModel):
    metrics: EvaluationMetrics
    metadata: Dict[str, Any] = Field(description="Report metadata including timestamp")


app = FastAPI(
    title="FinConnectAI API",
    description="Enterprise fraud detection and analysis API",
    version="2.1",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Initialize components
fraud_agent = FraudAgent()
evaluator = FraudEvaluator()


@app.post(
    "/api/v1/fraud/analyze",
    response_model=FraudAnalysisResponse,
    summary="Analyze transaction for fraud",
    description="Analyzes a single transaction for potential fraud using the FraudAgent",
)
async def analyze_transaction(transaction: Transaction) -> FraudAnalysisResponse:
    """Analyze a single transaction for fraud."""
    try:
        # Convert to dict and add timestamp
        transaction_dict = transaction.dict()
        transaction_dict["timestamp"] = datetime.utcnow().isoformat()

        # Ensure all required fields are present and valid
        required_fields = ["transaction_id", "amount", "merchant", "customer_id"]
        for field in required_fields:
            if field not in transaction_dict or transaction_dict[field] is None:
                raise HTTPException(
                    status_code=400,
                    detail=f"Missing required field: {field}"
                )

        try:
            result = fraud_agent.analyze_transaction(transaction_dict)
        except Exception as agent_error:
            logger.error(f"Error in fraud agent: {str(agent_error)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error processing transaction: {str(agent_error)}"
            )

        # Validate required response fields
        required_response_fields = ["decision", "confidence", "explanation"]
        for field in required_response_fields:
            if field not in result or result[field] is None:
                raise HTTPException(
                    status_code=500,
                    detail=f"Invalid response from fraud agent: missing {field}"
                )
        
        # Process confidence (ensure it's between 0 and 1)
        try:
            confidence = float(result["confidence"])
            confidence = max(0.0, min(1.0, confidence))  # Clamp between 0 and 1
            if confidence > 1.0 and confidence <= 100.0:
                confidence = confidence / 100.0  # Convert percentage to decimal if needed
        except (ValueError, TypeError):
            confidence = 0.5  # Default confidence if invalid
            
        # Process risk score (ensure it's between 0 and 1)
        try:
            risk_score = float(result.get("risk_score", 0.0))
            risk_score = max(0.0, min(1.0, risk_score))  # Clamp between 0 and 1
        except (ValueError, TypeError):
            risk_score = 0.0  # Default risk score if invalid
        
        # Get other fields with defaults
        decision = str(result.get("decision", "REVIEW")).upper()
        explanation = str(result.get("explanation", "No explanation provided"))
        recommended_action = str(result.get("recommended_action", "Review recommended"))
        timestamp = result.get("timestamp", datetime.utcnow().isoformat())
        
        return FraudAnalysisResponse(
            decision=decision,
            confidence=confidence,
            explanation=explanation,
            risk_score=risk_score,
            recommended_action=recommended_action,
            timestamp=timestamp
        )
        
    except HTTPException:
        raise  # Re-raise HTTP exceptions
    except Exception as e:
        logger.error(f"Unexpected error in analyze_transaction: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred: {str(e)}"
        )


class EvaluationRequest(BaseModel):
    model_config = {"protected_namespaces": ()}
    
    synthetic_data: List[Dict[str, bool]] = Field(
        description="List of ground truth data with 'is_fraud' labels"
    )
    model_predictions: List[Dict[str, Any]] = Field(
        description="List of model predictions with decisions",
        alias="model_output"  # Maintains backward compatibility with existing code
    )


@app.post(
    "/api/v1/fraud/evaluate",
    response_model=EvaluationReport,
    summary="Evaluate fraud detection performance",
    description="Calculate performance metrics using synthetic data and model outputs",
)
async def evaluate_fraud_detection(request: EvaluationRequest) -> EvaluationReport:
    """Evaluate fraud detection performance."""
    try:
        # Convert the request data to the format expected by the evaluator
        ground_truth = [item["is_fraud"] for item in request.synthetic_data]
        predictions = [
            {"is_fraud": item.get("is_fraud", False), "confidence": item.get("confidence", 0.0)}
            for item in request.model_predictions
        ]
        
        # Get evaluation metrics
        metrics = evaluator.evaluate(ground_truth, predictions)
        
        # Create and return the evaluation report
        report = EvaluationReport(
            metrics=metrics,
            metadata={
                "evaluation_timestamp": datetime.utcnow().isoformat(),
                "model_version": "1.0.0"
            }
        )
        return report
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get(
    "/api/v1/fraud/latest-report",
    response_model=EvaluationReport,
    summary="Get latest evaluation report",
    description="Retrieve the most recent fraud detection evaluation report",
)
async def get_latest_evaluation() -> EvaluationReport:
    """Get the most recent evaluation report."""
    try:
        report = evaluator.get_latest_report()
        if not report:
            raise HTTPException(status_code=404, detail="No evaluation reports found")
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
