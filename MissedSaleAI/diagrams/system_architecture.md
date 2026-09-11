# Overall System Architecture

## Overview
MissedSale AI connects real-time customer behavior streams with an autonomous Agentic AI loop, Scikit-Learn machine learning predictions, PostgreSQL persistence, and Resend email delivery.

![System Architecture](system_architecture.svg)

```mermaid
graph TB
    subgraph ClientLayer ["1. Client & Touchpoints"]
        Customer["Customer / Shopper"]
        Storefront["Storefront Web App<br/>(HTML5 / Bootstrap 5 / JS)"]
        CRM_UI["Internal CRM Portal<br/>(Pipeline, 360° Profiles, Chart.js)"]
        Inbox["Customer Email Inbox"]
    end

    subgraph BackendLayer ["2. Backend & Data Store"]
        Flask["Flask Application Server<br/>(Auth, REST APIs, Agent Controller)"]
        DB[("PostgreSQL Database<br/>(customers, sales, behaviors,<br/>opportunities, agent memory)")]
    end

    subgraph AgentLayer ["3. AI/ML & Agent Loop"]
        ML["Scikit-Learn ML Engine<br/>(Random Forest Champion<br/>Logistic Regression Baseline)"]
        Agent["Sales Recovery Agent<br/>(7-Step Autonomous Loop)"]
    end

    subgraph ToolLayer ["4. Tool Services"]
        Resend["Resend Email API"]
        Webhooks["Event Webhook Receiver"]
        Tools["Tool Registry<br/>(DBTool, CRMTool, EmailTool)"]
    end

    Customer -->|Browses & Abandons| Storefront
    Storefront -->|POST /api/behavior| Flask
    Flask -->|Persist Records| DB
    Agent -->|Fetch Context & History| DB
    Agent -->|Extract Features| ML
    ML -->|Return Probabilities| Agent
    Agent -->|Execute Tools| Tools
    Tools -->|Create Opp & Log| DB
    Tools -->|Dispatch Outreach| Resend
    Resend -->|Delivers Email| Inbox
    Inbox -->|Resumes Checkout Link| Storefront
    Resend -->|Delivery / Open Events| Webhooks
    Webhooks -->|Update Status| Flask
    Flask -->|Render Real-Time| CRM_UI
```
