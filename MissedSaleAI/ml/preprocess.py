"""
Preprocessing pipeline for MissedSale AI.
Handles feature scaling, categorical mappings, and dataset preparation.
"""

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler

FEATURE_COLUMNS = [
    "number_of_visits",
    "product_views",
    "cart_additions",
    "checkout_started",
    "previous_purchases",
    "average_order_value",
    "days_since_last_activity",
    "customer_value_score",
    "discount_used",
    "email_engagement",
    "session_duration"
]

CUSTOMER_VALUE_MAP = {
    "low": 1.0,
    "medium": 2.0,
    "high": 3.0,
    1: 1.0,
    2: 2.0,
    3: 3.0
}

def extract_features(df_or_dict):
    """
    Standardize raw input (DataFrame or dict) into clean numeric feature DataFrame.
    """
    if isinstance(df_or_dict, dict):
        df = pd.DataFrame([df_or_dict])
    else:
        df = df_or_dict.copy()
        
    # Map customer_value string to numeric score
    if "customer_value_score" not in df.columns:
        if "customer_value" in df.columns:
            df["customer_value_score"] = df["customer_value"].astype(str).str.lower().map(CUSTOMER_VALUE_MAP).fillna(1.0)
        else:
            df["customer_value_score"] = 1.0

    # Ensure all required columns exist with defaults
    defaults = {
        "number_of_visits": 1,
        "product_views": 1,
        "cart_additions": 0,
        "checkout_started": 0,
        "previous_purchases": 0,
        "average_order_value": 50.0,
        "days_since_last_activity": 1,
        "customer_value_score": 1.0,
        "discount_used": 0,
        "email_engagement": 0.3,
        "session_duration": 60.0
    }
    
    for col, default_val in defaults.items():
        if col not in df.columns:
            df[col] = default_val
            
    return df[FEATURE_COLUMNS].astype(float)
