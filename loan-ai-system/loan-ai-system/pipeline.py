# =============================================================================
# pipeline.py
# =============================================================================
# PURPOSE: End-to-end automation script that ties everything together.
#
# This script demonstrates the FULL automated loan approval pipeline:
#   1. Receives a loan application (simulated)
#   2. Preprocesses the data
#   3. Runs ML prediction
#   4. Applies decision engine
#   5. Generates email using LLM
#   6. Sends email (if configured)
#   7. Stores result in database (if configured)
#
# HOW TO RUN:
#   python pipeline.py
#
# PREREQUISITES:
#   1. Run: python src/preprocess.py
#   2. Run: python src/feature_engineering.py
#   3. Run: python src/train_model.py
# =============================================================================

import os
import sys

# Add project root to Python path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from src.predict import predict_loan
from llm.email_generator import generate_email
from mail_service.email_sender import send_email
from src.db_service import save_loan_application, save_loan_prediction


def process_loan_application(applicant):
    """
    Process a single loan application through the complete pipeline.

    Args:
        applicant: dict with applicant information including:
            - name: str
            - email: str
            - All loan features (no_of_dependents, income_annum, etc.)

    Returns:
        dict with the complete result
    """
    name = applicant.pop("name", "Unknown Applicant")
    email_address = applicant.pop("email", "")

    print(f"  📋 Applicant: {name}")
    print(f"  💰 Loan Amount: ₹{applicant['loan_amount']:,.0f}")
    print(f"  📊 CIBIL Score: {applicant['cibil_score']}")
    print()

    # ------------------------------------------------------------------
    # STEP 1: ML Prediction
    # ------------------------------------------------------------------
    print("  [1/4] Running ML prediction...")
    result = predict_loan(applicant)
    print(f"        {result['emoji']} Decision: {result['decision']}")
    print(f"        Approval probability: {result['approval_probability']:.2%}")
    print()

    # ------------------------------------------------------------------
    # STEP 2: Generate Email using LLM
    # ------------------------------------------------------------------
    print("  [2/4] Generating decision email with LLM...")
    email_content = generate_email(
        applicant_name=name,
        decision=result["decision"],
        probability=result["approval_probability"],
        loan_amount=applicant["loan_amount"],
    )
    print(f"        Email generated ✓ ({len(email_content)} characters)")
    print()

    # ------------------------------------------------------------------
    # STEP 3: Send Email
    # ------------------------------------------------------------------
    print("  [3/4] Sending email...")
    if email_address:
        email_sent = send_email(
            recipient_email=email_address,
            subject=f"Loan Application Decision — {result['decision']}",
            body=email_content,
        )
    else:
        print("        ⚠️  No email address provided — skipping email send")
        email_sent = False
    print()

    # ------------------------------------------------------------------
    # STEP 4: Store in Database (optional)
    # ------------------------------------------------------------------
    print("  [4/4] Storing result in database...")
    try:
        # Prepare data for save_loan_application (add back name and email)
        applicant_data = applicant.copy()
        applicant_data["applicant_name"] = name
        applicant_data["applicant_email"] = email_address
        
        loan_id = save_loan_application(applicant_data, result["decision"])
        
        if loan_id:
            save_loan_prediction(
                loan_id=loan_id,
                status=result["decision"],
                probability=result["approval_probability"],
                email_sent=email_sent
            )
            print(f"        ✅ Saved to database (loan_id: {loan_id})")
        else:
            print("        ⚠️  Database save failed — check logs")
            
    except Exception as e:
        print(f"        ⚠️  Database storage skipped: {e}")
    print()

    return {
        "name": name,
        "decision": result["decision"],
        "probability": result["approval_probability"],
        "email_generated": True,
        "email_sent": email_sent,
        "email_content": email_content,
    }


# =============================================================================
# MAIN: Demo with sample loan applications
# =============================================================================
if __name__ == "__main__":
    print("=" * 70)
    print("🏦 AUTOMATED ENTERPRISE LOAN APPROVAL PIPELINE")
    print("=" * 70)
    print()
    print("This pipeline demonstrates the full automated workflow:")
    print("  Application → ML Prediction → LLM Email → Send → Database")
    print()

    # -----------------------------------------------------------------------
    # Sample applications to test the pipeline
    # -----------------------------------------------------------------------
    sample_applications = [
        {
            "name": "Reliance Industries Ltd",
            "email": "",
            "no_of_dependents": 2,
            "education": 1,
            "self_employed": 0,
            "income_annum": 9500000,
            "loan_amount": 25000000,
            "loan_term": 12,
            "cibil_score": 800,
            "residential_assets_value": 15000000,
            "commercial_assets_value": 10000000,
            "luxury_assets_value": 20000000,
            "bank_asset_value": 8000000,
        },
        {
            "name": "Small Startup Pvt Ltd",
            "email": "",
            "no_of_dependents": 5,
            "education": 0,
            "self_employed": 1,
            "income_annum": 1200000,
            "loan_amount": 30000000,
            "loan_term": 6,
            "cibil_score": 350,
            "residential_assets_value": 200000,
            "commercial_assets_value": 0,
            "luxury_assets_value": 100000,
            "bank_asset_value": 50000,
        },
        {
            "name": "Medium Enterprise Co",
            "email": "",
            "no_of_dependents": 3,
            "education": 1,
            "self_employed": 1,
            "income_annum": 5500000,
            "loan_amount": 18000000,
            "loan_term": 16,
            "cibil_score": 580,
            "residential_assets_value": 4000000,
            "commercial_assets_value": 2000000,
            "luxury_assets_value": 3000000,
            "bank_asset_value": 2000000,
        },
    ]

    results = []

    for i, applicant in enumerate(sample_applications, 1):
        print(f"{'─' * 70}")
        print(f"APPLICATION {i} of {len(sample_applications)}")
        print(f"{'─' * 70}")
        print()

        result = process_loan_application(applicant)
        results.append(result)

    # -----------------------------------------------------------------------
    # Summary
    # -----------------------------------------------------------------------
    print("=" * 70)
    print("📊 PIPELINE SUMMARY")
    print("=" * 70)
    print()
    print(f"  {'Applicant':<30} {'Decision':<15} {'Probability':>12}")
    print(f"  {'─' * 30} {'─' * 15} {'─' * 12}")

    for r in results:
        emoji = "✅" if r["decision"] == "APPROVED" else "❌" if r["decision"] == "REJECTED" else "⚠️"
        print(f"  {r['name']:<30} {emoji} {r['decision']:<12} {r['probability']:>11.2%}")

    print()
    print("=" * 70)
    print("✅ PIPELINE COMPLETE!")
    print("=" * 70)
    print()
    print("Generated emails are shown above for each application.")
    print("To send real emails, configure EMAIL_ADDRESS and EMAIL_PASSWORD in .env")
