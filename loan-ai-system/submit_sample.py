import requests
import json

url = "http://127.0.0.1:8000/predict"
data = {
    "applicant_name": "John Doe",
    "applicant_email": "johndoe@example.com",
    "no_of_dependents": 2,
    "education": 1,
    "self_employed": 0,
    "income_annum": 3500000,
    "loan_amount": 1500000,
    "loan_term": 12,
    "cibil_score": 780,
    "residential_assets_value": 2000000,
    "commercial_assets_value": 500000,
    "luxury_assets_value": 300000,
    "bank_asset_value": 1500000
}

try:
    response = requests.post(url, json=data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
except Exception as e:
    print(f"Error: {e}")
