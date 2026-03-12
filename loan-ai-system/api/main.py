# =============================================================================
# api/main.py
# =============================================================================
# PURPOSE: Create a REST API using FastAPI that accepts loan applications
#          and returns ML predictions + LLM-generated email content
#          and sends the email automatically.
#
# ENDPOINTS:
#   GET  /           → Welcome message
#   GET  /health     → Health check
#   POST /predict    → Submit loan application, get prediction + email
#
# RUN:
#   uvicorn api.main:app --reload
#
# OPEN:
#   http://localhost:8000/docs
# =============================================================================

import os
import sys

# Add project root to Python path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.join(BASE_DIR, "..")
sys.path.insert(0, PROJECT_DIR)

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import pandas as pd
import joblib

from llm.email_generator import generate_email
from mail_service.email_sender import send_email

# ---------------------------------------------------------------------------
# Initialize FastAPI app
# ---------------------------------------------------------------------------
app = FastAPI(
    title="Loan Approval API",
    description="AI-powered enterprise loan approval system using ML + LLM",
    version="1.0.0",
)

# ---------------------------------------------------------------------------
# Load ML model
# ---------------------------------------------------------------------------
MODEL_PATH = os.path.join(PROJECT_DIR, "models", "xgb_model.pkl")

try:
    model = joblib.load(MODEL_PATH)
    print(f"✅ Model loaded from: {MODEL_PATH}")
except FileNotFoundError:
    print(f"⚠️ Model not found at {MODEL_PATH}. Run train_model.py first!")
    model = None

APPROVE_THRESHOLD = 0.7
REJECT_THRESHOLD = 0.3

# ---------------------------------------------------------------------------
# Request Model
# ---------------------------------------------------------------------------
class LoanApplication(BaseModel):

    applicant_name: str = Field(..., description="Applicant name")
    applicant_email: str = Field(default="", description="Applicant email")

    no_of_dependents: int = Field(..., ge=0, le=10)
    education: int = Field(..., ge=0, le=1)
    self_employed: int = Field(..., ge=0, le=1)

    income_annum: float = Field(..., gt=0)
    loan_amount: float = Field(..., gt=0)
    loan_term: int = Field(..., gt=0)

    cibil_score: int = Field(..., ge=300, le=900)

    residential_assets_value: float
    commercial_assets_value: float
    luxury_assets_value: float
    bank_asset_value: float


# ---------------------------------------------------------------------------
# Response Model
# ---------------------------------------------------------------------------
class PredictionResponse(BaseModel):

    applicant_name: str
    decision: str
    approval_probability: float
    rejection_probability: float
    email_content: str


# ---------------------------------------------------------------------------
# Root endpoint
# ---------------------------------------------------------------------------
@app.get("/")
def root():
    return {
        "message": "Welcome to the Loan Approval API",
        "docs": "Visit /docs for API documentation",
    }


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------
@app.get("/health")
def health_check():

    return {
        "status": "healthy",
        "model_loaded": model is not None,
    }


# ---------------------------------------------------------------------------
# Prediction Endpoint
# ---------------------------------------------------------------------------
@app.post("/predict", response_model=PredictionResponse)
def predict_loan(application: LoanApplication):

    if model is None:
        raise HTTPException(
            status_code=503,
            detail="Model not loaded. Run training first.",
        )

    # Convert request → DataFrame
    data = pd.DataFrame(
        [application.model_dump(exclude={"applicant_name", "applicant_email"})]
    )

    # Feature engineering
    data["total_assets"] = (
        data["residential_assets_value"]
        + data["commercial_assets_value"]
        + data["luxury_assets_value"]
        + data["bank_asset_value"]
    )

    data["loan_to_income"] = data["loan_amount"] / (data["income_annum"] + 1)

    data["assets_to_loan"] = data["total_assets"] / (data["loan_amount"] + 1)

    data["income_per_dependent"] = data["income_annum"] / (
        data["no_of_dependents"] + 1
    )

    data["loan_term_to_amount"] = data["loan_term"] / (data["loan_amount"] + 1)

    # Model prediction
    prediction = model.predict(data)[0]
    probabilities = model.predict_proba(data)[0]

    approval_prob = float(probabilities[1])
    rejection_prob = float(probabilities[0])

    # Decision engine
    if approval_prob > APPROVE_THRESHOLD:
        decision = "APPROVED"
    elif approval_prob < REJECT_THRESHOLD:
        decision = "REJECTED"
    else:
        decision = "CONDITIONAL"

    # Generate email using LLM
    try:

        email_content = generate_email(
            applicant_name=application.applicant_name,
            decision=decision,
            probability=approval_prob,
            loan_amount=application.loan_amount,
        )

        # Send email if address provided
        if application.applicant_email:

            send_email(
                recipient_email=application.applicant_email,
                subject="Loan Application Decision",
                body=email_content,
            )

    except Exception as e:

        email_content = f"[Email generation failed: {str(e)}. Check OPENAI_API_KEY]"

    # Return API response
    return PredictionResponse(
        applicant_name=application.applicant_name,
        decision=decision,
        approval_probability=approval_prob,
        rejection_probability=rejection_prob,
        email_content=email_content,
    )