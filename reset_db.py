import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def reset_db():
    try:
        # Connect to system db
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            database="postgres",
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
        )
        conn.autocommit = True
        cur = conn.cursor()
        
        # Drop and create
        print("Dropping database 'loan_system'...")
        cur.execute("DROP DATABASE IF EXISTS loan_system;")
        print("Creating database 'loan_system'...")
        cur.execute("CREATE DATABASE loan_system;")
        
        cur.close()
        conn.close()
        print("✅ Database reset successfully!")
    except Exception as e:
        print(f"❌ Reset failed: {e}")

if __name__ == "__main__":
    reset_db()
