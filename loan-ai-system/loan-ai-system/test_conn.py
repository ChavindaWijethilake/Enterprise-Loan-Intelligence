import os
import sys

# Add project root to path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.database import get_connection
print(f"Connection Object: {get_connection()}")
