# =============================================================================
# src/feature_engineering.py
# =============================================================================
# PURPOSE: Create new features (columns) from existing data to help ML models
#          make better predictions.
#
# WHAT IS FEATURE ENGINEERING?
#   It's the process of creating new meaningful columns from existing data.
#   For example, instead of just knowing "income" and "loan_amount" separately,
#   we create "loan_to_income" ratio which tells us how big the loan is
#   compared to the applicant's income — a much more useful signal!
#
# WHAT IT DOES:
#   1. Loads the preprocessed dataset
#   2. Creates financial ratio features
#   3. Saves the final dataset ready for ML training
#
# HOW TO RUN:
#   python src/feature_engineering.py
# =============================================================================

import pandas as pd
import numpy as np
import os

# ---------------------------------------------------------------------------
# STEP 1: Set up file paths
# ---------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.join(BASE_DIR, "..")

PREPROCESSED_PATH = os.path.join(PROJECT_DIR, "data", "loan_preprocessed.csv")
FEATURES_PATH = os.path.join(PROJECT_DIR, "data", "loan_features.csv")

# ---------------------------------------------------------------------------
# STEP 2: Load preprocessed data
# ---------------------------------------------------------------------------
print("=" * 60)
print("FEATURE ENGINEERING")
print("=" * 60)
print()
print("Loading preprocessed dataset...")

df = pd.read_csv(PREPROCESSED_PATH)
print(f"  Loaded: {df.shape[0]} rows, {df.shape[1]} columns")
print()

# ---------------------------------------------------------------------------
# STEP 3: Create new features
# ---------------------------------------------------------------------------
print("Creating new financial features...")
print()

# --- Feature 1: Total Assets ---
# Sum of all asset types — tells us the applicant's total wealth
df["total_assets"] = (
    df["residential_assets_value"]
    + df["commercial_assets_value"]
    + df["luxury_assets_value"]
    + df["bank_asset_value"]
)
print("  1. total_assets = residential + commercial + luxury + bank assets")

# --- Feature 2: Loan to Income Ratio ---
# How big is the loan compared to annual income?
# Higher ratio = more risky (borrowing way more than they earn)
# We add a small number (1) to avoid dividing by zero
df["loan_to_income"] = df["loan_amount"] / (df["income_annum"] + 1)
print("  2. loan_to_income = loan_amount / income_annum")

# --- Feature 3: Assets to Loan Ratio ---
# How much collateral (assets) does the applicant have compared to the loan?
# Higher ratio = safer (they have assets to back up the loan)
df["assets_to_loan"] = df["total_assets"] / (df["loan_amount"] + 1)
print("  3. assets_to_loan = total_assets / loan_amount")

# --- Feature 4: Income per Dependent ---
# How much income per person the applicant supports?
# Lower value = more financial burden
df["income_per_dependent"] = df["income_annum"] / (df["no_of_dependents"] + 1)
print("  4. income_per_dependent = income_annum / (dependents + 1)")

# --- Feature 5: Loan Term to Amount Ratio ---
# Spreading a loan over more months means smaller payments
df["loan_term_to_amount"] = df["loan_term"] / (df["loan_amount"] + 1)
print("  5. loan_term_to_amount = loan_term / loan_amount")

print()

# ---------------------------------------------------------------------------
# STEP 4: Summary of new features
# ---------------------------------------------------------------------------
print("Feature engineering summary:")
print(f"  Original columns: {df.shape[1] - 5}")
print(f"  New features added: 5")
print(f"  Total columns: {df.shape[1]}")
print()

# Show statistics of new features
new_features = [
    "total_assets", "loan_to_income", "assets_to_loan",
    "income_per_dependent", "loan_term_to_amount"
]
print("New feature statistics:")
print(df[new_features].describe().round(2))
print()

# ---------------------------------------------------------------------------
# STEP 5: Save the final dataset
# ---------------------------------------------------------------------------
print(f"Saving feature-engineered dataset...")
df.to_csv(FEATURES_PATH, index=False)
print(f"  Saved to: {FEATURES_PATH}")
print()
print("=" * 60)
print("✅ FEATURE ENGINEERING COMPLETE!")
print("=" * 60)
print()
print("Next step: Train ML models")
print("  Command: python src/train_model.py")