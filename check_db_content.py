import os
import sys

# Add project root to path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from dotenv import load_dotenv
load_dotenv()
print(f"DEBUG: check_db_content.py DB_NAME: '{os.getenv('DB_NAME')}'")
from src.db_service import get_connection

def check_db():
    conn = get_connection()
    if not conn:
        print("Failed to connect to DB")
        return
    
    try:
        cur = conn.cursor()
        
        cur.execute("SELECT count(*) FROM loan_applications;")
        app_count = cur.fetchone()[0]
        
        cur.execute("SELECT count(*) FROM loan_predictions;")
        pred_count = cur.fetchone()[0]
        
        print(f"Loan Applications: {app_count}")
        print(f"Loan Predictions: {pred_count}")
        
        if app_count > 0:
            cur.execute("SELECT loan_id, applicant_name, status FROM loan_applications LIMIT 5;")
            rows = cur.fetchall()
            print("\nRecent Applications:")
            for row in rows:
                print(row)
                
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_db()
