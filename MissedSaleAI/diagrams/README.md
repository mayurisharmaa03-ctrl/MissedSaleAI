# MissedSale AI – Architecture & System Diagrams (Lucid-Style)

This directory contains professional enterprise architecture diagrams for **MissedSale AI – Intelligent Lost-Sales Detection & Recovery Platform**.

All diagrams follow **Lucidchart-style enterprise design specifications**:
- Rounded rectangle functional blocks
- Distinct decision diamonds
- Color-coded swimlanes
- Directional relation arrows
- High-resolution SVG vector renderings and native GitHub Mermaid code

---

## Diagram Catalog

| Diagram | SVG Vector Asset | Markdown & Mermaid Spec | Key Elements |
|---|---|---|---|
| **1. Overall System Architecture** | [`system_architecture.svg`](system_architecture.svg) | [`system_architecture.md`](system_architecture.md) | Client touchpoints, Flask backend, PostgreSQL, Scikit-Learn ML, 7-Stage Agent, Resend API |
| **2. Agentic AI Loop Architecture** | [`agent_architecture.svg`](agent_architecture.svg) | [`agent_architecture.md`](agent_architecture.md) | **OBSERVE ➔ ANALYZE ➔ REASON ➔ DECIDE ➔ ACT ➔ MONITOR ➔ ADAPT** loop with memory |
| **3. Autonomous Workflow** | [`workflow.svg`](workflow.svg) | [`workflow.md`](workflow.md) | Step-by-step flowchart with dual decision diamonds and feedback loop |
| **4. PostgreSQL ER Schema** | [`database_er_diagram.svg`](database_er_diagram.svg) | [`database_er_diagram.md`](database_er_diagram.md) | Entity relationship diagram across all 12 operational & agent memory tables |
| **5. End-to-End Sequence Flow** | [`sequence_diagram.svg`](sequence_diagram.svg) | [`sequence_diagram.md`](sequence_diagram.md) | 12-step sequence from cart drop-off to email dispatch, customer purchase & adaptation |

---

## Viewing In-App
An interactive visual viewer is available directly within the CRM application at:
**[http://127.0.0.1:5000/architecture](http://127.0.0.1:5000/architecture)**
