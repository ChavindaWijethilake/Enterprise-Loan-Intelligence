# =============================================================================
# src/create_table.py
# =============================================================================
# PURPOSE: Create the database tables in PostgreSQL.
#
# TABLES CREATED:
#   1. loan_applications — stores submitted loan applications
#   2. loan_predictions  — stores ML prediction results
#
# HOW TO RUN:
#   python src/create_table.py
#
# PREREQUISITE:
#   - PostgreSQL must be running
#   - Database 'loan_system' must exist (create it in pgAdmin first)
#   - .env must have correct database credentials
# =============================================================================

import os
import sys

# Add parent directory to path so we can import from src/
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.join(BASE_DIR, "..")
sys.path.insert(0, PROJECT_DIR)

from src.db_service import get_connection


def create_tables():
    """Create all required database tables."""

    # SQL to create the loan_applications table
    create_applications_table = """
    CREATE TABLE IF NOT EXISTS loan_applications (
        loan_id SERIAL PRIMARY KEY,
        applicant_name TEXT,
        applicant_email TEXT,
        no_of_dependents INT,
        education INT,
        self_employed INT,
        income_annum FLOAT,
        loan_amount FLOAT,
        loan_term INT,
        cibil_score INT,
        residential_assets_value FLOAT,
        commercial_assets_value FLOAT,
        luxury_assets_value FLOAT,
        bank_asset_value FLOAT,
        status TEXT DEFAULT 'PENDING',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """

    # SQL to create the loan_predictions table
    create_predictions_table = """
    CREATE TABLE IF NOT EXISTS loan_predictions (
        prediction_id SERIAL PRIMARY KEY,
        loan_id INT REFERENCES loan_applications(loan_id),
        model_used TEXT,
        prediction TEXT,
        probability FLOAT,
        email_sent BOOLEAN DEFAULT FALSE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """

    print("=" * 60)
    print("CREATING DATABASE TABLES")
    print("=" * 60)
    print()

    connection = get_connection()

    if connection is None:
        print("❌ Cannot create tables — database connection failed.")
        return

    try:
        cursor = connection.cursor()

        # Create loan_applications table
        print("Creating table: loan_applications...")
        cursor.execute(create_applications_table)
        print("  ✅ loan_applications table ready")

        # Create loan_predictions table
        print("Creating table: loan_predictions...")
        cursor.execute(create_predictions_table)
        print("  ✅ loan_predictions table ready")

        # Save changes to database
        connection.commit()

        print()
        print("=" * 60)
        print("✅ ALL TABLES CREATED SUCCESSFULLY!")
        print("=" * 60)

    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        connection.rollback()

    finally:
        cursor.close()
        connection.close()


if __name__ == "__main__":
    create_tables()
