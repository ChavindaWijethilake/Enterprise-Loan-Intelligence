# =============================================================================
# src/db_service.py — PostgreSQL Database Service Layer
# =============================================================================
# PURPOSE:
#   Manages all database interactions for the AELAS system using a psycopg2
#   SimpleConnectionPool (min=1, max=10 connections). Provides CRUD operations
#   for the loan_applications and loan_predictions tables.
#
# POOL LIFECYCLE:
#   - Pool is created at module import time using .env credentials.
#   - get_connection() borrows a connection from the pool.
#   - release_connection() returns it. Always call this in a finally block.
#
# TABLES:
#   - loan_applications: stores applicant details + current status.
#   - loan_predictions:  stores AI model output + email delivery status.
# =============================================================================

import psycopg2
from psycopg2 import pool
import os
import traceback
from dotenv import load_dotenv
from src.logger import get_logger

logger = get_logger("db_service")
logger.info("DB_SERVICE MODULE LOADED")

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.join(BASE_DIR, "..")
ENV_PATH = os.path.join(PROJECT_DIR, ".env")
load_dotenv(ENV_PATH)

# Initialize Connection Pool
try:
    db_pool = psycopg2.pool.SimpleConnectionPool(
        1, 10,
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
    )
    if db_pool:
        logger.info("Database connection pool created successfully")
except Exception as e:
    logger.error(f"Failed to create connection pool: {e}", exc_info=True)
    db_pool = None

def get_connection():
    """Borrow a connection from the pool. Returns None if pool is unavailable."""
    try:
        if db_pool:
            return db_pool.getconn()
        return None
    except Exception as e:
        logger.error(f"DB Conn Error: {e}", exc_info=True)
        return None

def release_connection(conn):
    """Return a borrowed connection back to the pool."""
    try:
        if db_pool and conn:
            db_pool.putconn(conn)
    except Exception as e:
        logger.error(f"DB Conn Release Error: {e}", exc_info=True)

def save_loan_application(applicant_data: dict, status: str):
    """
    Insert a new loan application into the loan_applications table.

    Args:
        applicant_data: Dict containing all applicant fields (name, email,
                        dependents, education, income, assets, etc.).
        status: Initial status string (e.g., 'PENDING', 'APPROVED').

    Returns:
        int | None: The auto-generated loan_id, or None on failure.
    """
    logger.debug("Inside save_loan_application, calling get_connection()...")
    conn = get_connection()
    if not conn:
        logger.error("get_connection() returned None!")
        return None
    logger.debug("Connection acquired successfully.")
    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO loan_applications (applicant_name, applicant_email, no_of_dependents, education, self_employed, income_annum, loan_amount, loan_term, cibil_score, residential_assets_value, commercial_assets_value, luxury_assets_value, bank_asset_value, status) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING loan_id",
            (applicant_data.get("applicant_name"), applicant_data.get("applicant_email", ""), applicant_data.get("no_of_dependents"), applicant_data.get("education"), applicant_data.get("self_employed"), applicant_data.get("income_annum"), applicant_data.get("loan_amount"), applicant_data.get("loan_term"), applicant_data.get("cibil_score"), applicant_data.get("residential_assets_value"), applicant_data.get("commercial_assets_value"), applicant_data.get("luxury_assets_value"), applicant_data.get("bank_asset_value"), status)
        )
        loan_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        release_connection(conn)
        return loan_id
    except Exception as e:
        logger.error(f"Save App Error: {e}", exc_info=True)
        if conn: release_connection(conn)
        return None

def save_loan_prediction(loan_id: int, status: str, probability: float, email_sent: bool):
    """
    Record an AI prediction result in the loan_predictions table.

    Args:
        loan_id:     Foreign key to loan_applications.
        status:      Prediction outcome (APPROVED / REJECTED / CONDITIONAL).
        probability: Model's approval probability (0.0–1.0).
        email_sent:  Whether the notification email was delivered.

    Returns:
        bool: True on success, False on failure.
    """
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
        release_connection(conn)
        return True
    except Exception as e:
        logger.error(f"Save Pred Error: {e}", exc_info=True)
        if conn: release_connection(conn)
        return False

def get_loan_application(loan_id: int) -> dict:
    """
    Retrieve a single loan application by its ID.

    Returns:
        dict | None: Application fields as a dictionary, or None if not found.
    """
    conn = get_connection()
    if not conn: return None
    try:
        cur = conn.cursor()
        cur.execute("SELECT applicant_name, applicant_email, no_of_dependents, education, self_employed, income_annum, loan_amount, loan_term, cibil_score, residential_assets_value, commercial_assets_value, luxury_assets_value, bank_asset_value, status FROM loan_applications WHERE loan_id = %s", (loan_id,))
        row = cur.fetchone()
        cur.close()
        release_connection(conn)
        if not row: return None
        
        return {
            "applicant_name": row[0],
            "applicant_email": row[1],
            "no_of_dependents": row[2],
            "education": row[3],
            "self_employed": row[4],
            "income_annum": row[5],
            "loan_amount": row[6],
            "loan_term": row[7],
            "cibil_score": row[8],
            "residential_assets_value": row[9],
            "commercial_assets_value": row[10],
            "luxury_assets_value": row[11],
            "bank_asset_value": row[12],
            "status": row[13]
        }
    except Exception as e:
        logger.error(f"Get App Error: {e}", exc_info=True)
        if conn: release_connection(conn)
        return None

def get_all_loans():
    """
    Retrieve all loan applications ordered by creation date (newest first).

    Returns:
        list[dict]: List of application dictionaries, empty list on failure.
    """
    conn = get_connection()
    if not conn: return []
    try:
        cur = conn.cursor()
        cur.execute("SELECT loan_id, applicant_name, applicant_email, no_of_dependents, education, self_employed, income_annum, loan_amount, loan_term, cibil_score, residential_assets_value, commercial_assets_value, luxury_assets_value, bank_asset_value, status, created_at FROM loan_applications ORDER BY created_at DESC")
        rows = cur.fetchall()
        cur.close()
        release_connection(conn)
        
        loans = []
        for r in rows:
            loans.append({
                "loan_id": r[0],
                "applicant_name": r[1],
                "applicant_email": r[2],
                "no_of_dependents": r[3],
                "education": r[4],
                "self_employed": r[5],
                "income_annum": r[6],
                "loan_amount": r[7],
                "loan_term": r[8],
                "cibil_score": r[9],
                "residential_assets_value": r[10],
                "commercial_assets_value": r[11],
                "luxury_assets_value": r[12],
                "bank_asset_value": r[13],
                "status": r[14],
                "created_at": r[15]
            })
        return loans
    except Exception as e:
        logger.error(f"Get All Loans Error: {e}", exc_info=True)
        if conn: release_connection(conn)
        return []

def get_loan_by_id(loan_id: int):
    """Alias for get_loan_application — used by api/main.py for consistency."""
    return get_loan_application(loan_id)

def update_loan_status(loan_id: int, status: str):
    """
    Update the status field of an existing loan application.

    Args:
        loan_id: Target loan ID.
        status:  New status (APPROVED / REJECTED / PROCESSING / FAILED, etc.).

    Returns:
        bool: True on success, False on failure.
    """
    conn = get_connection()
    if not conn: return False
    try:
        cur = conn.cursor()
        cur.execute("UPDATE loan_applications SET status = %s WHERE loan_id = %s", (status, loan_id))
        conn.commit()
        cur.close()
        release_connection(conn)
        return True
    except Exception as e:
        logger.error(f"Update Status Error: {e}", exc_info=True)
        if conn: release_connection(conn)
        return False

if __name__ == "__main__":
    c = get_connection()
    if c:
        logger.info("DB OK")
        release_connection(c)
    else:
        logger.error("DB FAIL")
