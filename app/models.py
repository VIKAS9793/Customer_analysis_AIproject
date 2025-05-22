from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum

class Currency(str, Enum):
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"
    JPY = "JPY"
    INR = "INR"
    CNY = "CNY"
    AUD = "AUD"
    CAD = "CAD"

class Transaction(BaseModel):
    transaction_id: str
    amount: float
    merchant: str
    customer_id: str
    currency: Currency = Field(default=Currency.USD)
    location: Optional[str] = None

class FraudAnalysisResponse(BaseModel):
    decision: str
    confidence: float
    explanation: str
    risk_score: float
    amount: float
    currency: Currency
    location: Optional[str]
    recommended_action: str
