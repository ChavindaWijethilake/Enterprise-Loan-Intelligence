# =============================================================================
# src/train_model.py
# =============================================================================
# PURPOSE: Train two Machine Learning models and compare their performance.
#
# MODELS TRAINED:
#   1. Random Forest — an ensemble of many decision trees
#   2. XGBoost (Gradient Boosting) — builds trees sequentially, each one
#      learning from the mistakes of the previous one
#
# DATA SPLIT:
#   80% Training  — model learns from this data
#   10% Validation — used to tune/check model during development
#   10% Testing    — final unseen test (simulates real-world performance)
#
# METRICS EXPLAINED:
#   - Accuracy:  % of all predictions that are correct
#   - Precision: of all "Approved" predictions, how many were actually approved?
#   - Recall:    of all actually approved loans, how many did the model catch?
#   - ROC-AUC:   overall ability to distinguish approved vs rejected (0.5 = random, 1.0 = perfect)
#
# HOW TO RUN:
#   python src/train_model.py
# =============================================================================

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    roc_auc_score,
    classification_report,
    confusion_matrix,
)
import xgboost as xgb
import joblib
import os

# ---------------------------------------------------------------------------
# STEP 1: Set up file paths
# ---------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.join(BASE_DIR, "..")

FEATURES_PATH = os.path.join(PROJECT_DIR, "data", "loan_features.csv")
RF_MODEL_PATH = os.path.join(PROJECT_DIR, "models", "rf_model.pkl")
XGB_MODEL_PATH = os.path.join(PROJECT_DIR, "models", "xgb_model.pkl")

# ---------------------------------------------------------------------------
# STEP 2: Load the feature-engineered dataset
# ---------------------------------------------------------------------------
print("=" * 60)
print("ML MODEL TRAINING")
print("=" * 60)
print()
print("Loading feature-engineered dataset...")

df = pd.read_csv(FEATURES_PATH)
print(f"  Dataset: {df.shape[0]} rows, {df.shape[1]} columns")
print()

# ---------------------------------------------------------------------------
# STEP 3: Separate features (X) and target (y)
# ---------------------------------------------------------------------------
# Features = input columns the model uses to make predictions
# Target = the column we want to predict (loan_status)
print("Separating features and target variable...")

# Drop columns that should NOT be used as features:
#   - loan_id: just an identifier, not useful for prediction
#   - loan_status: this is our TARGET, not a feature!
columns_to_drop = ["loan_status", "loan_id"]
X = df.drop(columns_to_drop, axis=1, errors="ignore")
y = df["loan_status"]

print(f"  Features (X): {X.shape[1]} columns")
print(f"  Feature names: {list(X.columns)}")
print(f"  Target (y): {y.shape[0]} values")
print(f"  Target distribution: Approved={int(y.sum())}, Rejected={int(len(y) - y.sum())}")
print()

# ---------------------------------------------------------------------------
# STEP 4: Split data into Training / Validation / Testing
# ---------------------------------------------------------------------------
# Split 1: 80% training, 20% temporary
# Split 2: Split the 20% temporary into 10% validation + 10% testing
print("Splitting dataset: 80% Train / 10% Validation / 10% Test...")

X_train, X_temp, y_train, y_temp = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)
X_val, X_test, y_val, y_test = train_test_split(
    X_temp, y_temp, test_size=0.5, random_state=42, stratify=y_temp
)

print(f"  Training:   {X_train.shape[0]} rows ({X_train.shape[0]/len(X)*100:.0f}%)")
print(f"  Validation: {X_val.shape[0]} rows ({X_val.shape[0]/len(X)*100:.0f}%)")
print(f"  Testing:    {X_test.shape[0]} rows ({X_test.shape[0]/len(X)*100:.0f}%)")
print()

# ---------------------------------------------------------------------------
# STEP 5: Train Random Forest
# ---------------------------------------------------------------------------
print("=" * 60)
print("TRAINING MODEL 1: Random Forest")
print("=" * 60)
print()

rf_model = RandomForestClassifier(
    n_estimators=200,      # Number of trees in the forest
    max_depth=10,          # Maximum depth of each tree
    min_samples_split=5,   # Minimum samples to split a node
    random_state=42,       # Reproducibility
    n_jobs=-1,             # Use all CPU cores for speed
)

print("Training Random Forest (200 trees, max_depth=10)...")
rf_model.fit(X_train, y_train)
print("  Training complete ✓")
print()

# Evaluate Random Forest
rf_val_pred = rf_model.predict(X_val)
rf_val_prob = rf_model.predict_proba(X_val)[:, 1]

rf_accuracy = accuracy_score(y_val, rf_val_pred)
rf_precision = precision_score(y_val, rf_val_pred)
rf_recall = recall_score(y_val, rf_val_pred)
rf_auc = roc_auc_score(y_val, rf_val_prob)

print("Random Forest — Validation Results:")
print(f"  Accuracy:  {rf_accuracy:.4f} ({rf_accuracy*100:.1f}%)")
print(f"  Precision: {rf_precision:.4f}")
print(f"  Recall:    {rf_recall:.4f}")
print(f"  ROC-AUC:   {rf_auc:.4f}")
print()

# ---------------------------------------------------------------------------
# STEP 6: Train XGBoost (Gradient Boosting)
# ---------------------------------------------------------------------------
print("=" * 60)
print("TRAINING MODEL 2: XGBoost (Gradient Boosting)")
print("=" * 60)
print()

xgb_model = xgb.XGBClassifier(
    n_estimators=300,      # Number of boosting rounds
    learning_rate=0.05,    # Step size for each update (smaller = more careful)
    max_depth=6,           # Maximum depth of each tree
    eval_metric="logloss", # Loss function for binary classification
    random_state=42,
    n_jobs=-1,
)

print("Training XGBoost (300 rounds, learning_rate=0.05, max_depth=6)...")
xgb_model.fit(X_train, y_train)
print("  Training complete ✓")
print()

# Evaluate XGBoost
xgb_val_pred = xgb_model.predict(X_val)
xgb_val_prob = xgb_model.predict_proba(X_val)[:, 1]

xgb_accuracy = accuracy_score(y_val, xgb_val_pred)
xgb_precision = precision_score(y_val, xgb_val_pred)
xgb_recall = recall_score(y_val, xgb_val_pred)
xgb_auc = roc_auc_score(y_val, xgb_val_prob)

print("XGBoost — Validation Results:")
print(f"  Accuracy:  {xgb_accuracy:.4f} ({xgb_accuracy*100:.1f}%)")
print(f"  Precision: {xgb_precision:.4f}")
print(f"  Recall:    {xgb_recall:.4f}")
print(f"  ROC-AUC:   {xgb_auc:.4f}")
print()

# ---------------------------------------------------------------------------
# STEP 7: Compare Models
# ---------------------------------------------------------------------------
print("=" * 60)
print("MODEL COMPARISON")
print("=" * 60)
print()
print(f"  {'Metric':<12} {'Random Forest':>15} {'XGBoost':>15} {'Winner':>10}")
print(f"  {'-'*12} {'-'*15} {'-'*15} {'-'*10}")
print(f"  {'Accuracy':<12} {rf_accuracy:>15.4f} {xgb_accuracy:>15.4f} {'RF' if rf_accuracy > xgb_accuracy else 'XGBoost':>10}")
print(f"  {'Precision':<12} {rf_precision:>15.4f} {xgb_precision:>15.4f} {'RF' if rf_precision > xgb_precision else 'XGBoost':>10}")
print(f"  {'Recall':<12} {rf_recall:>15.4f} {xgb_recall:>15.4f} {'RF' if rf_recall > xgb_recall else 'XGBoost':>10}")
print(f"  {'ROC-AUC':<12} {rf_auc:>15.4f} {xgb_auc:>15.4f} {'RF' if rf_auc > xgb_auc else 'XGBoost':>10}")
print()

# Determine best model
if xgb_auc >= rf_auc:
    print("  🏆 Recommended model: XGBoost (better ROC-AUC)")
else:
    print("  🏆 Recommended model: Random Forest (better ROC-AUC)")
print()

# ---------------------------------------------------------------------------
# STEP 8: Test Set Evaluation (Final Performance)
# ---------------------------------------------------------------------------
print("=" * 60)
print("FINAL TEST SET EVALUATION (Unseen Data)")
print("=" * 60)
print()

# Test Random Forest
rf_test_pred = rf_model.predict(X_test)
rf_test_accuracy = accuracy_score(y_test, rf_test_pred)
print(f"  Random Forest test accuracy: {rf_test_accuracy:.4f} ({rf_test_accuracy*100:.1f}%)")

# Test XGBoost
xgb_test_pred = xgb_model.predict(X_test)
xgb_test_accuracy = accuracy_score(y_test, xgb_test_pred)
print(f"  XGBoost test accuracy:       {xgb_test_accuracy:.4f} ({xgb_test_accuracy*100:.1f}%)")
print()

# Classification Report for XGBoost (the recommended model)
print("XGBoost — Detailed Classification Report (Test Set):")
print(classification_report(y_test, xgb_test_pred, target_names=["Rejected", "Approved"]))

# ---------------------------------------------------------------------------
# STEP 9: Feature Importance
# ---------------------------------------------------------------------------
print("=" * 60)
print("TOP 10 MOST IMPORTANT FEATURES (XGBoost)")
print("=" * 60)
print()

importance = pd.Series(xgb_model.feature_importances_, index=X.columns)
importance = importance.sort_values(ascending=False)

for i, (feature, score) in enumerate(importance.head(10).items()):
    bar = "█" * int(score * 50)
    print(f"  {i+1:>2}. {feature:<25} {score:.4f} {bar}")
print()

# ---------------------------------------------------------------------------
# STEP 10: Save Models
# ---------------------------------------------------------------------------
print("Saving trained models...")

joblib.dump(rf_model, RF_MODEL_PATH)
print(f"  ✅ Random Forest saved: {RF_MODEL_PATH}")

joblib.dump(xgb_model, XGB_MODEL_PATH)
print(f"  ✅ XGBoost saved: {XGB_MODEL_PATH}")

print()
print("=" * 60)
print("✅ MODEL TRAINING COMPLETE!")
print("=" * 60)
print()
print("Next step: Test a prediction")
print("  Command: python src/predict.py")