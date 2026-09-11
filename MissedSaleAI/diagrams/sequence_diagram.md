# End-to-End Recovery Sequence Flow

## Overview
Complete 12-step sequence spanning customer drop-off, agent detection, ML inference, decision formulation, Resend API dispatch, purchase conversion, and agent policy adaptation.

![Sequence Diagram](sequence_diagram.svg)

```mermaid
sequenceDiagram
    autonumber
    actor Customer
    participant Frontend as Storefront UI
    participant Backend as Flask Backend
    participant DB as PostgreSQL
    participant ML as ML Engine
    participant Agent as Recovery Agent
    participant CRM as CRM Tool
    participant Resend as Resend API

    Customer->>Frontend: Abandons cart (Premium Laptop ₹75,000)
    Frontend->>Backend: POST /api/behavior (cart_added=1, checkout_started=1)
    Backend->>DB: Persist CustomerBehavior record
    
    Agent->>DB: 1. OBSERVE: Fetch customer history & prior orders (3)
    Agent->>ML: 2. ANALYZE: Send 11 behavior features
    ML-->>Agent: Returns: Lost-Sale 91%, Recovery 84%
    
    Note over Agent: 3. REASON & DECIDE: High VIP value + No contact fatigue -> HIGH PRIORITY
    
    Agent->>CRM: 4. ACT: Create/Update Opportunity #104
    CRM->>DB: Persist Opportunity & Decision Rationale
    Agent->>Resend: 5. ACT: Send Template 2 (Checkout Abandonment)
    Resend-->>Customer: Delivers recovery email with incentive
    
    Customer->>Frontend: 6. Clicks instant checkout link & completes order
    Frontend->>Backend: POST /api/sales (status="COMPLETED", amount=₹75,000)
    Backend->>DB: Insert Sale record
    
    Agent->>DB: 7. MONITOR: Queries recent sales for converted carts
    Agent->>CRM: 8. ADAPT: Mark Opportunity RECOVERED & record ₹75,000
    CRM->>DB: Update Opportunity status="RECOVERED", recovered_amount=75000.00
    Note over Agent: 9. ADAPT: Terminate recovery loop to protect customer experience
```
