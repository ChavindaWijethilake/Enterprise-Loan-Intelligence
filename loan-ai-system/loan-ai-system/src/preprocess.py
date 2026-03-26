# =============================================================================
# src/preprocess.py
# =============================================================================
# PURPOSE: Clean the raw loan dataset and prepare it for machine learning.
#
# WHAT IT DOES:
#   1. Loads the raw CSV file (loan_dataset.csv)
#   2. Strips whitespace from text columns (the CSV has extra spaces)
#   3. Fills in any missing values
#   4. Converts text categories to numbers (encoding)
#   5. Converts the target variable (Approved/Rejected) to 1/0
#   6. Saves the cleaned dataset as loan_preprocessed.csv
#
# HOW TO RUN:
#   python src/preprocess.py
# =============================================================================

import pandas as pd
import numpy as np
import os

# ---------------------------------------------------------------------------
# STEP 1: Set up file paths
# ---------------------------------------------------------------------------
# os.path.dirname(__file__) gives us the folder where THIS script lives (src/)
# os.path.join(...) builds a path that works on any operating system
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.join(BASE_DIR, "..")  # Go up one level to loan-ai-system/

RAW_DATA_PATH = os.path.join(PROJECT_DIR, "data", "loan_dataset.csv")
CLEAN_DATA_PATH = os.path.join(PROJECT_DIR, "data", "loan_preprocessed.csv")

# ---------------------------------------------------------------------------
# STEP 2: Load the raw dataset
# ---------------------------------------------------------------------------
print("=" * 60)
print("STEP 1: Loading raw dataset...")
print("=" * 60)

df = pd.read_csv(RAW_DATA_PATH)

print(f"  Dataset loaded: {df.shape[0]} rows, {df.shape[1]} columns")
print(f"  Columns: {list(df.columns)}")
print()

# ---------------------------------------------------------------------------
# STEP 3: Strip whitespace from column names and string values
# ---------------------------------------------------------------------------
# The CSV has extra spaces in column names and values like " Graduate"
# We need to remove those spaces so our code works correctly
print("STEP 2: Cleaning whitespace from text values...")

# Clean column names (remove leading/trailing spaces)
df.columns = df.columns.str.strip()

# Clean string columns (remove leading/trailing spaces from values)
for col in df.select_dtypes(include=["object"]).columns:
    df[col] = df[col].str.strip()

print(f"  Column names after cleaning: {list(df.columns)}")
print(f"  Unique education values: {df['education'].unique()}")
print(f"  Unique self_employed values: {df['self_employed'].unique()}")
print(f"  Unique loan_status values: {df['loan_status'].unique()}")
print()

# ---------------------------------------------------------------------------
# STEP 4: Check for missing values
# ---------------------------------------------------------------------------
print("STEP 3: Checking for missing values...")

missing = df.isnull().sum()
missing_cols = missing[missing > 0]

if len(missing_cols) > 0:
    print(f"  Found missing values in:")
    for col, count in missing_cols.items():
        print(f"    - {col}: {count} missing")
else:
    print("  No missing values found! ✓")
print()

# ---------------------------------------------------------------------------
# STEP 5: Fill missing values (just in case)
# ---------------------------------------------------------------------------
# Even if there are no missing values now, this protects against future data
print("STEP 4: Filling any missing values...")

# For numerical columns: fill with the median (middle value)
# Median is better than mean because it's not affected by extreme values
numerical_cols = [
    "income_annum", "loan_amount", "loan_term", "cibil_score",
    "residential_assets_value", "commercial_assets_value",
    "luxury_assets_value", "bank_asset_value"
]
for col in numerical_cols:
    if col in df.columns:
        df[col] = df[col].fillna(df[col].median())

# For dependents: fill with 0
if "no_of_dependents" in df.columns:
    df["no_of_dependents"] = df["no_of_dependents"].fillna(0)

# For text columns: fill with the most common value (mode)
if "education" in df.columns:
    df["education"] = df["education"].fillna("Not Graduate")
if "self_employed" in df.columns:
    df["self_employed"] = df["self_employed"].fillna("No")

print("  Missing values filled ✓")
print()

# ---------------------------------------------------------------------------
# STEP 6: Encode categorical variables (convert text → numbers)
# ---------------------------------------------------------------------------
# Machine learning models can only work with numbers, not text.
# So we convert:
#   "Graduate"     → 1
#   "Not Graduate" → 0
#   "Yes"          → 1
#   "No"           → 0
print("STEP 5: Encoding categorical variables (text → numbers)...")

df["education"] = df["education"].map({"Graduate": 1, "Not Graduate": 0})
df["self_employed"] = df["self_employed"].map({"Yes": 1, "No": 0})

print(f"  education: Graduate=1, Not Graduate=0")
print(f"  self_employed: Yes=1, No=0")
print()

# ---------------------------------------------------------------------------
# STEP 7: Encode the target variable
# ---------------------------------------------------------------------------
# The target variable is what we want the ML model to predict.
# We convert:
#   "Approved" → 1
#   "Rejected" → 0
print("STEP 6: Encoding target variable (loan_status)...")

df["loan_status"] = df["loan_status"].map({"Approved": 1, "Rejected": 0})

approved_count = df["loan_status"].sum()
rejected_count = len(df) - approved_count
print(f"  Approved: {int(approved_count)} loans")
print(f"  Rejected: {int(rejected_count)} loans")
print(f"  Approval rate: {approved_count / len(df) * 100:.1f}%")
print()

# ---------------------------------------------------------------------------
# STEP 8: Final check — make sure no NaN values remain
# ---------------------------------------------------------------------------
print("STEP 7: Final data quality check...")

remaining_nan = df.isnull().sum().sum()
if remaining_nan > 0:
    print(f"  ⚠ WARNING: {remaining_nan} NaN values still remain!")
    # Drop rows with NaN as a last resort
    df = df.dropna()
    print(f"  Dropped rows with NaN. New shape: {df.shape}")
else:
    print(f"  No NaN values remain ✓")
    print(f"  Final shape: {df.shape[0]} rows, {df.shape[1]} columns")
print()

# ---------------------------------------------------------------------------
# STEP 9: Save the preprocessed dataset
# ---------------------------------------------------------------------------
print("STEP 8: Saving preprocessed dataset...")

df.to_csv(CLEAN_DATA_PATH, index=False)

print(f"  Saved to: {CLEAN_DATA_PATH}")
print()
print("=" * 60)
print("✅ PREPROCESSING COMPLETE!")
print("=" * 60)
print()
print("Next step: Run feature engineering")
print("  Command: python src/feature_engineering.py")