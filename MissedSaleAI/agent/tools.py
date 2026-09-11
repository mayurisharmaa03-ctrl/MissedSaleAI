"""
Tool and Action Layer for the MissedSale AI Agent.
Enables autonomous interaction with Database, CRM, Resend Email API, and Analytics.
"""

from datetime import datetime, timezone
from models import db, Customer, Product, Sale, CustomerBehavior, LostSale, RecoveryOpportunity, Campaign, CommunicationLog
from agent.prompts import generate_recovery_message

class DatabaseTool:
    """Tool for reading and writing customer, product, and sales data."""
    
    @staticmethod
    def get_customer(customer_id):
        return Customer.query.get(customer_id)
        
    @staticmethod
    def get_customer_behavior(customer_id):
        return CustomerBehavior.query.filter_by(customer_id=customer_id).order_by(CustomerBehavior.last_activity.desc()).first()
        
    @staticmethod
    def get_customer_history(customer_id):
        return Sale.query.filter_by(customer_id=customer_id).all()
        
    @staticmethod
    def get_pending_unprocessed_customers():
        """Finds customers with recent cart activity who have not purchased."""
        return CustomerBehavior.query.filter_by(purchased=False).order_by(CustomerBehavior.last_activity.desc()).all()
        
    @staticmethod
    def record_sale(customer_id, product_id, amount, status="COMPLETED"):
        sale = Sale(
            customer_id=customer_id,
            product_id=product_id,
            amount=amount,
            status=status,
            sale_date=datetime.now(timezone.utc)
        )
        db.session.add(sale)
        db.session.commit()
        return sale

class CRMTool:
    """Tool for managing recovery pipeline, priorities, and opportunity lifecycle."""
    
    @staticmethod
    def create_or_update_opportunity(customer_id, product_id, lost_prob, recovery_prob, priority, action, lost_sale_id=None):
        opp = RecoveryOpportunity.query.filter_by(
            customer_id=customer_id,
            product_id=product_id
        ).first()
        
        if not opp:
            opp = RecoveryOpportunity(
                customer_id=customer_id,
                product_id=product_id,
                lost_sale_id=lost_sale_id,
                recovery_probability=recovery_prob,
                priority=priority,
                recommended_action=action,
                status="ACTION_REQUIRED" if priority in ("HIGH", "MEDIUM") else "ANALYZING",
                created_at=datetime.now(timezone.utc)
            )
            db.session.add(opp)
        else:
            opp.recovery_probability = recovery_prob
            opp.priority = priority
            opp.recommended_action = action
            if opp.status in ("NEW", "ANALYZING") and priority in ("HIGH", "MEDIUM"):
                opp.status = "ACTION_REQUIRED"
                
        db.session.commit()
        return opp

    @staticmethod
    @staticmethod
    def update_opportunity_status(opportunity_id, new_status):
        opp = db.session.get(RecoveryOpportunity, opportunity_id)
        if opp:
            opp.status = new_status
            db.session.commit()
        return opp

    @staticmethod
    def record_recovery(opportunity_id, amount):
        opp = db.session.get(RecoveryOpportunity, opportunity_id)
        if opp:
            opp.status = "RECOVERED"
            opp.recovered_at = datetime.now(timezone.utc)
            opp.recovered_amount = amount
            
            # Also update the associated lost_sale record if present
            if opp.lost_sale_id:
                ls = db.session.get(LostSale, opp.lost_sale_id)
                if ls:
                    ls.status = "RECOVERED"
            db.session.commit()
        return opp

class EmailTool:
    """Tool for generating personalized email copy and dispatching via Resend API."""
    
    @staticmethod
    def draft_email(customer, product, priority, context=None):
        prod_name = product.name if product else "Selected Items"
        prod_price = product.price if product else 99.0
        cust_val = customer.customer_value if customer else "Medium"
        return generate_recovery_message(customer.name, prod_name, prod_price, priority, cust_val, context=context)

    @staticmethod
    def send_email(customer, product, opportunity, email_service, context=None):
        """Dispatches recovery email via email_service (Resend API or demo mode)."""
        draft = EmailTool.draft_email(customer, product, opportunity.priority, context=context)
        result = email_service.send_recovery_email(
            to_email=customer.email,
            customer_name=customer.name,
            subject=draft["subject"],
            body_text=draft["body"],
            customer_id=customer.id,
            opportunity_id=opportunity.id
        )
        return result

class AnalyticsTool:
    """Tool for computing real-time sales recovery statistics."""
    
    @staticmethod
    def compute_kpis():
        total_customers = Customer.query.count()
        total_sales_count = Sale.query.filter_by(status="COMPLETED").count()
        total_sales_volume = db.session.query(db.func.sum(Sale.amount)).filter_by(status="COMPLETED").scalar() or 0.0
        
        potential_lost_sales = LostSale.query.count()
        recovery_opportunities = RecoveryOpportunity.query.count()
        high_priority = RecoveryOpportunity.query.filter_by(priority="HIGH").count()
        
        emails_sent = CommunicationLog.query.count()
        recovered_opportunities = RecoveryOpportunity.query.filter_by(status="RECOVERED").all()
        recovered_sales_count = len(recovered_opportunities)
        recovered_revenue = sum(o.recovered_amount for o in recovered_opportunities)
        
        recovery_rate = (recovered_sales_count / recovery_opportunities * 100) if recovery_opportunities > 0 else 0.0
        
        return {
            "total_customers": total_customers,
            "total_sales_count": total_sales_count,
            "total_sales_volume": round(total_sales_volume, 2),
            "potential_lost_sales": potential_lost_sales,
            "recovery_opportunities": recovery_opportunities,
            "high_priority_opportunities": high_priority,
            "emails_sent": emails_sent,
            "recovered_sales_count": recovered_sales_count,
            "recovered_revenue": round(recovered_revenue, 2),
            "recovery_rate": round(recovery_rate, 1)
        }
