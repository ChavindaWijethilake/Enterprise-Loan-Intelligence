import os
import sys
import unittest

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.db_service import get_connection, release_connection

class TestDB(unittest.TestCase):
    def test_db_connection_pool(self):
        """Verify that the database connection pool is healthy and functional."""
        conn = None
        try:
            conn = get_connection()
            self.assertIsNotNone(conn)
            self.assertFalse(conn.closed)
            
            # Simple query to verify connectivity
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
                result = cur.fetchone()
                self.assertEqual(result[0], 1)
                
        finally:
            if conn:
                release_connection(conn)

    def test_connection_release(self):
        """Verify that connections can be released back to the pool."""
        conn = get_connection()
        release_connection(conn)
        # If we got here, it's a pass
        self.assertTrue(True)

if __name__ == "__main__":
    unittest.main()
