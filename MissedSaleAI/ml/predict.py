"""
Inference service for MissedSale AI.
Loads trained models and predicts lost_sale_probability and recovery_probability.
"""

import os
import joblib
import numpy as np
import pandas as pd

try:
    from ml.preprocess import extract_features
except ImportError:
    try:
        from preprocess import extract_features
    except ImportError:
        from MissedSaleAI.ml.preprocess import extract_features

_MODEL_BUNDLE = None

def get_model_bundle():
    global _MODEL_BUNDLE
    if _MODEL_BUNDLE is None:
        model_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "model.pkl")
        if not os.path.exists(model_path):
            from ml.train import train_models
            train_models()
        _MODEL_BUNDLE = joblib.load(model_path)
    return _MODEL_BUNDLE

def predict_lost_sale_and_recovery(features_dict_or_df):
    """
    Given customer activity and behavior features, computes:
    - lost_sale_probability (champion Random Forest)
    - baseline_lost_probability (baseline Logistic Regression)
    - recovery_probability (Recovery Random Forest)
    """
    bundle = get_model_bundle()
    X = extract_features(features_dict_or_df)
    
    # Random Forest champion prediction
    rf_lost = bundle["champion_rf_lost"]
    lost_probs = rf_lost.predict_proba(X)
    lost_prob = float(lost_probs[0][1]) if lost_probs.shape[1] > 1 else float(lost_probs[0][0])
    
    # Baseline Logistic Regression prediction
    scaler = bundle["scaler"]
    lr_lost = bundle["baseline_lr"]
    X_scaled = scaler.transform(X)
    lr_probs = lr_lost.predict_proba(X_scaled)
    baseline_prob = float(lr_probs[0][1]) if lr_probs.shape[1] > 1 else float(lr_probs[0][0])
    
    # Recovery prediction
    rf_recov = bundle["recovery_model"]
    recov_probs = rf_recov.predict_proba(X)
    recov_prob = float(recov_probs[0][1]) if recov_probs.shape[1] > 1 else float(recov_probs[0][0])
    
    return {
        "lost_sale_probability": round(lost_prob, 4),
        "baseline_lost_probability": round(baseline_prob, 4),
        "recovery_probability": round(recov_prob, 4),
        "is_potential_lost_sale": bool(lost_prob >= 0.50)
    }

def get_feature_importances():
    bundle = get_model_bundle()
    rf = bundle["champion_rf_lost"]
    cols = bundle["feature_columns"]
    importances = dict(zip(cols, [round(float(v), 4) for v in rf.feature_importances_]))
    return dict(sorted(importances.items(), key=lambda item: item[1], reverse=True))
