"""
MissedSale AI - Main Application Entrypoint
Autonomous AI Sales Recovery Platform
"""

import os
import sys
from pathlib import Path

_THIS_DIR = str(Path(__file__).resolve().parent)
_PARENT_DIR = str(Path(__file__).resolve().parent.parent)
while _PARENT_DIR in sys.path:
    sys.path.remove(_PARENT_DIR)
while "" in sys.path:
    sys.path.remove("")
while "." in sys.path:
    sys.path.remove(".")
while _THIS_DIR in sys.path:
    sys.path.remove(_THIS_DIR)
sys.path.insert(0, _THIS_DIR)
os.chdir(_THIS_DIR)

from flask import Flask
from config import Config
from models import db
from seed_db import seed_database
from ml.train import train_models

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize database
    db.init_app(app)
    
    # Register blueprints
    from routes.auth import auth_bp
    from routes.dashboard import dashboard_bp
    from routes.customers import customers_bp
    from routes.sales import sales_bp
    from routes.opportunities import opportunities_bp
    from routes.crm import crm_bp
    from routes.campaigns import campaigns_bp
    from routes.agent import agent_bp
    from routes.analytics import analytics_bp
    from routes.settings import settings_bp
    from routes.api import api_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(customers_bp)
    app.register_blueprint(sales_bp)
    app.register_blueprint(opportunities_bp)
    app.register_blueprint(crm_bp)
    app.register_blueprint(campaigns_bp)
    app.register_blueprint(agent_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(settings_bp)
    app.register_blueprint(api_bp)
    
    # Context processor for global template variables
    @app.context_processor
    def inject_global_vars():
        from agent.agent import SalesRecoveryAgent
        agent = SalesRecoveryAgent()
        status = agent.get_agent_status()
        return {
            "app_name": Config.APP_NAME,
            "app_version": Config.APP_VERSION,
            "agent_global_status": status
        }
        
    # CLI commands
    @app.cli.command("init-db")
    def init_db_command():
        """Initialize database tables."""
        with app.app_context():
            db.create_all()
            print("Database tables created.")

    @app.cli.command("seed-data")
    def seed_data_command():
        """Seed sample products, customers, and opportunities."""
        seed_database(app)

    @app.cli.command("train-ml")
    def train_ml_command():
        """Train baseline and champion ML models."""
        metrics = train_models()
        print("Models successfully trained.")

    @app.cli.command("run-agent")
    def run_agent_command():
        """Run autonomous agent loop on pending carts."""
        with app.app_context():
            from agent.agent import SalesRecoveryAgent
            agent = SalesRecoveryAgent()
            results = agent.run_batch_autonomous_cycle(limit=5)
            print(f"Agent executed cycle for {len(results)} opportunities.")

    # Auto-initialize and seed if database is empty on first run
    with app.app_context():
        try:
            db.create_all()
            from models import Product
            if Product.query.count() == 0:
                print("Auto-seeding empty database...")
                seed_database(app)
        except Exception as e:
            print(f"Database startup warning: {e}")

    return app

app = create_app()

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    print(f"\n=======================================================")
    print(f"  MissedSale AI – Intelligent Lost-Sales Recovery")
    print(f"  Running on: http://127.0.0.1:{port}")
    print(f"=======================================================\n")
    app.run(host="0.0.0.0", port=port, debug=Config.DEBUG)
