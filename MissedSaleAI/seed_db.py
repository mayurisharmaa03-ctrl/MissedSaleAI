"""
Database Seeder for MissedSale AI.
Populates realistic Indian-style demo accounts, products in INR (₹), customers,
behavior logs, lost sales, CRM opportunities, and agent activity history.
Guarantees the demo scenario for Rahul Sharma (demo_customer@example.com).
"""

from datetime import datetime, timedelta, timezone
import random
from models import (
    db, User, Customer, Product, Sale, CustomerBehavior,
    LostSale, RecoveryOpportunity, AgentAction, AgentDecision,
    CommunicationLog, Campaign, ModelPrediction
)

def seed_database(app):
    with app.app_context():
        # Create all tables if they do not exist
        db.create_all()
        
        # 1. Admin User
        admin = User.query.filter_by(username="admin").first()
        if not admin:
            admin = User(username="admin", email="admin@missedsale.ai", role="admin")
            admin.set_password("admin123")
            db.session.add(admin)
            print("Created default admin user: admin / admin123")
        else:
            admin.set_password("admin123")

        # 2. Seed Products (16 products in INR ₹)
        products_data = [
            {"name": "Premium Laptop 15.6-inch Intel i9", "category": "Computers", "price": 75000.00, "stock": 25},
            {"name": "UltraSound Pro ANC Wireless Headphones", "category": "Audio", "price": 14999.00, "stock": 50},
            {"name": "CrystalVision 55-inch 4K OLED Smart TV", "category": "Entertainment", "price": 54999.00, "stock": 15},
            {"name": "Nova Chrono Titanium Smartwatch", "category": "Wearables", "price": 18500.00, "stock": 40},
            {"name": "AeroAir Smart HEPA Air Purifier", "category": "Home", "price": 12499.00, "stock": 35},
            {"name": "LuxeComfort High-Back Ergonomic Chair", "category": "Furniture", "price": 19999.00, "stock": 20},
            {"name": "VortexPro 4K Waterproof Action Camera", "category": "Cameras", "price": 24999.00, "stock": 30},
            {"name": "ZenGlow Minimalist Smart RGB Desk Lamp", "category": "Home", "price": 4499.00, "stock": 75},
            {"name": "HyperGlide RGB Mechanical Keyboard", "category": "Accessories", "price": 7999.00, "stock": 60},
            {"name": "BassPulse Dolby Atmos Wireless Soundbar", "category": "Audio", "price": 16499.00, "stock": 28},
            {"name": "SwiftCharge 100W GaN Multi-Port Charger", "category": "Accessories", "price": 3899.00, "stock": 90},
            {"name": "NeoFit Smart Health & Fitness Band", "category": "Wearables", "price": 2999.00, "stock": 100},
            {"name": "AeroDrone GPS 4K Folding Camera Drone", "category": "Cameras", "price": 38500.00, "stock": 18},
            {"name": "PixelGamer 27-inch 165Hz QHD Gaming Monitor", "category": "Computers", "price": 22999.00, "stock": 32},
            {"name": "CloudMesh Whole-Home WiFi 6 System", "category": "Networking", "price": 11299.00, "stock": 45},
            {"name": "TrueSound Studio Monitor Bookshelf Speakers", "category": "Audio", "price": 18999.00, "stock": 22}
        ]

        existing_products = {p.name: p for p in Product.query.all()}
        products = []
        for p_data in products_data:
            if p_data["name"] in existing_products:
                prod = existing_products[p_data["name"]]
                prod.price = p_data["price"]
                prod.stock = p_data["stock"]
                prod.category = p_data["category"]
            else:
                prod = Product(**p_data)
                db.session.add(prod)
            products.append(prod)
        db.session.commit()
        products = Product.query.all()
        premium_laptop = next((p for p in products if "Premium Laptop" in p.name), products[0])
        headphones = next((p for p in products if "Headphones" in p.name), products[1])
        tv = next((p for p in products if "TV" in p.name), products[2])
        chair = next((p for p in products if "Chair" in p.name), products[5])

        # 3. Seed Customers (25 Indian customers across High, Medium, Low tiers)
        customers_info = [
            ("Rahul Sharma", "demo_customer@example.com", "+91-98765-43210", "High", False),  # Guaranteed Demo Scenario
            ("Priya Patel", "priya.patel@example.com", "+91-98234-56781", "High", False),
            ("Amit Kumar", "amit.kumar@example.com", "+91-97123-45672", "Medium", False),
            ("Sneha Reddy", "sneha.reddy@example.com", "+91-96345-67893", "High", False),
            ("Vikram Malhotra", "vikram.m@example.com", "+91-95456-78904", "High", False),
            ("Ananya Iyer", "ananya.iyer@example.com", "+91-94567-89015", "Medium", False),
            ("Rohan Verma", "rohan.verma@example.com", "+91-93678-90126", "Low", False),
            ("Pooja Hegde", "pooja.h@example.com", "+91-92789-01237", "Medium", False),
            ("Arjun Singhania", "arjun.s@example.com", "+91-91890-12348", "High", False),
            ("Deepa Nair", "deepa.nair@example.com", "+91-90901-23459", "Low", False),
            ("Karthik Raja", "karthik.r@example.com", "+91-99812-34560", "Medium", False),
            ("Meera Sen", "meera.sen@example.com", "+91-98723-45671", "High", False),
            ("Suresh Nair", "suresh.nair@example.com", "+91-97634-56782", "Low", False),
            ("Kavita Deshmukh", "kavita.d@example.com", "+91-96545-67893", "Medium", False),
            ("Tanvi Kulkarni", "tanvi.k@example.com", "+91-95456-78904", "High", False),
            ("Nikhil Joshi", "nikhil.j@example.com", "+91-94367-89015", "Low", True), # Opted out
            ("Shreya Mukherjee", "shreya.m@example.com", "+91-93278-90126", "Medium", False),
            ("Rajesh Khanna", "rajesh.k@example.com", "+91-92189-01237", "High", False),
            ("Divya Menon", "divya.m@example.com", "+91-91090-12348", "Medium", False),
            ("Siddharth Rao", "siddharth.rao@example.com", "+91-99901-23459", "Low", False),
            ("Sunita Gupta", "sunita.g@example.com", "+91-98812-34560", "Medium", False),
            ("Manish Tiwari", "manish.t@example.com", "+91-97723-45671", "High", False),
            ("Ritu Agarwal", "ritu.a@example.com", "+91-96634-56782", "Low", False),
            ("Harish Bhatt", "harish.b@example.com", "+91-95545-67893", "Medium", False),
            ("Neha Saxena", "neha.s@example.com", "+91-94456-78904", "High", False)
        ]

        existing_custs = {c.email: c for c in Customer.query.all()}
        customers = []
        for name, email, phone, tier, opt_out in customers_info:
            if email in existing_custs:
                c = existing_custs[email]
                c.name = name
                c.phone = phone
                c.customer_value = tier
                c.email_opt_out = opt_out
            else:
                c = Customer(
                    name=name,
                    email=email,
                    phone=phone,
                    customer_value=tier,
                    email_opt_out=opt_out,
                    email_count=0
                )
                db.session.add(c)
            customers.append(c)
        db.session.commit()
        customers = Customer.query.all()
        rahul = next(c for c in customers if c.email == "demo_customer@example.com")

        # 4. Seed Past Sales (60+ historical orders)
        now = datetime.now(timezone.utc)
        
        # Guaranteed Rahul Sharma sales history: exactly 3 past purchases
        rahul_sales = Sale.query.filter_by(customer_id=rahul.id).all()
        if len(rahul_sales) < 3:
            for s in rahul_sales:
                db.session.delete(s)
            s1 = Sale(customer_id=rahul.id, product_id=headphones.id, amount=headphones.price, status="COMPLETED", sale_date=now - timedelta(days=90))
            s2 = Sale(customer_id=rahul.id, product_id=chair.id, amount=chair.price, status="COMPLETED", sale_date=now - timedelta(days=45))
            s3 = Sale(customer_id=rahul.id, product_id=products[8].id, amount=products[8].price, status="COMPLETED", sale_date=now - timedelta(days=20))
            db.session.add_all([s1, s2, s3])
            db.session.commit()

        # Seed sales for other customers if sales table has fewer than 50
        if Sale.query.count() < 55:
            for c in customers:
                if c.id == rahul.id:
                    continue
                num_orders = 4 if c.customer_value == "High" else (2 if c.customer_value == "Medium" else 1)
                for _ in range(num_orders):
                    p = random.choice(products)
                    sale_dt = now - timedelta(days=random.randint(5, 120), hours=random.randint(1, 18))
                    s = Sale(customer_id=c.id, product_id=p.id, amount=p.price, status="COMPLETED", sale_date=sale_dt)
                    db.session.add(s)
            db.session.commit()

        # 5. Seed Customer Behavior (60+ records)
        # Guaranteed Rahul Sharma behavior matching Section 39:
        # Product viewed: 8 times, Cart added: YES (1), Checkout started: YES, Purchased: NO
        cb_rahul = CustomerBehavior.query.filter_by(customer_id=rahul.id, product_id=premium_laptop.id).first()
        if not cb_rahul:
            cb_rahul = CustomerBehavior(
                customer_id=rahul.id,
                product_id=premium_laptop.id,
                page_views=8,
                product_views=8,
                cart_added=1,
                checkout_started=True,
                purchased=False,
                session_duration=320.0,
                last_activity=now - timedelta(minutes=45)
            )
            db.session.add(cb_rahul)
        else:
            cb_rahul.page_views = 8
            cb_rahul.product_views = 8
            cb_rahul.cart_added = 1
            cb_rahul.checkout_started = True
            cb_rahul.purchased = False
            cb_rahul.session_duration = 320.0
            cb_rahul.last_activity = now - timedelta(minutes=45)

        # Seed realistic behaviors for others
        if CustomerBehavior.query.count() < 55:
            abandon_cases = [
                # (customer_idx, product_idx, cart_added, checkout_started, views, duration_s)
                (1, 2, True, True, 6, 280.0),    # Priya (High) -> TV, checkout started
                (2, 4, True, False, 4, 150.0),   # Amit (Med) -> Air Purifier, cart added
                (3, 1, True, True, 7, 310.0),    # Sneha (High) -> Headphones, checkout started
                (4, 0, True, True, 9, 420.0),    # Vikram (High) -> Laptop, checkout started
                (5, 3, True, False, 5, 190.0),   # Ananya (Med) -> Smartwatch, cart added
                (6, 6, False, False, 2, 45.0),   # Rohan (Low) -> Action Cam, browse only
                (7, 7, True, True, 5, 240.0),    # Pooja (Med) -> Lamp, checkout started
                (8, 9, True, True, 8, 380.0),    # Arjun (High) -> Soundbar, checkout started
                (9, 11, False, False, 3, 60.0),  # Deepa (Low) -> Fitness band, browse only
                (10, 10, True, False, 4, 130.0), # Karthik (Med) -> Charger, cart added
                (11, 12, True, True, 10, 480.0), # Meera (High) -> Drone, checkout started
                (12, 13, False, False, 2, 50.0), # Suresh (Low) -> Monitor, browse only
                (13, 14, True, False, 5, 170.0), # Kavita (Med) -> WiFi, cart added
                (14, 15, True, True, 7, 290.0),  # Tanvi (High) -> Speakers, checkout started
                (15, 8, True, False, 3, 90.0),   # Nikhil (Low/Opt-Out) -> Keyboard, cart added
                (16, 5, True, True, 6, 310.0),   # Shreya (Med) -> Chair, checkout started
                (17, 0, True, True, 8, 410.0),   # Rajesh (High) -> Laptop, checkout started
                (18, 3, True, False, 4, 160.0),  # Divya (Med) -> Smartwatch, cart added
                (19, 7, False, False, 1, 30.0),  # Siddharth (Low) -> Lamp, browse only
                (20, 1, True, True, 5, 220.0),   # Sunita (Med) -> Headphones, checkout started
                (21, 2, True, True, 9, 460.0),   # Manish (High) -> TV, checkout started
                (22, 11, False, False, 2, 40.0), # Ritu (Low) -> Fitness band, browse only
                (23, 4, True, False, 4, 140.0),  # Harish (Med) -> Air purifier, cart added
                (24, 6, True, True, 7, 330.0)    # Neha (High) -> Camera, checkout started
            ]
            for c_idx, p_idx, cart_added, checkout_started, views, dur in abandon_cases:
                act_time = now - timedelta(hours=random.randint(1, 72), minutes=random.randint(5, 55))
                cb = CustomerBehavior(
                    customer_id=customers[c_idx].id,
                    product_id=products[p_idx].id,
                    page_views=views,
                    product_views=views,
                    cart_added=1 if cart_added else 0,
                    checkout_started=checkout_started,
                    purchased=False,
                    session_duration=dur,
                    last_activity=act_time
                )
                db.session.add(cb)
            db.session.commit()

        # 6. Seed Realistic Recovery Opportunities and Successful/Failed Historical Cases
        # Case A: Priya Patel -> Recovered TV ₹54,999 (Successful Recovery!)
        priya = customers[1]
        ls_priya = LostSale.query.filter_by(customer_id=priya.id).first()
        if not ls_priya:
            ls_priya = LostSale(customer_id=priya.id, product_id=tv.id, lost_probability=0.88, detected_at=now - timedelta(days=3), status="RECOVERED")
            db.session.add(ls_priya)
            db.session.commit()
            
            opp_priya = RecoveryOpportunity(
                customer_id=priya.id,
                product_id=tv.id,
                lost_sale_id=ls_priya.id,
                recovery_probability=0.86,
                priority="HIGH",
                recommended_action="SEND_PERSONALIZED_EMAIL",
                reasoning="Customer Priya Patel added 4K OLED TV (₹54,999) to cart and started checkout. High VIP customer with 4 past orders. Recovery probability is 86%. Dispatched checkout abandonment incentive code VIPCARE15.",
                status="RECOVERED",
                recovered_at=now - timedelta(days=2),
                recovered_amount=54999.00
            )
            db.session.add(opp_priya)
            db.session.commit()
            
            # Record sale for the recovery
            s_rec = Sale(customer_id=priya.id, product_id=tv.id, amount=54999.00, status="COMPLETED", sale_date=now - timedelta(days=2))
            db.session.add(s_rec)
            
            comm_priya = CommunicationLog(
                customer_id=priya.id,
                opportunity_id=opp_priya.id,
                channel="EMAIL",
                recipient=priya.email,
                status="DELIVERED",
                subject=f"Complete your purchase of {tv.name}",
                body=f"Hi Priya,\n\nWe noticed you were interested in the {tv.name} (₹54,999.00). Your selection is held with VIP priority...",
                provider="Resend API",
                resend_id=f"re_priya_seed_{int(now.timestamp())}",
                sent_at=now - timedelta(days=3)
            )
            db.session.add(comm_priya)

        # Case B: Sneha Reddy -> Recovered Headphones ₹14,999 (Successful Recovery!)
        sneha = customers[3]
        ls_sneha = LostSale.query.filter_by(customer_id=sneha.id).first()
        if not ls_sneha:
            ls_sneha = LostSale(customer_id=sneha.id, product_id=headphones.id, lost_probability=0.82, detected_at=now - timedelta(days=5), status="RECOVERED")
            db.session.add(ls_sneha)
            db.session.commit()
            
            opp_sneha = RecoveryOpportunity(
                customer_id=sneha.id,
                product_id=headphones.id,
                lost_sale_id=ls_sneha.id,
                recovery_probability=0.79,
                priority="HIGH",
                recommended_action="SEND_PERSONALIZED_EMAIL",
                reasoning="Customer Sneha Reddy abandoned cart with UltraSound Pro ANC Headphones (₹14,999). High purchase frequency. Personalized recovery email dispatched.",
                status="RECOVERED",
                recovered_at=now - timedelta(days=4),
                recovered_amount=14999.00
            )
            db.session.add(opp_sneha)
            
            s_rec2 = Sale(customer_id=sneha.id, product_id=headphones.id, amount=14999.00, status="COMPLETED", sale_date=now - timedelta(days=4))
            db.session.add(s_rec2)

        # Case C: Rohan Verma -> Failed / Fatigue reached (Suppressed)
        rohan = customers[6]
        ls_rohan = LostSale.query.filter_by(customer_id=rohan.id).first()
        if not ls_rohan:
            ls_rohan = LostSale(customer_id=rohan.id, product_id=products[6].id, lost_probability=0.65, detected_at=now - timedelta(days=6), status="EXPIRED")
            db.session.add(ls_rohan)
            db.session.commit()
            
            opp_rohan = RecoveryOpportunity(
                customer_id=rohan.id,
                product_id=products[6].id,
                lost_sale_id=ls_rohan.id,
                recovery_probability=0.28,
                priority="LOW",
                recommended_action="HALT_FATIGUE",
                reasoning="Customer Rohan Verma reached max contact fatigue without opening emails. Recovery probability 28%. Automated emails halted to avoid spam.",
                status="CLOSED"
            )
            db.session.add(opp_rohan)

        # 7. Guaranteed Demo Scenario: Rahul Sharma Lost Sale & Pending Opportunity
        ls_rahul = LostSale.query.filter_by(customer_id=rahul.id, product_id=premium_laptop.id).first()
        if not ls_rahul:
            ls_rahul = LostSale(
                customer_id=rahul.id,
                product_id=premium_laptop.id,
                lost_probability=0.91,
                detected_at=now - timedelta(minutes=40),
                status="DETECTED"
            )
            db.session.add(ls_rahul)
            db.session.commit()

        opp_rahul = RecoveryOpportunity.query.filter_by(customer_id=rahul.id, product_id=premium_laptop.id).first()
        if not opp_rahul:
            opp_rahul = RecoveryOpportunity(
                customer_id=rahul.id,
                product_id=premium_laptop.id,
                lost_sale_id=ls_rahul.id,
                recovery_probability=0.84,
                priority="HIGH",
                recommended_action="SEND_PERSONALIZED_EMAIL",
                reasoning="Customer Rahul Sharma added Premium Laptop worth ₹75,000 to cart, started checkout, but did not purchase. Customer has previously purchased 3 times and has high customer value. Recovery probability is 84%.",
                status="NEW",
                created_at=now - timedelta(minutes=35)
            )
            db.session.add(opp_rahul)

        # 8. Seed Agent Activity Log
        action_samples = [
            ("OBSERVE_BEHAVIOR", rahul.id, "Observed Customer 'Rahul Sharma' (Tier: High). Page views: 8, Cart additions: 1, Checkout initiated: True, Past orders: 3.", "Observation recorded."),
            ("PREDICT_LOST_SALE", rahul.id, "ML models evaluated: Lost-Sale Probability = 91.0%, Recovery Probability = 84.0%.", "Champion Model RF: 0.910, Recovery RF: 0.840"),
            ("CREATE_OPPORTUNITY", rahul.id, f"Created CRM Opportunity for Rahul Sharma: Item 'Premium Laptop' (₹75,000.00). Priority: HIGH.", "Opportunity created successfully."),
            ("DETECT_RECOVERY", priya.id, "Monitored customer event stream: Confirmed Completed Purchase of ₹54,999.00 for CrystalVision 55-inch 4K OLED TV.", "SUCCESS_RECOVERED: ₹54,999.00"),
            ("SEND_RECOVERY_EMAIL", priya.id, "Dispatched recovery outreach with VIP promo code VIPCARE15 for 4K OLED TV.", "Email successfully sent via Resend API."),
            ("HALT_FATIGUE", rohan.id, "Customer Rohan Verma reached max outreach attempts (2). Agent adapted by halting automated emails to protect brand reputation.", "HALTED_FATIGUE")
        ]
        for act_type, cust_id, reason, res in action_samples:
            act = AgentAction(customer_id=cust_id, action_type=act_type, reasoning=reason, result=res, created_at=now - timedelta(minutes=random.randint(10, 300)))
            db.session.add(act)

        db.session.commit()
        print("Database successfully seeded with 25 Indian customers, 16 INR products, and Rahul Sharma guaranteed demo scenario!")

if __name__ == "__main__":
    from app import create_app
    app = create_app()
    seed_database(app)
