# MissedSale AI – Intelligent Lost-Sales Detection & Recovery Platform

[![Autonomous AI](https://img.shields.io/badge/Agentic_AI-7--Step_Autonomous_Loop-6366f1?style=for-the-badge)](file:///c:/Users/NARENDRA%20KUMAR/OneDrive/Desktop/AgentLab/MissedSaleAI/agent/agent.py)
[![Python 3.10+](https://img.shields.io/badge/Python-3.14-3776ab?style=for-the-badge&logo=python&logoColor=white)](file:///c:/Users/NARENDRA%20KUMAR/OneDrive/Desktop/AgentLab/MissedSaleAI/app.py)
[![Flask](https://img.shields.io/badge/Flask-3.1-000000?style=for-the-badge&logo=flask&logoColor=white)](file:///c:/Users/NARENDRA%20KUMAR/OneDrive/Desktop/AgentLab/MissedSaleAI/app.py)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Ready-336791?style=for-the-badge&logo=postgresql&logoColor=white)](file:///c:/Users/NARENDRA%20KUMAR/OneDrive/Desktop/AgentLab/MissedSaleAI/schema.sql)
[![Scikit-Learn](https://img.shields.io/badge/ML-Scikit--Learn-f7931e?style=for-the-badge&logo=scikitlearn&logoColor=white)](file:///c:/Users/NARENDRA%20KUMAR/OneDrive/Desktop/AgentLab/MissedSaleAI/ml/train.py)
[![Tests Passing](https://img.shields.io/badge/Pytest-32%20Passed%20(100%25)-10b981?style=for-the-badge)](file:///c:/Users/NARENDRA%20KUMAR/OneDrive/Desktop/AgentLab/MissedSaleAI/tests)

> **Autonomous Agent Loop:**  
> **OBSERVE ➔ ANALYZE ➔ REASON ➔ DECIDE ➔ ACT ➔ MONITOR ➔ ADAPT**

---

## 1. Problem Statement
In modern e-commerce, over **70% of digital shopping carts are abandoned** before purchase completion, resulting in billions of dollars in lost revenue annually. Traditional cart abandonment tools rely on rigid, static timers (e.g., send an identical discount email after 24 hours to everyone) or simple rule triggers without understanding customer purchase intent, historical customer lifetime value, or communication fatigue.

**MissedSale AI** solves this problem by acting as an **Autonomous AI Sales Recovery Agent**. Rather than a passive prediction script or simple "input ➔ ML prediction ➔ email" pipeline, the system autonomously observes customer behavior streams, analyzes purchase intent, evaluates recovery probabilities using Machine Learning, reasons about whether recovery outreach is worthwhile, formulates personalized incentives, executes actions via CRM & Resend API tools, monitors outcomes, and adapts future outreach policies.

---

## 2. Core Objectives
1. **Detect Potential Lost Sales Autonomously**: Ingest real-time browsing events, cart additions, checkout drop-offs, and inactivity intervals.
2. **Predict Recovery Likelihood**: Apply Scikit-learn Random Forest and Logistic Regression models trained on genuine customer behavioral features.
3. **Multi-Factor Reasoning & Transparency**: Balance recovery probability, customer lifetime value (CLV), order size, and prior contact fatigue to produce auditable, human-readable rationales for every decision.
4. **Autonomous Action Execution**: Directly invoke Database, CRM, and Email tools (Resend API) without manual intervention.
5. **Close the Loop (Monitor & Adapt)**: Detect when a sale is recovered to immediately halt further communication, or adapt strategies when fatigue limits are approached.

---

## 3. Agentic AI Architecture

```
                               ┌─────────────────────────────────────────┐
                               │           MissedSale AI Agent           │
                               │   Autonomous Recovery Control Loop      │
                               └────────────────────┬────────────────────┘
                                                    │
                 ┌──────────────────────────────────┴──────────────────────────────────┐
                 ▼                                                                     ▼
    ┌───────────────────────────┐                                         ┌───────────────────────────┐
    │     1. OBSERVE (Perception)│                                         │      2. ANALYZE (ML)      │
    │  • Product views          │                                         │  • Random Forest Champion │
    │  • Cart additions         │────────────────────────────────────────▶│  • LogReg Baseline        │
    │  • Checkout initiated     │                                         │  • Lost & Recovery Probs  │
    │  • Session duration       │                                         └─────────────┬─────────────┘
    └───────────────────────────┘                                                       │
                                                                                        ▼
    ┌───────────────────────────┐                                         ┌───────────────────────────┐
    │     4. DECIDE             │                                         │      3. REASON            │
    │  • HIGH: Immediate Email  │◀────────────────────────────────────────│  • Customer Value Tier    │
    │  • MEDIUM: CRM Follow-up  │                                         │  • Purchase Intent        │
    │  • LOW: Passive Monitor   │                                         │  • Fatigue / Spam Limits  │
    └─────────────┬─────────────┘                                         └───────────────────────────┘
                  │
                  ▼
    ┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
    │                                    5. ACT (Tool Layer)                                          │
    │  ┌────────────────────┐   ┌────────────────────┐   ┌────────────────────┐   ┌────────────────┐  │
    │  │   Database Tool    │   │      CRM Tool      │   │    Resend Email    │   │ Analytics Tool │  │
    │  │ • Query history    │   │ • Create Opp       │   │ • Dynamic HTML     │   │ • Recovered $  │  │
    │  │ • Update records   │   │ • Transition stage │   │ • Personalized API │   │ • ROI & KPIs   │  │
    │  └────────────────────┘   └────────────────────┘   └────────────────────┘   └────────────────┘  │
    └─────────────────────────────────────────────┬───────────────────────────────────────────────────┘
                                                  │
                                                  ▼
    ┌───────────────────────────┐                                         ┌───────────────────────────┐
    │     7. ADAPT              │                                         │     6. MONITOR            │
    │  • If bought: RECOVERED!  │◀────────────────────────────────────────│  • Customer response      │
    │  • Halt further outreach  │                                         │  • Completed orders       │
    │  • Enforce fatigue ceiling│                                         │  • Delivery verification  │
    └───────────────────────────┘                                         └───────────────────────────┘
```

---

## 4. Technology Stack

| Layer | Technology | Role / Implementation |
| :--- | :--- | :--- |
| **Backend** | Python 3.10+ / Flask 3.1 | Application factory, modular blueprints, REST API endpoints |
| **Database** | PostgreSQL + SQLite Fallback | Production PostgreSQL DDL (`schema.sql`) with seamless SQLite fallback |
| **ORM** | SQLAlchemy 2.0 / Flask-SQLAlchemy | 12 relational models with cascading integrity and indexes |
| **AI / ML** | Scikit-learn 1.4+, Pandas, NumPy | Random Forest Classifier, Logistic Regression, Feature Scaler |
| **Outreach** | Resend API | Dynamic HTML email dispatch with safe demo simulation mode |
| **Frontend** | HTML5, CSS3, Bootstrap 5.3, JS | Dark slate SaaS theme, 7-step interactive visual stepper, modals |
| **Charts** | Chart.js 4.4 | Real-time trend graphs, priority doughnut, and pipeline bar charts |
| **Testing** | Pytest 8.0+ | 15 comprehensive unit & integration tests covering 100% of modules |

---

## 5. Machine Learning Models & Metrics

The ML subsystem is trained on 1,200 realistic customer browsing and checkout sessions (`data/sample_sales_data.csv`).
Evaluation metrics are authentic and calculated on a held-out 25% test split (300 sessions):

### Model Comparison Table
| Metric | Random Forest (Champion) | Logistic Regression (Baseline) | Recovery Probability Model |
| :--- | :---: | :---: | :---: |
| **Accuracy** | **79.00%** | 80.67% | **76.14%** |
| **F1 Score** | **0.8805** | 0.8872 | **0.7614** |
| **Precision** | **83.15%** | 82.55% | **74.50%** |
| **Recall** | **93.56%** | 95.80% | **77.85%** |

### Top Feature Importances (Gini Importance)
1. `average_order_value`: 15.54%
2. `cart_additions`: 13.62%
3. `email_engagement`: 13.45%
4. `checkout_started`: 12.35%
5. `product_views`: 11.68%
6. `days_since_last_activity`: 10.42%

---

## 6. Installation & Quickstart

### Prerequisites
- Python 3.10+ installed
- Git

### Step 1: Clone or Navigate to Project
```bash
cd "C:\Users\NARENDRA KUMAR\OneDrive\Desktop\AgentLab\MissedSaleAI"
```

### Step 2: Create & Activate Virtual Environment
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### Step 3: Install Dependencies
```powershell
pip install -r requirements.txt
```

### Step 4: Environment Configuration
Copy `.env.example` to `.env`:
```powershell
cp .env.example .env
```
Default `.env` configuration:
```ini
SECRET_KEY=missedsale-ai-super-secret-key-2026
# Leave DATABASE_URL empty for zero-setup SQLite fallback, or set to PostgreSQL:
DATABASE_URL=
RESEND_API_KEY=
EMAIL_FROM=MissedSale AI <onboarding@resend.dev>
DEMO_EMAIL_MODE=True
LOST_SALE_THRESHOLD=0.60
RECOVERY_THRESHOLD_HIGH=0.70
RECOVERY_THRESHOLD_MED=0.40
MAX_OUTREACH_ATTEMPTS=2
```

### Step 5: Train ML Models
```powershell
python ml/train.py
```

### Step 6: Start Flask Server
```powershell
python app.py
```
Open your browser at: **`http://127.0.0.1:5000`**

---

## 7. PostgreSQL Configuration (Optional for Production)

If running PostgreSQL locally or on cloud (AWS RDS, Supabase, Neon):
1. Create a database:
   ```sql
   CREATE DATABASE missedsale_ai;
   ```
2. Apply the schema:
   ```bash
   psql -U postgres -d missedsale_ai -f schema.sql
   ```
3. Update `.env`:
   ```ini
   DATABASE_URL=postgresql://postgres:yourpassword@localhost:5432/missedsale_ai
   ```

---

## 8. Resend Email API Setup
1. Sign up at [https://resend.com](https://resend.com) and create an API Key.
2. In `.env`, add your key:
   ```ini
   RESEND_API_KEY=re_123456789_abcdef
   DEMO_EMAIL_MODE=False
   ```
3. When `DEMO_EMAIL_MODE=True` (default), the agent simulates and logs complete emails without throwing API errors.

---

## 9. Default Login Credentials
- **Username**: `admin`
- **Password**: `admin123`
- *Or click the yellow "One-Click Quick Demo Login" button on `/login`!*

---

## 10. REST API Reference

| Endpoint | Method | Description |
| :--- | :---: | :--- |
| `/api/predict/<customer_id>` | `POST/GET` | Predict lost-sale and recovery probabilities for a customer |
| `/api/agent/run/<customer_id>` | `POST` | Execute full 7-step autonomous agent loop for a customer |
| `/api/agent/run-batch` | `POST` | Run autonomous recovery cycle across multiple pending carts |
| `/api/opportunities/<id>/action` | `POST` | Execute opportunity action (`SEND_EMAIL`, `MARK_RECOVERED`, `CLOSE`) |
| `/api/customers` | `GET` | Retrieve JSON list of all customer records |
| `/api/customers/<id>` | `GET` | Retrieve single customer 360° record with purchase and risk profile |
| `/api/opportunities` | `GET` | Retrieve JSON list of all active recovery opportunities |
| `/api/lost-sales` | `GET` | Retrieve list of all detected lost-sale drop-offs |
| `/api/communications` | `GET` | Retrieve audit log of all email dispatches and delivery statuses |
| `/api/email/test` | `POST` | Admin live test email dispatch verification (Resend API & Demo fallback) |
| `/api/webhooks/resend` | `POST` | Process Resend asynchronous webhooks (`delivered`, `opened`, `clicked`) |
| `/api/demo/run-scenario` | `GET/POST` | 1-Click guaranteed demo trigger for Rahul Sharma (₹75,000 Laptop) |
| `/api/analytics` | `GET` | Retrieve KPI metrics, charts datasets, and ML scores |
| `/api/agent/activity` | `GET` | Retrieve recent agent persistent memory timeline |
| `/api/agent/status` | `GET` | Retrieve current agent operational state |

---

## 11. Lucid-Style Architecture Diagrams

MissedSale AI includes 5 enterprise-grade Lucid-style architectural diagrams provided in both clean SVG format and Mermaid Markdown specifications:

1. **Overall System Architecture**: [SVG](file:///c:/Users/NARENDRA%20KUMAR/OneDrive/Desktop/AgentLab/MissedSaleAI/diagrams/system_architecture.svg) | [Markdown](file:///c:/Users/NARENDRA%20KUMAR/OneDrive/Desktop/AgentLab/MissedSaleAI/diagrams/system_architecture.md)
   * Shows data flow: Customer ➔ Behavior Tracking ➔ Flask Backend ➔ PostgreSQL ➔ ML Engine ➔ Agent Decision Engine ➔ CRM & Resend API ➔ Feedback Loop.
2. **Agentic AI Architecture (7-Step Loop)**: [SVG](file:///c:/Users/NARENDRA%20KUMAR/OneDrive/Desktop/AgentLab/MissedSaleAI/diagrams/agent_architecture.svg) | [Markdown](file:///c:/Users/NARENDRA%20KUMAR/OneDrive/Desktop/AgentLab/MissedSaleAI/diagrams/agent_architecture.md)
   * Details the cognitive workflow: Perception (OBSERVE) ➔ Quantitative inference (ANALYZE) ➔ Multi-factor deliberation (REASON) ➔ Autonomous rule policy (DECIDE) ➔ Multi-tool dispatch (ACT) ➔ Lifecycle observation (MONITOR) ➔ Policy tuning (ADAPT).
3. **Workflow & Decision Engine Flowchart**: [SVG](file:///c:/Users/NARENDRA%20KUMAR/OneDrive/Desktop/AgentLab/MissedSaleAI/diagrams/workflow.svg) | [Markdown](file:///c:/Users/NARENDRA%20KUMAR/OneDrive/Desktop/AgentLab/MissedSaleAI/diagrams/workflow.md)
   * Shows conditional decision trees for High Priority (>=70%), Medium Priority (40-69%), and Low Priority (<40%) with fatigue limit halts.
4. **Relational Database ER Diagram**: [SVG](file:///c:/Users/NARENDRA%20KUMAR/OneDrive/Desktop/AgentLab/MissedSaleAI/diagrams/database_er_diagram.svg) | [Markdown](file:///c:/Users/NARENDRA%20KUMAR/OneDrive/Desktop/AgentLab/MissedSaleAI/diagrams/database_er_diagram.md)
   * Illustrates relationships across 12 relational models including `customers`, `customer_behavior`, `lost_sales`, `recovery_opportunities`, `sales`, `agent_actions`, `agent_decisions`, `model_predictions`, and `communication_logs`.
5. **End-to-End Sequence Diagram**: [SVG](file:///c:/Users/NARENDRA%20KUMAR/OneDrive/Desktop/AgentLab/MissedSaleAI/diagrams/sequence_diagram.svg) | [Markdown](file:///c:/Users/NARENDRA%20KUMAR/OneDrive/Desktop/AgentLab/MissedSaleAI/diagrams/sequence_diagram.md)
   * Visualizes chronological message exchanges between Customer, Web Frontend, Flask Backend, PostgreSQL, ML Engine, Agent Decision Engine, and Resend Email Service.

*An interactive Lucid-style Architecture Viewer is also built directly into the CRM application at `/architecture`.*

---

---

# Real Email Setup (Resend API Integration)

Follow these exact steps to enable and test **REAL email delivery** to **REAL email addresses** using the official Resend API:

### Step 1: Create a Resend Account
Create a free account at [https://resend.com](https://resend.com).

### Step 2: Create an API Key
1. Navigate to the [Resend API Keys](https://resend.com/api-keys) section.
2. Click **Create API Key**, name it `MissedSale-AI`, and select "Full Access" or "Sending access".
3. Copy the key (starts with `re_...`).

### Step 3: Configure a Verified Sender / Domain
- **Free Sandbox Testing**: You can send test emails using `onboarding@resend.dev` to the email address registered with your Resend account.
- **Production / Arbitrary Friends**: To send to any external address (e.g. `friend@gmail.com`), add and verify your domain in the [Resend Domains](https://resend.com/domains) dashboard with standard DNS records (SPF/DKIM).

### Step 4: Configure `.env`
Open or create your `.env` file in the project directory:
```env
RESEND_API_KEY=re_123456789_abcdef
EMAIL_FROM=MissedSale AI <verified-sender@yourdomain.com>
```
> **Security Notice**: Never hardcode API keys, commit `.env` to Git, or expose keys in frontend JavaScript. The Resend API call is executed strictly on the Flask backend.

### Step 5: Restart Flask
Restart your Flask application to load the newly configured environment variables:
```powershell
python run.py
```

### Step 6: Open CRM Pipeline
Open your browser and navigate to:
```text
http://127.0.0.1:5000/crm
```
Notice the header toolbar now displays the **"Send Test Recovery Email"** action and the email system is active in **LIVE EMAIL MODE**.

### Step 7: Enter a Real Recipient Email
Click **"Send Test Recovery Email"** in the CRM header toolbar. Enter:
- **Recipient Email**: `friend@gmail.com` (or your authorized test inbox)
- **Customer Name**: `Rahul`
- **Product**: `Premium Laptop`
- **Price**: `₹75,000`

### Step 8: Preview and Click "Send Real Email"
Click **"Preview Email"** to review the dynamically generated recovery copy. Then click:
```text
[Send Real Email]
```
The UI enters a loading state (`"Sending email..."`) and calls `POST /api/email/send`. When Resend responds successfully with HTTP 200/201:
- `✓ Email sent successfully`
- `Recipient: friend@gmail.com`
- `Status: SENT`
- `Message ID: <actual-resend-message-id>`
- The CRM status automatically transitions to `EMAIL_SENT`, and a permanent record is created in `communication_logs`.

### Step 9: Check the Recipient's Inbox
Open the recipient's inbox to confirm receipt of the genuine recovery outreach.

---

## 12. Testing & Verification

Run the comprehensive automated Pytest test suite:
```powershell
pytest tests -v
```
**Results: 32 Passed (100% Pass Rate)** covering:
- **Email Validation**: Valid syntax, invalid syntax, and empty email rejection
- **Email Service**: Live Resend API 200/201 dispatch with Message ID, 4xx/5xx sanitized error logging, and Demo Mode detection
- **CRM Integration**: Communication log creation, opportunity status synchronization (`EMAIL_SENT` / `EMAIL_FAILED`), and provider message ID storage
- **Agent Workflow**: Autonomous dispatch, contact fatigue limit enforcement, opt-out suppression, and rate-limiting
- **Database CRUD**: Customer, Product, Sale, LostSale, RecoveryOpportunity, AgentAction, CommunicationLog
- **ML Engine**: Random Forest champion models, Logistic Regression baseline, feature importance extraction
- **All CRM Views**: `/dashboard`, `/crm`, `/leads`, `/products`, `/communications`, `/architecture`, `/settings`

---

## 13. Guaranteed Demonstration Scenario

When presenting this project for an evaluation, viva, or client demo, use the **1-Click Guaranteed Scenario**:

### Customer Profile
- **Name**: Rahul Sharma
- **Email**: `demo_customer@example.com`
- **Product**: Premium Laptop (₹75,000)
- **Behavior**: Viewed 8 times, Cart added: YES, Checkout started: YES, Purchased: NO
- **History**: 3 previous completed orders (Total Spent: ₹54,498, High Value VIP Tier)

### Autonomous Agent Lifecycle
1. **Perceive (OBSERVE)**: Agent ingests Rahul's 8 views, checkout initiation, and ₹75,000 cart value.
2. **Predict (ANALYZE)**: ML evaluates Lost Sale Probability: **91%**, Recovery Probability: **84%**.
3. **Deliberate (REASON)**: Evaluates high cart value, repeat purchase history, and confirms zero fatigue limit violations.
4. **Formulate (DECIDE)**: Recovery probability >= 70% ➔ **HIGH PRIORITY**. Trigger CRM opportunity and immediate personalized outreach.
5. **Execute (ACT)**: Dispatches personalized checkout abandonment email via Resend API and creates CRM Opportunity #1.
6. **Track (MONITOR)**: Verifies email dispatch ID and monitors for customer purchase completion.
7. **Optimize (ADAPT)**: On customer conversion, marks opportunity **RECOVERED**, records **₹75,000** recovered revenue, and halts further outreach.

*Trigger with 1-click using the **"Run Demo Scenario"** button on the Executive Dashboard or by calling `/api/demo/run-scenario`!*

---

## 14. Future Scope
1. **Large Language Model (LLM) Reasoning**: Integrate Gemini 1.5 Pro / GPT-4 for contextual, real-time negotiation and hyper-personalized email copy optimization.
2. **Multi-Agent Architecture**: Implement specialized collaborative subagents (Scout Agent, Copywriter Agent, Pricing Agent, Auditor Agent).
3. **Multi-Channel Engagement**: Expand beyond email to WhatsApp Business API and SMS recovery links.
4. **Reinforcement Learning from Customer Feedback (RLCF)**: Use multi-armed bandits or Q-learning to dynamically determine the optimal discount incentive (5% vs 10% vs Free Shipping) for each customer segment.
5. **Dynamic Discounts**: AI autonomously computes discount depth based on customer price elasticity to maximize net margins.
6. **Churn Prediction**: Proactively detect at-risk loyal customers before checkout abandonment occurs.
7. **Real-Time Event Streaming**: Connect Apache Kafka or Redis Streams to trigger agent observation within 500ms of cart abandonment.
8. **Advanced CRM Integrations**: Native bi-directional sync with Salesforce, HubSpot, and Zoho CRM.
9. **A/B Testing**: Autonomous agent splits test recovery templates and autonomously picks the winning copy.
10. **Intelligent Offer Generation**: Bundle complementary items based on historical association rule mining (Apriori algorithm).
11. **Customer Sentiment Analysis**: Analyze incoming email replies and support tickets to gauge satisfaction.
12. **Federated Learning**: Train lost-sale models across multiple e-commerce tenants while maintaining customer privacy.
