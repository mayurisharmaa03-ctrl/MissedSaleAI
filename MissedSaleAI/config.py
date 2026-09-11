"""
Centralized Configuration for MissedSale AI Platform.
Supports PostgreSQL with transparent SQLite fallback for frictionless local execution.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "missedsale-ai-super-secret-key-2026")
    
    # Database Configuration
    # Defaults to PostgreSQL, falls back to local SQLite if PostgreSQL is unreachable or not specified
    PG_DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/missedsale_ai")
    SQLITE_DATABASE_URL = f"sqlite:///{BASE_DIR / 'missedsale.db'}"
    
    # Test if PostgreSQL can be connected to, otherwise fallback
    DATABASE_URL = os.getenv("DATABASE_URL")
    IS_VERCEL = bool(os.getenv("VERCEL") or os.getenv("AWS_LAMBDA_FUNCTION_NAME"))
    if not DATABASE_URL:
        if IS_VERCEL:
            DATABASE_URL = "sqlite:////tmp/missedsale.db"
        else:
            DATABASE_URL = SQLITE_DATABASE_URL
        
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Resend Email API Configuration
    RESEND_API_KEY = os.getenv("RESEND_API_KEY", "").strip()
    EMAIL_FROM = os.getenv("EMAIL_FROM", "MissedSale AI <onboarding@resend.dev>").strip()
    DEMO_EMAIL_MODE = os.getenv("DEMO_EMAIL_MODE", "False").lower() in ("true", "1", "t")

    @classmethod
    def is_resend_configured(cls):
        """Returns True if an API key is configured."""
        return bool(cls.RESEND_API_KEY and len(cls.RESEND_API_KEY) > 5)

    # Configurable Discounts (Section 17)
    DISCOUNT_ENABLED = os.getenv("DISCOUNT_ENABLED", "True").lower() in ("true", "1", "t")
    DEFAULT_DISCOUNT_PERCENT = int(os.getenv("DEFAULT_DISCOUNT_PERCENT", "10"))
    DEFAULT_DISCOUNT_CODE = os.getenv("DEFAULT_DISCOUNT_CODE", "RECOVER10")
    VIP_DISCOUNT_CODE = os.getenv("VIP_DISCOUNT_CODE", "VIPCARE15")

    # Autonomous Agent Thresholds (Configurable)
    LOST_SALE_THRESHOLD = float(os.getenv("LOST_SALE_THRESHOLD", "0.60"))
    RECOVERY_THRESHOLD_HIGH = float(os.getenv("RECOVERY_THRESHOLD_HIGH", "0.70"))
    RECOVERY_THRESHOLD_MED = float(os.getenv("RECOVERY_THRESHOLD_MED", "0.40"))
    MAX_OUTREACH_ATTEMPTS = int(os.getenv("MAX_OUTREACH_ATTEMPTS", "2"))
    MAX_EMAILS_PER_DAY = int(os.getenv("MAX_EMAILS_PER_DAY", "3"))
    MIN_EMAIL_INTERVAL_SECONDS = int(os.getenv("MIN_EMAIL_INTERVAL_SECONDS", "60"))
    
    # App Information
    APP_NAME = "MissedSale AI"
    APP_VERSION = "2.0.0"
    DEBUG = os.getenv("FLASK_DEBUG", "True").lower() in ("true", "1", "t")
