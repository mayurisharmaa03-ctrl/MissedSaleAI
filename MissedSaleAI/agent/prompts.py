"""
Prompt and Message Templates for MissedSale AI.
Provides personalized, dynamic messaging based on customer tier, product, and recovery context.
Implements the 4 distinct production templates defined in the system specification:
  - Template 1: Cart Abandonment
  - Template 2: Checkout Abandonment
  - Template 3: High Value Customer (VIP)
  - Template 4: Follow-up
"""

def template_cart_abandonment(customer_name, product_name, product_price):
    """Template 1 – Cart Abandonment"""
    subject = f"Still interested in {product_name}?"
    body = f"""Hi {customer_name},

We noticed you were interested in the {product_name} (₹{product_price:,.2f}) and added it to your shopping cart.

Your selected product is still available and currently held in your cart.

If you would like to continue your purchase, you can return to your cart right away:

👉 [Return to Cart & Complete Order]

If you have any questions about features, delivery, or specifications, reply directly to this email and our team will be delighted to assist you.

Best regards,
MissedSale AI Autonomous Recovery
"""
    return {"template_id": 1, "template_name": "Cart Abandonment", "subject": subject, "body": body}

def template_checkout_abandonment(customer_name, product_name, product_price):
    """Template 2 – Checkout Abandonment"""
    subject = f"Complete your purchase of {product_name}"
    body = f"""Hi {customer_name},

We noticed you were interested in the {product_name}.

It looks like you were almost ready to complete your purchase (₹{product_price:,.2f}) but didn't finish checkout.

Your selected product is still safely reserved in your checkout session.

If you would like to continue your purchase, you can return to your cart:

👉 [Resume Checkout Now - 1-Click Purchase Link]

Use promo code **RECOVER10** at checkout for free express delivery on this order.

Best regards,
MissedSale AI
"""
    return {"template_id": 2, "template_name": "Checkout Abandonment", "subject": subject, "body": body}

def template_high_value_customer(customer_name, product_name, product_price):
    """Template 3 – High Value Customer"""
    subject = f"We saved your selection for you"
    body = f"""Dear {customer_name},

As one of our most valued VIP customers, we wanted to let you know that we noticed you were looking at the {product_name} (₹{product_price:,.2f}).

We have personally saved your item with priority status so it won't be claimed by other shoppers.

As a gesture of our appreciation for your loyalty, we've applied a VIP priority privilege code **VIPCARE15** giving you 15% savings if completed within 48 hours:

👉 [Claim Your Saved Selection & VIP Savings]

Should you need dedicated concierge support or customized assistance, our senior sales specialists are at your disposal.

Warmest regards,
MissedSale AI – Executive Sales Concierge
"""
    return {"template_id": 3, "template_name": "High Value Customer", "subject": subject, "body": body}

def template_follow_up(customer_name, product_name, product_price):
    """Template 4 – Follow-up"""
    subject = f"Just checking in about {product_name}"
    body = f"""Hi {customer_name},

Just following up regarding the {product_name} (₹{product_price:,.2f}) you recently viewed.

Stock for this product is running low, but we're keeping your cart active for a short while longer.

👉 [Check Availability & Finish Order]

If you decided on a different model or need any advice, feel free to reply and let us know how we can best help.

Best regards,
Customer Success Team @ MissedSale AI
"""
    return {"template_id": 4, "template_name": "Follow-up", "subject": subject, "body": body}

def generate_recovery_message(customer_name, product_name, product_price, recovery_priority="HIGH", customer_value="Medium", context=None):
    """
    Intelligently selects the most suitable template according to the Agent Decision Engine:
    - High-Value customer tier -> Template 3
    - Follow-up attempt -> Template 4
    - Checkout started -> Template 2
    - Cart additions -> Template 1
    """
    context = context or {}
    prior_attempts = context.get("prior_attempts", 0)
    checkout_started = context.get("checkout_started", False)
    
    if prior_attempts > 0:
        return template_follow_up(customer_name, product_name, product_price)
    elif str(customer_value).lower() in ("high", "vip"):
        return template_high_value_customer(customer_name, product_name, product_price)
    elif checkout_started or recovery_priority == "HIGH":
        return template_checkout_abandonment(customer_name, product_name, product_price)
    else:
        return template_cart_abandonment(customer_name, product_name, product_price)
