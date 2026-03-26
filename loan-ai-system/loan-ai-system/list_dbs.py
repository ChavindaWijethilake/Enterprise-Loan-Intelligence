import psycopg2
import os
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.join(BASE_DIR, "..")
ENV_PATH = os.path.join(PROJECT_DIR, ".env")
load_dotenv(ENV_PATH)

def list_dbs():
    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            database="postgres", # Connect to system db
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
        )
        cur = conn.cursor()
        cur.execute("SELECT datname FROM pg_database WHERE datistemplate = false;")
        dbs = cur.fetchall()
        print("Available Databases:")
        for db in dbs:
            print(f" - {db[0]}")
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    list_dbs()
