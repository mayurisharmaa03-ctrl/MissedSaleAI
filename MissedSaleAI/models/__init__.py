"""
Database initialization and model exports.
"""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from models.user import User
from models.customer import Customer
from models.product import Product
from models.sales import Sale, CustomerBehavior
from models.opportunity import LostSale, RecoveryOpportunity
from models.campaign import Campaign, CommunicationLog
from models.agent_action import AgentAction, AgentDecision, ModelPrediction

__all__ = [
    "db",
    "User",
    "Customer",
    "Product",
    "Sale",
    "CustomerBehavior",
    "LostSale",
    "RecoveryOpportunity",
    "Campaign",
    "CommunicationLog",
    "AgentAction",
    "AgentDecision",
    "ModelPrediction",
]
