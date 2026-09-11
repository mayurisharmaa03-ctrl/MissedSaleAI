"""
Dataset generator for MissedSale AI.
Generates realistic customer behavior and sales data for training ML models:
- Lost-Sale Detection Model (Classifier)
- Recovery Opportunity Predictor (Classifier/Regressor)
"""

import os
import numpy as np
import pandas as pd

def generate_dataset(n_samples=1200, seed=42):
    np.random.seed(seed)
    
    customer_ids = [f"CUST-{1000 + i}" for i in range(n_samples)]
    number_of_visits = np.random.negative_binomial(4, 0.4, n_samples) + 1
    product_views = number_of_visits * np.random.randint(1, 5, n_samples) + np.random.poisson(2, n_samples)
    cart_additions = np.minimum(product_views, np.random.binomial(product_views, 0.35))
    
    # checkout started depends on cart additions
    checkout_prob = np.where(cart_additions > 0, 0.70, 0.05)
    checkout_started = np.random.binomial(1, checkout_prob)
    
    previous_purchases = np.random.negative_binomial(2, 0.5, n_samples)
    avg_order_val = np.round(np.random.gamma(shape=5.0, scale=30.0, size=n_samples), 2)
    days_since_last_activity = np.random.exponential(scale=6.0, size=n_samples).astype(int) + 1
    
    # customer value category and score
    # base customer value on previous purchases and avg order value
    clv_score = previous_purchases * avg_order_val
    customer_value_tier = []
    for score in clv_score:
        if score > 500:
            customer_value_tier.append("High")
        elif score > 150:
            customer_value_tier.append("Medium")
        else:
            customer_value_tier.append("Low")
            
    discount_used = np.random.binomial(1, 0.38, n_samples)
    email_engagement = np.round(np.clip(np.random.beta(2, 3, n_samples), 0.0, 1.0), 2)
    session_duration = np.round(product_views * np.random.uniform(45, 120, n_samples) + np.random.uniform(30, 180, n_samples), 1)
    
    # Realistic logic for potential_lost_sale:
    # High if cart additions > 0 and checkout started == 1 or visits high with cart additions but no purchase
    # Calculate log-odds of abandoning cart with intent
    lost_logit = (
        0.8 * (cart_additions > 0) +
        1.5 * checkout_started +
        0.05 * days_since_last_activity +
        0.002 * avg_order_val -
        0.4 * (previous_purchases > 3) -
        0.8 # baseline offset
    )
    lost_prob = 1 / (1 + np.exp(-lost_logit))
    potential_lost_sale = np.random.binomial(1, np.clip(lost_prob, 0.05, 0.95))
    
    # For recovery: high if customer has previous purchases, high email engagement,
    # recent activity (low days_since_last_activity), and discount affinity
    recov_logit = (
        1.2 * (previous_purchases > 0) +
        2.0 * email_engagement -
        0.12 * days_since_last_activity +
        0.6 * discount_used +
        0.5 * (np.array(customer_value_tier) == "High") -
        0.4 * (np.array(customer_value_tier) == "Low")
    )
    recov_prob = 1 / (1 + np.exp(-recov_logit))
    # actual recovered target if engaged (for ML evaluation)
    recovered = np.where(potential_lost_sale == 1, np.random.binomial(1, np.clip(recov_prob, 0.1, 0.9)), 0)
    
    df = pd.DataFrame({
        "customer_id": customer_ids,
        "number_of_visits": number_of_visits,
        "product_views": product_views,
        "cart_additions": cart_additions,
        "checkout_started": checkout_started,
        "previous_purchases": previous_purchases,
        "average_order_value": avg_order_val,
        "days_since_last_activity": days_since_last_activity,
        "customer_value": customer_value_tier,
        "discount_used": discount_used,
        "email_engagement": email_engagement,
        "session_duration": session_duration,
        "potential_lost_sale": potential_lost_sale,
        "recovered": recovered,
        "recovery_probability_true": np.round(recov_prob, 3)
    })
    
    return df

if __name__ == "__main__":
    out_dir = os.path.dirname(os.path.abspath(__file__))
    os.makedirs(out_dir, exist_ok=True)
    csv_path = os.path.join(out_dir, "sample_sales_data.csv")
    df = generate_dataset()
    df.to_csv(csv_path, index=False)
    print(f"Generated {len(df)} samples at {csv_path}")
    print("Class distribution (potential_lost_sale):")
    print(df['potential_lost_sale'].value_counts(normalize=True))
