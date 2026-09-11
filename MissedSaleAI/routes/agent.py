"""
Agent Control Center & Activity Audit Log routes.
"""

from flask import Blueprint, render_template, request, jsonify
from routes.auth import login_required
from models import Customer, CustomerBehavior, AgentAction, RecoveryOpportunity
from agent.agent import SalesRecoveryAgent

agent_bp = Blueprint("agent", __name__)
recovery_agent = SalesRecoveryAgent()

@agent_bp.route("/agent")
@login_required
def agent_control():
    agent_status = recovery_agent.get_agent_status()
    # Find customers with cart activity who haven't completed purchase
    pending_behaviors = CustomerBehavior.query.filter_by(purchased=False).order_by(CustomerBehavior.last_activity.desc()).all()
    all_customers = Customer.query.order_by(Customer.name.asc()).all()
    recent_actions = AgentAction.query.order_by(AgentAction.created_at.desc()).limit(10).all()
    
    return render_template(
        "agent.html",
        agent_status=agent_status,
        pending_behaviors=pending_behaviors,
        all_customers=all_customers,
        recent_actions=recent_actions
    )

@agent_bp.route("/agent/activity")
@login_required
def agent_activity():
    actions = AgentAction.query.order_by(AgentAction.created_at.desc()).all()
    return render_template("agent_activity.html", actions=actions)
