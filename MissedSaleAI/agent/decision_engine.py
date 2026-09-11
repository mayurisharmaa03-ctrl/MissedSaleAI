"""
Autonomous Agent Decision Engine for MissedSale AI.
Evaluates multi-factor signals (intent, value, recency, ML probabilities, fatigue)
to make auditable recovery decisions with human-readable rationales.
"""

from config import Config

class DecisionEngine:
    def __init__(self, lost_threshold=None, recov_high=None, recov_med=None, max_attempts=None):
        self.lost_threshold = lost_threshold or Config.LOST_SALE_THRESHOLD
        self.recov_high = recov_high or Config.RECOVERY_THRESHOLD_HIGH
        self.recov_med = recov_med or Config.RECOVERY_THRESHOLD_MED
        self.max_attempts = max_attempts or Config.MAX_OUTREACH_ATTEMPTS
        
    def evaluate(self, customer, behavior, product, lost_prob, recovery_prob, fatigue_reached=False, prior_attempts=0):
        """
        Executes multi-factor reasoning:
        1. Checks for fatigue/spam prevention
        2. Assesses purchase intent (cart additions, checkout started, duration)
        3. Assesses customer value and order amount
        4. Applies ML thresholds
        5. Determines priority & action
        6. Formulates transparent explanation text
        """
        reasons = []
        is_opportunity = False
        action = "MONITOR"
        priority = "LOW"
        
        # 1. Opt-out and Fatigue Check
        if getattr(customer, "email_opt_out", False):
            reasons.append("Customer has active email opt-out / unsubscribe status.")
            return {
                "is_opportunity": False,
                "priority": "LOW",
                "recommended_action": "OPT_OUT_SUPPRESSION",
                "reasoning": " ".join(reasons) + " Communication strictly suppressed in adherence with email compliance and user preferences.",
                "should_send_email": False,
                "should_create_crm_opp": True
            }

        if fatigue_reached:
            reasons.append(f"Customer has already received {prior_attempts} recovery outreach attempts (max fatigue limit reached).")
            return {
                "is_opportunity": False,
                "priority": "LOW",
                "recommended_action": "HALT_FATIGUE",
                "reasoning": " ".join(reasons) + " To protect customer trust and avoid annoyance, further automated messages are halted. Manual sales manager review is recommended.",
                "should_send_email": False,
                "should_create_crm_opp": True
            }
            
        # 2. Intent Assessment
        has_checkout = bool(behavior and behavior.checkout_started)
        has_cart = bool(behavior and behavior.cart_added > 0)
        has_views = bool(behavior and behavior.product_views > 0)
        
        if has_checkout:
            reasons.append("Customer initiated checkout but did not finalize payment, indicating very high purchase intent.")
        elif has_cart:
            reasons.append(f"Customer added {behavior.cart_added} item(s) to shopping cart without proceeding to checkout.")
        elif has_views:
            reasons.append(f"Customer browsed {behavior.product_views} product pages recently.")
        else:
            reasons.append("Low direct shopping session activity observed.")
            
        # 3. Customer Value & Past Orders
        past_orders = customer.total_purchases()
        cust_val = customer.customer_value
        product_price = product.price if product else 0.0
        
        if cust_val == "High" or past_orders >= 3:
            reasons.append(f"Customer is a VIP/Repeat buyer ({past_orders} past orders, Tier: {cust_val}).")
        elif cust_val == "Medium":
            reasons.append(f"Customer has moderate lifetime value ({past_orders} past orders).")
        else:
            reasons.append("Customer is new or low-frequency buyer.")
            
        # 4. Lost Sale Probability Evaluation
        if (has_checkout and not (behavior and behavior.purchased)) or (has_cart and not (behavior and behavior.purchased)) or lost_prob >= self.lost_threshold:
            is_opportunity = True
            reasons.append(f"ML Lost-Sale Probability is {lost_prob * 100:.1f}%. Active recovery opportunity identified.")
        else:
            reasons.append(f"ML Lost-Sale Probability is {lost_prob * 100:.1f}% (below trigger threshold {self.lost_threshold * 100:.0f}%).")
            
        # 5. Recovery Probability & Action Selection
        reasons.append(f"ML Recovery Potential is estimated at {recovery_prob * 100:.1f}%.")
        
        if is_opportunity:
            if recovery_prob >= self.recov_high:
                priority = "HIGH"
                action = "SEND_PERSONALIZED_EMAIL"
                should_email = True
                reasons.append(f"Recovery probability >= {self.recov_high * 100:.0f}%: HIGH PRIORITY. Create CRM opportunity, formulate personalized recovery email, send via Resend, and monitor response.")
            elif recovery_prob >= self.recov_med:
                priority = "MEDIUM"
                action = "CRM_FOLLOW_UP"
                should_email = False
                reasons.append(f"Recovery probability {self.recov_med * 100:.0f}%–{self.recov_high * 100 - 1:.0f}%: MEDIUM PRIORITY. Create CRM follow-up task and monitor customer activity.")
            else:
                priority = "LOW"
                action = "MONITOR"
                should_email = False
                reasons.append(f"Recovery probability < {self.recov_med * 100:.0f}%: LOW PRIORITY. Monitor session activity passively without outreach.")
        else:
            priority = "LOW"
            action = "MONITOR"
            should_email = False
            reasons.append("No immediate lost-sale intervention required; continuing passive session observation.")
            
        full_reasoning = " ".join(reasons)
        
        return {
            "is_opportunity": is_opportunity,
            "priority": priority,
            "recommended_action": action,
            "reasoning": full_reasoning,
            "should_send_email": should_email,
            "should_create_crm_opp": is_opportunity
        }
