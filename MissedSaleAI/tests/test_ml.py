"""
Tests for Machine Learning Subsystem (Preprocessing, Inference, Feature Importances).
"""

from ml.preprocess import extract_features, FEATURE_COLUMNS
from ml.predict import predict_lost_sale_and_recovery, get_feature_importances

def test_feature_extraction():
    raw_dict = {
        "number_of_visits": 5,
        "product_views": 8,
        "cart_additions": 3,
        "checkout_started": 1,
        "previous_purchases": 2,
        "average_order_value": 120.0,
        "days_since_last_activity": 2,
        "customer_value": "High",
        "discount_used": 1,
        "email_engagement": 0.7
    }
    df = extract_features(raw_dict)
    assert len(df) == 1
    assert list(df.columns) == FEATURE_COLUMNS
    assert df["customer_value_score"].iloc[0] == 3.0  # High mapped to 3.0

def test_ml_prediction_inference():
    raw_dict = {
        "number_of_visits": 4,
        "product_views": 6,
        "cart_additions": 2,
        "checkout_started": 1,
        "previous_purchases": 3,
        "average_order_value": 150.0,
        "days_since_last_activity": 1,
        "customer_value": "High",
        "discount_used": 1,
        "email_engagement": 0.8
    }
    result = predict_lost_sale_and_recovery(raw_dict)
    
    assert "lost_sale_probability" in result
    assert "baseline_lost_probability" in result
    assert "recovery_probability" in result
    assert "is_potential_lost_sale" in result
    
    # Check probability bounds
    assert 0.0 <= result["lost_sale_probability"] <= 1.0
    assert 0.0 <= result["baseline_lost_probability"] <= 1.0
    assert 0.0 <= result["recovery_probability"] <= 1.0
    assert isinstance(result["is_potential_lost_sale"], bool)

def test_feature_importances():
    importances = get_feature_importances()
    assert isinstance(importances, dict)
    assert len(importances) == len(FEATURE_COLUMNS)
    assert round(sum(importances.values()), 1) == 1.0
