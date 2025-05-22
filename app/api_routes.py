"""
FastAPI routes for FinConnectAI fraud detection endpoints
"""

from datetime import datetime
from typing import Any, Dict, List

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from agents.fraud_agent import FraudAgent

from .fraud_evaluator import FraudEvaluator


class Transaction(BaseModel):
    transaction_id: str = Field(description="Unique identifier for the transaction")
    amount: float = Field(gt=0, description="Transaction amount")
    merchant: str = Field(description="Name of the merchant")
    customer_id: str = Field(description="Customer identifier")
    timestamp: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat(),
        description="Transaction timestamp in ISO format",
    )


class FraudAnalysisResponse(BaseModel):
    decision: str = Field(description="Fraud decision: 'fraud' or 'legitimate'")
    confidence: float = Field(ge=0, le=1, description="Confidence score between 0 and 1")
    explanation: str = Field(description="Human-readable explanation of the decision")
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
fraud_agent = FraudAgent({"risk_threshold": 0.7})
evaluator = FraudEvaluator()


@app.post(
    "/api/v1/fraud/analyze",
    response_model=FraudAnalysisResponse,
    summary="Analyze transaction for fraud",
    description="Analyzes a single transaction for potential fraud using the FraudAgent",
)
async def analyze_transaction(transaction: Transaction) -> FraudAnalysisResponse:
    """Analyze a single transaction for fraud."""
    required_fields = ["transaction_id", "amount", "merchant"]
    missing_fields = [field for field in required_fields if field not in transaction]

    if missing_fields:
        raise HTTPException(
            status_code=400, detail=f"Missing required fields: {', '.join(missing_fields)}"
        )

    try:
        result = fraud_agent.analyze_transaction(transaction)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class EvaluationRequest(BaseModel):
    synthetic_data: List[Dict[str, bool]] = Field(
        description="List of ground truth data with 'is_fraud' labels"
    )
    model_output: List[Dict[str, Any]] = Field(
        description="List of model predictions with decisions"
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
        report = evaluator.evaluate_predictions(request.synthetic_data, request.model_output)
        return report
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
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
