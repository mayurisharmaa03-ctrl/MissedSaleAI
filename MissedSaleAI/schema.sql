-- =================================================================
-- MissedSale AI – Intelligent Lost-Sales Detection & Recovery Platform
-- PostgreSQL Database Schema Definition
-- =================================================================

-- 1. Users Table (Authentication & Access Control)
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(80) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(30) DEFAULT 'admin',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 2. Customers Table
CREATE TABLE IF NOT EXISTS customers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(120) NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    phone VARCHAR(30),
    customer_value VARCHAR(20) DEFAULT 'Medium',
    email_opt_out BOOLEAN DEFAULT FALSE,
    last_email_sent TIMESTAMP WITH TIME ZONE,
    email_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_customers_email ON customers(email);

-- 3. Products Table
CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    category VARCHAR(80) NOT NULL DEFAULT 'General',
    price NUMERIC(10, 2) NOT NULL DEFAULT 0.00,
    stock INTEGER NOT NULL DEFAULT 100,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 4. Sales Table
CREATE TABLE IF NOT EXISTS sales (
    id SERIAL PRIMARY KEY,
    customer_id INTEGER NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
    product_id INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    amount NUMERIC(10, 2) NOT NULL,
    status VARCHAR(30) NOT NULL DEFAULT 'COMPLETED',
    sale_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_sales_customer_id ON sales(customer_id);
CREATE INDEX IF NOT EXISTS idx_sales_sale_date ON sales(sale_date);

-- 5. Customer Behavior Table
CREATE TABLE IF NOT EXISTS customer_behavior (
    id SERIAL PRIMARY KEY,
    customer_id INTEGER NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
    product_id INTEGER REFERENCES products(id) ON DELETE SET NULL,
    page_views INTEGER DEFAULT 1,
    product_views INTEGER DEFAULT 1,
    cart_added INTEGER DEFAULT 0,
    checkout_started BOOLEAN DEFAULT FALSE,
    purchased BOOLEAN DEFAULT FALSE,
    session_duration NUMERIC(8, 2) DEFAULT 60.00,
    last_activity TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_behavior_customer ON customer_behavior(customer_id);
CREATE INDEX IF NOT EXISTS idx_behavior_activity ON customer_behavior(last_activity);

-- 6. Lost Sales Table
CREATE TABLE IF NOT EXISTS lost_sales (
    id SERIAL PRIMARY KEY,
    customer_id INTEGER NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
    product_id INTEGER REFERENCES products(id) ON DELETE SET NULL,
    lost_probability NUMERIC(5, 4) NOT NULL DEFAULT 0.7500,
    detected_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(30) NOT NULL DEFAULT 'DETECTED'
);
CREATE INDEX IF NOT EXISTS idx_lost_sales_customer ON lost_sales(customer_id);

-- 7. Recovery Opportunities Table (CRM Pipeline)
CREATE TABLE IF NOT EXISTS recovery_opportunities (
    id SERIAL PRIMARY KEY,
    customer_id INTEGER NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
    product_id INTEGER REFERENCES products(id) ON DELETE SET NULL,
    lost_sale_id INTEGER REFERENCES lost_sales(id) ON DELETE SET NULL,
    recovery_probability NUMERIC(5, 4) NOT NULL DEFAULT 0.5000,
    priority VARCHAR(20) NOT NULL DEFAULT 'MEDIUM',
    recommended_action VARCHAR(50) NOT NULL DEFAULT 'CRM_FOLLOW_UP',
    reasoning TEXT,
    status VARCHAR(30) NOT NULL DEFAULT 'NEW',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    recovered_at TIMESTAMP WITH TIME ZONE,
    recovered_amount NUMERIC(10, 2) DEFAULT 0.00
);
CREATE INDEX IF NOT EXISTS idx_opp_customer ON recovery_opportunities(customer_id);
CREATE INDEX IF NOT EXISTS idx_opp_status ON recovery_opportunities(status);
CREATE INDEX IF NOT EXISTS idx_opp_priority ON recovery_opportunities(priority);

-- 8. Campaigns Table
CREATE TABLE IF NOT EXISTS campaigns (
    id SERIAL PRIMARY KEY,
    customer_id INTEGER NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
    opportunity_id INTEGER REFERENCES recovery_opportunities(id) ON DELETE SET NULL,
    subject VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    status VARCHAR(30) DEFAULT 'SENT',
    sent_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_campaigns_customer ON campaigns(customer_id);

-- 9. Communication Logs Table
CREATE TABLE IF NOT EXISTS communication_logs (
    id SERIAL PRIMARY KEY,
    customer_id INTEGER REFERENCES customers(id) ON DELETE CASCADE,
    opportunity_id INTEGER REFERENCES recovery_opportunities(id) ON DELETE SET NULL,
    channel VARCHAR(30) DEFAULT 'EMAIL',
    recipient VARCHAR(120) NOT NULL,
    status VARCHAR(30) DEFAULT 'SENT',
    subject VARCHAR(255),
    body TEXT,
    provider VARCHAR(50) DEFAULT 'Resend',
    resend_id VARCHAR(100),
    error_message TEXT,
    sent_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_comm_customer ON communication_logs(customer_id);
CREATE INDEX IF NOT EXISTS idx_comm_status ON communication_logs(status);

-- 10. Agent Actions (Persistent Agent Memory & Audit Log)
CREATE TABLE IF NOT EXISTS agent_actions (
    id SERIAL PRIMARY KEY,
    customer_id INTEGER NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
    opportunity_id INTEGER REFERENCES recovery_opportunities(id) ON DELETE SET NULL,
    action_type VARCHAR(60) NOT NULL,
    reasoning TEXT NOT NULL,
    result TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_agent_actions_customer ON agent_actions(customer_id);
CREATE INDEX IF NOT EXISTS idx_agent_actions_created ON agent_actions(created_at);

-- 11. Agent Decisions Table
CREATE TABLE IF NOT EXISTS agent_decisions (
    id SERIAL PRIMARY KEY,
    customer_id INTEGER NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
    opportunity_id INTEGER REFERENCES recovery_opportunities(id) ON DELETE SET NULL,
    decision VARCHAR(60),
    reasoning TEXT,
    rationale TEXT NOT NULL,
    confidence NUMERIC(4, 3) DEFAULT 0.850,
    priority VARCHAR(20) NOT NULL DEFAULT 'MEDIUM',
    recommended_action VARCHAR(60) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_agent_decisions_customer ON agent_decisions(customer_id);

-- 12. Model Predictions Table
CREATE TABLE IF NOT EXISTS model_predictions (
    id SERIAL PRIMARY KEY,
    customer_id INTEGER NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
    lost_probability NUMERIC(5, 4) NOT NULL,
    recovery_probability NUMERIC(5, 4) NOT NULL,
    model_name VARCHAR(60) DEFAULT 'Random Forest Champion',
    baseline_probability NUMERIC(5, 4),
    features_json TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_model_preds_customer ON model_predictions(customer_id);
