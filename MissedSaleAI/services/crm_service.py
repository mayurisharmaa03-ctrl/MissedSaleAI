"""
CRM Service for managing customer pipelines, opportunities, and lifecycle states.
"""

from datetime import datetime, timezone
from models import db, Customer, Product, Sale, CustomerBehavior, LostSale, RecoveryOpportunity, AgentAction, CommunicationLog

class CRMService:
    @staticmethod
    def list_customers(search=None, value_filter=None):
        query = Customer.query
        if search:
            query = query.filter(Customer.name.ilike(f"%{search}%") | Customer.email.ilike(f"%{search}%"))
        if value_filter and value_filter != "ALL":
            query = query.filter_by(customer_value=value_filter)
        return query.order_by(Customer.id.desc()).all()

    @staticmethod
    def get_customer_profile(customer_id):
        customer = Customer.query.get_or_404(customer_id)
        sales = Sale.query.filter_by(customer_id=customer_id).order_by(Sale.sale_date.desc()).all()
        behaviors = CustomerBehavior.query.filter_by(customer_id=customer_id).order_by(CustomerBehavior.last_activity.desc()).all()
        opportunities = RecoveryOpportunity.query.filter_by(customer_id=customer_id).order_by(RecoveryOpportunity.created_at.desc()).all()
        actions = AgentAction.query.filter_by(customer_id=customer_id).order_by(AgentAction.created_at.desc()).all()
        communications = CommunicationLog.query.filter_by(customer_id=customer_id).order_by(CommunicationLog.sent_at.desc()).all()
        
        return {
            "customer": customer,
            "sales": sales,
            "behaviors": behaviors,
            "opportunities": opportunities,
            "actions": actions,
            "communications": communications,
            "total_spent": sum(s.amount for s in sales if s.status == "COMPLETED"),
            "completed_sales_count": len([s for s in sales if s.status == "COMPLETED"])
        }

    @staticmethod
    def list_opportunities(status_filter=None, priority_filter=None):
        query = RecoveryOpportunity.query
        if status_filter and status_filter != "ALL":
            query = query.filter_by(status=status_filter)
        if priority_filter and priority_filter != "ALL":
            query = query.filter_by(priority=priority_filter)
        return query.order_by(RecoveryOpportunity.created_at.desc()).all()

    @staticmethod
    def transition_opportunity_status(opportunity_id, new_status, recovered_amount=None):
        opp = RecoveryOpportunity.query.get_or_404(opportunity_id)
        valid_statuses = [
            "NEW", "ANALYZING", "ACTION_REQUIRED", "EMAIL_SENT", 
            "FOLLOW_UP", "RECOVERED", "CLOSED", "IGNORED"
        ]
        if new_status in valid_statuses:
            opp.status = new_status
            if new_status == "RECOVERED":
                opp.recovered_at = datetime.now(timezone.utc)
                if recovered_amount is not None:
                    opp.recovered_amount = float(recovered_amount)
                elif opp.product:
                    opp.recovered_amount = opp.product.price
                else:
                    opp.recovered_amount = 120.0
                    
                # Create a recovered sale record
                sale = Sale(
                    customer_id=opp.customer_id,
                    product_id=opp.product_id or 1,
                    amount=opp.recovered_amount,
                    status="COMPLETED",
                    sale_date=datetime.now(timezone.utc)
                )
                db.session.add(sale)
                
            db.session.commit()
        return opp
