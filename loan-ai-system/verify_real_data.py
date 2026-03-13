import requests
import json

def verify_real_data():
    url = "http://localhost:8000/predict"
    payload = {
        "applicant_name": "REAL DATA VERIFICATION LTD",
        "applicant_email": "verify@enterprise.com",
        "no_of_dependents": 2,
        "education": 1,
        "self_employed": 0,
        "income_annum": 8500000,
        "loan_amount": 2000000,
        "loan_term": 10,
        "cibil_score": 820,
        "residential_assets_value": 5000000,
        "commercial_assets_value": 1500000,
        "luxury_assets_value": 3000000,
        "bank_asset_value": 4000000
    }
    
    print(f"Submitting unique application: {payload['applicant_name']}...")
    try:
        response = requests.post(url, json=payload)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json().get('decision')}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    verify_real_data()
