# =============================================================================
# src/database.py
# =============================================================================
# PURPOSE: Connect Python to your PostgreSQL database (loan_system).
#
# HOW IT WORKS:
#   - Reads database credentials from the .env file
#   - Creates a connection to PostgreSQL
#   - Provides a reusable function get_connection() for other files to use
#
# HOW TO RUN (to test connection):
#   python src/database.py
# =============================================================================

import psycopg2
import os
from dotenv import load_dotenv

# ---------------------------------------------------------------------------
# Load environment variables from .env file
# ---------------------------------------------------------------------------
# find_dotenv() searches up the directory tree to find .env
# This means it works no matter which folder you run the script from
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.join(BASE_DIR, "..")
ENV_PATH = os.path.join(PROJECT_DIR, ".env")

load_dotenv(ENV_PATH)


def get_connection():
    """
    Create and return a connection to the PostgreSQL database.

    Uses credentials from the .env file:
      - DB_HOST: where the database server is (usually 'localhost')
      - DB_PORT: the port number (usually 5432)
      - DB_NAME: name of your database (loan_system)
      - DB_USER: your PostgreSQL username (usually 'postgres')
      - DB_PASSWORD: your PostgreSQL password

    Returns:
        psycopg2 connection object
    """
    try:
        connection = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
        )
        return connection
    except psycopg2.OperationalError as e:
        print("❌ ERROR: Could not connect to PostgreSQL!")
        print(f"   Details: {e}")
        print()
        print("   Possible fixes:")
        print("   1. Make sure PostgreSQL is running")
        print("   2. Check your .env file has correct credentials")
        print("   3. Make sure database 'loan_system' exists in pgAdmin")
        return None


# ---------------------------------------------------------------------------
# Test the connection when running this file directly
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("=" * 60)
    print("TESTING DATABASE CONNECTION")
    print("=" * 60)
    print()
    print(f"  Host:     {os.getenv('DB_HOST')}")
    print(f"  Port:     {os.getenv('DB_PORT')}")
    print(f"  Database: {os.getenv('DB_NAME')}")
    print(f"  User:     {os.getenv('DB_USER')}")
    print()

    connection = get_connection()

    if connection:
        cursor = connection.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print(f"  ✅ Connected successfully!")
        print(f"  PostgreSQL version: {version[0]}")
        cursor.close()
        connection.close()
    else:
        print("  ❌ Connection failed. See error above.")