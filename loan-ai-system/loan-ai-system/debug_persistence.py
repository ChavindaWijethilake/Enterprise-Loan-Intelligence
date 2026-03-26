import os
import sys
import pandas as pd
import joblib

# Add project root to path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.database import save_loan_application, save_loan_prediction
from api.main import LoanApplication

def debug_persistence():
    print("Direct Persistence Test Starting...")
    
    app_data = {
        "applicant_name": "Test User",
        "applicant_email": "test@example.com",
        "no_of_dependents": 1,
        "education": 1,
        "self_employed": 0,
        "income_annum": 1000000,
        "loan_amount": 500000,
        "loan_term": 12,
        "cibil_score": 700,
        "residential_assets_value": 1000000,
        "commercial_assets_value": 0,
        "luxury_assets_value": 0,
        "bank_asset_value": 500000
    }
    
    decision = "APPROVED"
    approval_prob = 0.85
    
    print(f"Saving Application: {app_data['applicant_name']}")
    loan_id = save_loan_application(app_data, decision)
    
    if loan_id:
        print(f"✅ Application Saved! Loan ID: {loan_id}")
        pred_saved = save_loan_prediction(
            loan_id=loan_id,
            status=decision,
            probability=approval_prob,
            email_sent=True
        )
        if pred_saved:
            print("✅ Prediction Saved!")
        else:
            print("❌ Prediction Save Failed!")
    else:
        print("❌ Application Save Failed!")

if __name__ == "__main__":
    debug_persistence()
