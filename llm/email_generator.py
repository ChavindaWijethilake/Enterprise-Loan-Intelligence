# =============================================================================
# llm/email_generator.py
# =============================================================================
# PURPOSE: Use OpenAI GPT to automatically generate professional loan decision
#          emails based on the ML model's prediction.
#
# HOW IT WORKS:
#   1. Takes the loan decision (Approved/Rejected/Conditional)
#   2. Sends a prompt to OpenAI GPT
#   3. GPT writes a professional banking email
#   4. Returns the email text
#
# REQUIRES:
#   - OPENAI_API_KEY in your .env file
#   - pip install openai
# =============================================================================

import os
from dotenv import load_dotenv

# Load environment variables
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.join(BASE_DIR, "..")
ENV_PATH = os.path.join(PROJECT_DIR, ".env")
load_dotenv(ENV_PATH)


def generate_email(applicant_name, decision, probability, loan_amount=None):
    """
    Generate a professional loan decision email using OpenAI GPT.

    Args:
        applicant_name: str — name of the applicant or company
        decision: str — "APPROVED", "REJECTED", or "CONDITIONAL"
        probability: float — approval probability (0.0 to 1.0)
        loan_amount: float — the requested loan amount (optional)

    Returns:
        str — the generated email text
    """
    # Check if OpenAI API key is configured
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key or api_key == "your_openai_key":
        # If no API key, generate a template email instead
        return _generate_template_email(applicant_name, decision, probability, loan_amount)

    # Use the OpenAI API
    try:
        from openai import OpenAI

        client = OpenAI(api_key=api_key)

        # Format loan amount for the prompt
        loan_str = f"₹{loan_amount:,.0f}" if loan_amount else "the requested amount"

        # Build the prompt
        prompt = f"""Write a professional banking email with the following details:

Recipient: {applicant_name}
Loan Amount: {loan_str}
Decision: {decision}
Confidence: {probability:.0%}

Requirements:
- Professional banking tone
- If APPROVED: congratulate them, mention next steps (document verification, fund disbursement)
- If REJECTED: be empathetic, suggest ways to improve their application
- If CONDITIONAL: explain that additional documentation is needed
- Keep it concise (under 200 words)
- Sign as "Loan Processing Department, Enterprise Banking Division"
- Do NOT include the confidence percentage in the email
"""

        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Cost-effective model
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500,
            temperature=0.7,
        )

        email_text = response.choices[0].message.content
        return email_text

    except Exception as e:
        print(f"⚠️  OpenAI API error: {e}")
        # Fallback to template if API fails
        return _generate_template_email(applicant_name, decision, probability, loan_amount)


def _generate_template_email(applicant_name, decision, probability, loan_amount=None):
    """
    Generate a template email when OpenAI API is not available.
    This is a fallback so the system works even without an API key.
    """
    loan_str = f"₹{loan_amount:,.0f}" if loan_amount else "the requested amount"

    if decision == "APPROVED":
        return f"""Subject: Loan Application — Approved

Dear {applicant_name},

We are pleased to inform you that your enterprise loan application for {loan_str} has been approved following our comprehensive automated evaluation.

Our risk assessment system has determined that your application meets our lending criteria. A member of our team will contact you shortly to discuss the next steps, including:

1. Document verification
2. Terms and conditions review
3. Fund disbursement schedule

Thank you for choosing our banking services.

Best regards,
Loan Processing Department
Enterprise Banking Division"""

    elif decision == "REJECTED":
        return f"""Subject: Loan Application — Update

Dear {applicant_name},

Thank you for submitting your enterprise loan application for {loan_str}.

After careful evaluation by our automated risk assessment system, we regret to inform you that your application does not meet our current lending criteria.

You may consider:
1. Improving your credit score
2. Reducing the loan amount
3. Providing additional collateral
4. Reapplying after 6 months

We appreciate your interest and encourage you to apply again in the future.

Best regards,
Loan Processing Department
Enterprise Banking Division"""

    else:  # CONDITIONAL
        return f"""Subject: Loan Application — Additional Information Required

Dear {applicant_name},

Thank you for your enterprise loan application for {loan_str}.

Our automated evaluation system has reviewed your application. To proceed, we require additional documentation:

1. Updated financial statements
2. Business plan or projections
3. Additional collateral details
4. Bank statements for the last 12 months

Please submit the requested documents within 30 days.

Best regards,
Loan Processing Department
Enterprise Banking Division"""


# ---------------------------------------------------------------------------
# Test when running directly
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("=" * 60)
    print("LLM EMAIL GENERATOR TEST")
    print("=" * 60)
    print()

    # Test all three decision types
    for decision in ["APPROVED", "REJECTED", "CONDITIONAL"]:
        print(f"--- {decision} Email ---")
        email = generate_email(
            applicant_name="ABC Manufacturing Ltd",
            decision=decision,
            probability=0.85 if decision == "APPROVED" else 0.25 if decision == "REJECTED" else 0.55,
            loan_amount=25000000,
        )
        print(email)
        print()
        print("-" * 60)
        print()
