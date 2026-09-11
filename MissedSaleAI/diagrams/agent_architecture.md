# Agentic AI Architecture – Autonomous Recovery Loop

## Overview
The MissedSale AI Agent functions as an autonomous, goal-oriented system adhering to the 7-stage control loop:
**OBSERVE ➔ ANALYZE ➔ REASON ➔ DECIDE ➔ ACT ➔ MONITOR ➔ ADAPT**

![Agent Architecture](agent_architecture.svg)

```mermaid
graph TD
    subgraph AGENTIC_AI_LOOP ["AGENTIC AI LOOP"]
        E[Customer Events] --> O[1. Observation Layer]
        O --> M[Data & Persistent Memory]
        M --> P[2. ML Prediction: Lost & Recovery Probs]
        P --> R[3. Agent Multi-Factor Reasoning]
        R --> D[4. Decision Engine: Priority Assessment]
        
        D --> A{Action Choice}
        A -->|Create Opportunity| T1[CRM Tool]
        A -->|Dispatch Message| T2[Resend Email Tool]
        A -->|Low Likelihood| T3[Passive Monitor Tool]
        
        T1 --> CR[Customer Response]
        T2 --> CR
        T3 --> CR
        
        CR --> MON[6. Outcome Monitoring]
        MON --> MEM[Agent Persistent Memory]
        MEM --> ADAPT[7. Policy Adaptation]
        ADAPT -.->|Feedback & State Update| O
    end
```
