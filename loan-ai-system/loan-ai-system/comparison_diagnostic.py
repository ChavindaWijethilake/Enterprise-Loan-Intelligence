import os
import sys
import psycopg2
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

load_dotenv()

from src.db_service import get_connection

def diagnostic():
    print("=== DATABASE DIAGNOSTIC ===")
    print(f"ENV DB_NAME: {os.getenv('DB_NAME')}")
    print(f"ENV DB_HOST: {os.getenv('DB_HOST')}")
    print(f"ENV DB_USER: {os.getenv('DB_USER')}")
    
    conn = get_connection()
    if conn:
        dsn = conn.get_dsn_parameters()
        print(f"ACTUAL CONNECTION DSN: {dsn}")
        
        cur = conn.cursor()
        cur.execute("SELECT current_database(), current_user;")
        db, user = cur.fetchone()
        print(f"DATABASE: {db}, USER: {user}")
        
        cur.execute("SELECT count(*) FROM loan_applications;")
        print(f"Loan Applications count: {cur.fetchone()[0]}")
        
        cur.close()
        conn.close()
    else:
        print("FAILED TO CONNECT")

if __name__ == "__main__":
    diagnostic()
