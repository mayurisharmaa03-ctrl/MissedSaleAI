"""
Model training script for MissedSale AI.
Trains both Logistic Regression (baseline) and Random Forest (champion)
for Lost Sale detection and Recovery Probability prediction.
Calculates and saves authentic evaluation metrics (Accuracy, Precision, Recall, F1, Confusion Matrix).
"""

import os
import json
import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
from sklearn.preprocessing import StandardScaler

try:
    from ml.preprocess import extract_features, FEATURE_COLUMNS
except ImportError:
    try:
        from preprocess import extract_features, FEATURE_COLUMNS
    except ImportError:
        from MissedSaleAI.ml.preprocess import extract_features, FEATURE_COLUMNS

def train_models(data_path=None, model_dir=None):
    if data_path is None:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        data_path = os.path.join(base_dir, "data", "sample_sales_data.csv")
        
    if model_dir is None:
        model_dir = os.path.dirname(os.path.abspath(__file__))
        
    print(f"Loading data from: {data_path}")
    df = pd.read_csv(data_path)
    
    # 1. Prepare Features & Targets
    X = extract_features(df)
    y_lost = df["potential_lost_sale"].astype(int)
    # Target for recovery: whether the abandoned sale was recovered
    y_recovery = df["recovered"].astype(int)
    
    # Train / Test Split
    X_train, X_test, y_lost_train, y_lost_test, y_recov_train, y_recov_test = train_test_split(
        X, y_lost, y_recovery, test_size=0.25, random_state=42, stratify=y_lost
    )
    
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # ==========================================
    # 2. Train Lost Sale Detection Models
    # ==========================================
    # Baseline: Logistic Regression
    baseline_lr = LogisticRegression(max_iter=1000, random_state=42)
    baseline_lr.fit(X_train_scaled, y_lost_train)
    y_lost_pred_lr = baseline_lr.predict(X_test_scaled)
    
    # Champion: Random Forest Classifier
    rf_lost = RandomForestClassifier(n_estimators=100, max_depth=8, random_state=42)
    rf_lost.fit(X_train, y_lost_train)
    y_lost_pred_rf = rf_lost.predict(X_test)
    
    # ==========================================
    # 3. Train Recovery Probability Model
    # ==========================================
    rf_recovery = RandomForestClassifier(n_estimators=100, max_depth=6, random_state=42)
    rf_recovery.fit(X_train, y_recov_train)
    y_recov_pred_rf = rf_recovery.predict(X_test)
    
    # ==========================================
    # 4. Authentic Metrics Calculation
    # ==========================================
    cm_baseline = confusion_matrix(y_lost_test, y_lost_pred_lr).tolist()
    cm_champion = confusion_matrix(y_lost_test, y_lost_pred_rf).tolist()
    cm_recovery = confusion_matrix(y_recov_test, y_recov_pred_rf).tolist()
    
    feature_importances = dict(zip(FEATURE_COLUMNS, [round(float(v), 4) for v in rf_lost.feature_importances_]))
    # Sort feature importances
    feature_importances = dict(sorted(feature_importances.items(), key=lambda item: item[1], reverse=True))
    
    metrics = {
        "dataset_samples": len(df),
        "test_samples": len(X_test),
        "baseline_logistic_regression": {
            "name": "Logistic Regression (Baseline)",
            "accuracy": round(float(accuracy_score(y_lost_test, y_lost_pred_lr)), 4),
            "precision": round(float(precision_score(y_lost_test, y_lost_pred_lr, zero_division=0)), 4),
            "recall": round(float(recall_score(y_lost_test, y_lost_pred_lr, zero_division=0)), 4),
            "f1_score": round(float(f1_score(y_lost_test, y_lost_pred_lr, zero_division=0)), 4),
            "confusion_matrix": cm_baseline
        },
        "champion_random_forest": {
            "name": "Random Forest (Champion)",
            "accuracy": round(float(accuracy_score(y_lost_test, y_lost_pred_rf)), 4),
            "precision": round(float(precision_score(y_lost_test, y_lost_pred_rf, zero_division=0)), 4),
            "recall": round(float(recall_score(y_lost_test, y_lost_pred_rf, zero_division=0)), 4),
            "f1_score": round(float(f1_score(y_lost_test, y_lost_pred_rf, zero_division=0)), 4),
            "confusion_matrix": cm_champion
        },
        "recovery_model": {
            "name": "Recovery Predictor (Random Forest)",
            "accuracy": round(float(accuracy_score(y_recov_test, y_recov_pred_rf)), 4),
            "precision": round(float(precision_score(y_recov_test, y_recov_pred_rf, zero_division=0)), 4),
            "recall": round(float(recall_score(y_recov_test, y_recov_pred_rf, zero_division=0)), 4),
            "f1_score": round(float(f1_score(y_recov_test, y_recov_pred_rf, zero_division=0)), 4),
            "confusion_matrix": cm_recovery
        },
        "feature_importances": feature_importances
    }
    
    # ==========================================
    # 5. Persist Models & Metrics
    # ==========================================
    bundle = {
        "scaler": scaler,
        "baseline_lr": baseline_lr,
        "champion_rf_lost": rf_lost,
        "recovery_model": rf_recovery,
        "feature_columns": FEATURE_COLUMNS
    }
    
    model_path = os.path.join(model_dir, "model.pkl")
    metrics_path = os.path.join(model_dir, "metrics.json")
    
    joblib.dump(bundle, model_path)
    with open(metrics_path, "w") as f:
        json.dump(metrics, f, indent=2)
        
    print(f"Models successfully serialized to: {model_path}")
    print(f"Metrics saved to: {metrics_path}")
    print("\n--- Model Training Results ---")
    print(f"Random Forest Lost-Sale Accuracy: {metrics['champion_random_forest']['accuracy'] * 100:.2f}%")
    print(f"Random Forest Lost-Sale F1 Score: {metrics['champion_random_forest']['f1_score']:.4f}")
    print(f"Baseline Logistic Regression Accuracy: {metrics['baseline_logistic_regression']['accuracy'] * 100:.2f}%")
    print(f"Recovery Model F1 Score: {metrics['recovery_model']['f1_score']:.4f}")
    print("Top Feature Importances:")
    for feat, imp in list(feature_importances.items())[:5]:
        print(f"  - {feat}: {imp:.4f}")
        
    return metrics

if __name__ == "__main__":
    train_models()
