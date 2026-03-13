import os
import sys
from dotenv import load_dotenv

# Add project root to path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

load_dotenv()
print(f"DEBUG: DB_NAME from env: '{os.getenv('DB_NAME')}'")

import sys
print(f"DEBUG: sys.path: {sys.path}")
import importlib
import src.db_service
importlib.reload(src.db_service)
print(f"IMPORT DEBUG: src.db_service file: {src.db_service.__file__}")
from src.db_service import save_loan_application

def test():
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
    
    print("Attempting to save application...")
    try:
        loan_id = save_loan_application(app_data, "APPROVED")
        if loan_id:
            print(f"SUCCESS! Loan ID: {loan_id}")
            # Immediate check
            import psycopg2
            from src.db_service import get_connection
            conn2 = get_connection()
            cur2 = conn2.cursor()
            cur2.execute("SELECT count(*) FROM loan_applications;")
            cnt = cur2.fetchone()[0]
            print(f"Immediate check count: {cnt}")
            cur2.close()
            conn2.close()
        else:
            print("FAILED! save_loan_application returned None")
    except Exception as e:
        print(f"EXCEPTIONAL FAILURE: {e}")

if __name__ == "__main__":
    test()
