# =============================================================================
# src/predict.py
# =============================================================================
# PURPOSE: Load a trained ML model and predict whether a new loan application
#          should be Approved, Rejected, or needs Conditional review.
#
# DECISION ENGINE:
#   The model outputs a probability between 0 and 1.
#   We use thresholds to make the final decision:
#
#   Probability > 0.7  → APPROVED (high confidence)
#   Probability < 0.3  → REJECTED (high confidence)
#   Between 0.3 - 0.7  → CONDITIONAL (needs more review / documentation)
#
# HOW TO RUN:
#   python src/predict.py
# =============================================================================

import pandas as pd
import numpy as np
import joblib
import os

# ---------------------------------------------------------------------------
# STEP 1: Set up file paths
# ---------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.join(BASE_DIR, "..")

XGB_MODEL_PATH = os.path.join(PROJECT_DIR, "models", "xgb_model.pkl")
RF_MODEL_PATH = os.path.join(PROJECT_DIR, "models", "rf_model.pkl")

# Decision thresholds
APPROVE_THRESHOLD = 0.7   # Probability above this → Approved
REJECT_THRESHOLD = 0.3    # Probability below this → Rejected


def make_decision(probability):
    """
    Convert a model probability into a loan decision.

    Args:
        probability: float between 0 and 1 (chance of approval)

    Returns:
        tuple: (decision_text, emoji)
    """
    if probability > APPROVE_THRESHOLD:
        return "APPROVED", "✅"
    elif probability < REJECT_THRESHOLD:
        return "REJECTED", "❌"
    else:
        return "CONDITIONAL", "⚠️"


def predict_loan(applicant_data, model_path=None):
    """
    Predict whether a loan should be approved.

    Args:
        applicant_data: dict with applicant information
        model_path: path to the saved model (default: XGBoost)

    Returns:
        dict with prediction results
    """
    if model_path is None:
        model_path = XGB_MODEL_PATH

    # Load the trained model
    model = joblib.load(model_path)

    # Convert applicant data to DataFrame
    df = pd.DataFrame([applicant_data])

    # -----------------------------------------------------------------------
    # Apply the same feature engineering as during training
    # -----------------------------------------------------------------------
    df["total_assets"] = (
        df["residential_assets_value"]
        + df["commercial_assets_value"]
        + df["luxury_assets_value"]
        + df["bank_asset_value"]
    )
    df["loan_to_income"] = df["loan_amount"] / (df["income_annum"] + 1)
    df["assets_to_loan"] = df["total_assets"] / (df["loan_amount"] + 1)
    df["income_per_dependent"] = df["income_annum"] / (df["no_of_dependents"] + 1)
    df["loan_term_to_amount"] = df["loan_term"] / (df["loan_amount"] + 1)

    # -----------------------------------------------------------------------
    # Make prediction
    # -----------------------------------------------------------------------
    prediction = model.predict(df)[0]
    probabilities = model.predict_proba(df)[0]

    # probability[1] = probability of being Approved (class 1)
    approval_probability = probabilities[1]

    # Apply decision engine
    decision, emoji = make_decision(approval_probability)

    return {
        "prediction": int(prediction),
        "approval_probability": float(approval_probability),
        "rejection_probability": float(probabilities[0]),
        "decision": decision,
        "emoji": emoji,
    }


# ---------------------------------------------------------------------------
# Test with a sample applicant when running directly
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("=" * 60)
    print("LOAN PREDICTION TEST")
    print("=" * 60)
    print()

    # -----------------------------------------------------------------------
    # Sample Applicant 1: Strong application (likely approved)
    # -----------------------------------------------------------------------
    strong_applicant = {
        "no_of_dependents": 2,
        "education": 1,              # Graduate
        "self_employed": 0,           # Not self-employed
        "income_annum": 9200000,      # High income
        "loan_amount": 20000000,
        "loan_term": 12,
        "cibil_score": 780,           # Excellent credit score
        "residential_assets_value": 12000000,
        "commercial_assets_value": 8000000,
        "luxury_assets_value": 15000000,
        "bank_asset_value": 6000000,
    }

    print("--- Test 1: Strong Applicant ---")
    print(f"  Income: ₹{strong_applicant['income_annum']:,.0f}")
    print(f"  Loan Amount: ₹{strong_applicant['loan_amount']:,.0f}")
    print(f"  CIBIL Score: {strong_applicant['cibil_score']}")
    print()

    result1 = predict_loan(strong_applicant)
    print(f"  {result1['emoji']} Decision: {result1['decision']}")
    print(f"  Approval Probability: {result1['approval_probability']:.2%}")
    print()

    # -----------------------------------------------------------------------
    # Sample Applicant 2: Weak application (likely rejected)
    # -----------------------------------------------------------------------
    weak_applicant = {
        "no_of_dependents": 5,
        "education": 0,              # Not Graduate
        "self_employed": 1,           # Self-employed (more risky)
        "income_annum": 1500000,      # Low income
        "loan_amount": 25000000,      # Very high loan
        "loan_term": 6,
        "cibil_score": 380,           # Poor credit score
        "residential_assets_value": 500000,
        "commercial_assets_value": 0,
        "luxury_assets_value": 200000,
        "bank_asset_value": 100000,
    }

    print("--- Test 2: Weak Applicant ---")
    print(f"  Income: ₹{weak_applicant['income_annum']:,.0f}")
    print(f"  Loan Amount: ₹{weak_applicant['loan_amount']:,.0f}")
    print(f"  CIBIL Score: {weak_applicant['cibil_score']}")
    print()

    result2 = predict_loan(weak_applicant)
    print(f"  {result2['emoji']} Decision: {result2['decision']}")
    print(f"  Approval Probability: {result2['approval_probability']:.2%}")
    print()

    # -----------------------------------------------------------------------
    # Sample Applicant 3: Borderline case (conditional)
    # -----------------------------------------------------------------------
    borderline_applicant = {
        "no_of_dependents": 3,
        "education": 1,              # Graduate
        "self_employed": 1,
        "income_annum": 5000000,
        "loan_amount": 15000000,
        "loan_term": 14,
        "cibil_score": 550,           # Average credit score
        "residential_assets_value": 3000000,
        "commercial_assets_value": 1000000,
        "luxury_assets_value": 2000000,
        "bank_asset_value": 1500000,
    }

    print("--- Test 3: Borderline Applicant ---")
    print(f"  Income: ₹{borderline_applicant['income_annum']:,.0f}")
    print(f"  Loan Amount: ₹{borderline_applicant['loan_amount']:,.0f}")
    print(f"  CIBIL Score: {borderline_applicant['cibil_score']}")
    print()

    result3 = predict_loan(borderline_applicant)
    print(f"  {result3['emoji']} Decision: {result3['decision']}")
    print(f"  Approval Probability: {result3['approval_probability']:.2%}")
    print()

    print("=" * 60)
    print("✅ PREDICTION TEST COMPLETE!")
    print("=" * 60)