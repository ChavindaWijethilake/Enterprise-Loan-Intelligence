import os
import sys
import unittest

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import requests

class TestAPI(unittest.TestCase):
    BASE_URL = "http://localhost:8000"

    def test_health_root(self):
        """Verify the API root/health endpoint."""
        try:
            response = requests.get(f"{self.BASE_URL}/")
            self.assertEqual(response.status_code, 200)
        except requests.exceptions.ConnectionError:
            self.fail("API server is not running on localhost:8000")

    def test_loan_application_validation(self):
        """Verify that invalid loan applications are rejected by the API."""
        invalid_payload = {
            "applicant_name": "Test User",
        }
        response = requests.post(f"{self.BASE_URL}/api/apply", json=invalid_payload)
        # FastAPI returns 422 for validation errors
        self.assertEqual(response.status_code, 422)

    def test_loan_submission_flow(self):
        """Verify a successful loan submission through the API."""
        valid_payload = {
            "applicant_name": "Test End-to-End",
            "applicant_email": "e2e@example.com",
            "no_of_dependents": 0,
            "education": 1,
            "self_employed": 1,
            "income_annum": 6000000,
            "loan_amount": 12000000,
            "loan_term": 7,
            "cibil_score": 820,
            "residential_assets_value": 3000000,
            "commercial_assets_value": 0,
            "luxury_assets_value": 2000000,
            "bank_asset_value": 1000000,
        }
        
        response = requests.post(f"{self.BASE_URL}/api/apply", json=valid_payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("loan_id", data)
        self.assertIn("message", data)
        self.assertEqual(data["message"], "Application submitted successfully")

if __name__ == "__main__":
    unittest.main()
