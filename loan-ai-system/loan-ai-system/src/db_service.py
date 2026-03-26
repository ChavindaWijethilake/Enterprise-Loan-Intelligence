import psycopg2
print("!!!! DB_SERVICE MODULE LOADED !!!!")
import os
import traceback
from dotenv import load_dotenv

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.join(BASE_DIR, "..")
ENV_PATH = os.path.join(PROJECT_DIR, ".env")
load_dotenv(ENV_PATH)

def get_connection():
    try:
        connection = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
        )
        return connection
    except Exception as e:
        print(f"❌ DB Conn Error: {e}")
        return None

def save_loan_application(applicant_data: dict, status: str):
    """Saves a loan application to the database and returns the loan_id."""
    print("DEBUG: Inside save_loan_application, calling get_connection()...")
    conn = get_connection()
    if not conn:
        print("DEBUG: get_connection() returned None!")
        return None
    print("DEBUG: Connection acquired successfully.")
    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO loan_applications (applicant_name, applicant_email, no_of_dependents, education, self_employed, income_annum, loan_amount, loan_term, cibil_score, residential_assets_value, commercial_assets_value, luxury_assets_value, bank_asset_value, status) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING loan_id",
            (applicant_data.get("applicant_name"), applicant_data.get("applicant_email", ""), applicant_data.get("no_of_dependents"), applicant_data.get("education"), applicant_data.get("self_employed"), applicant_data.get("income_annum"), applicant_data.get("loan_amount"), applicant_data.get("loan_term"), applicant_data.get("cibil_score"), applicant_data.get("residential_assets_value"), applicant_data.get("commercial_assets_value"), applicant_data.get("luxury_assets_value"), applicant_data.get("bank_asset_value"), status)
        )
        loan_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()
        return loan_id
    except Exception as e:
        print(f"❌ Save App Error: {e}")
        traceback.print_exc()
        return None

def save_loan_prediction(loan_id: int, status: str, probability: float, email_sent: bool):
    conn = get_connection()
    if not conn: return False
    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO loan_predictions (loan_id, model_used, prediction, probability, email_sent) VALUES (%s, 'XGBoost', %s, %s, %s)",
            (loan_id, status, probability, email_sent)
        )
        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Save Pred Error: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    c = get_connection()
    if c:
        print("✅ DB OK")
        c.close()
    else:
        print("❌ DB FAIL")
