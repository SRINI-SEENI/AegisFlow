# AegisFlow — Real-Time Transaction Risk & AML Investigation Platform

AegisFlow is a financial-crime platform with two tightly integrated halves:
1. **Real-Time Fraud Scoring Engine:** Scores incoming payments in under 100 ms using gradient-boosted models fed by a single-source online/offline feature store (Redis + PostgreSQL) with velocity, profile, and graph features. Every decision carries top-5 SHAP reason codes.
2. **Agentic AML Investigation Workbench:** Flagged cases enter a queue where a multi-agent LLM team (built with LangGraph) automatically gathers evidence, executes vector RAG over adverse media, and drafts a FinCEN-style Suspicious Activity Report (SAR) narrative for human compliance analyst review.

---

## 🏗️ System Architecture

```
Transaction Generator ──HTTP──► Ingestion API ──► PostgreSQL (transactions, entities, edges)
(fraud rings +                  │
 AML typologies)                ├──► Redis (online features: velocity, profiles, graph cache)
                                │
                                ▼
                      Scoring Service (FastAPI)
                      │ rules layer + XGBoost champion + challenger shadow
                      │ SHAP reason codes, calibrated probs
                      ├──► decisions table + audit outbox
                      └──► Alert/Case Engine ──► cases, alerts (PostgreSQL)
                                │
                                ▼
                      Investigation Orchestrator (LangGraph multi-agent)
                      │ link analyst · pattern analyst · media researcher (RAG/Qdrant)
                      │ narrative writer · QA reviewer
                                ▼
                      Case Workbench (React) ◄── Case/SAR API (FastAPI)
                                              human review, edit, approve
```

---

## 📋 Milestone Roadmap

| Milestone | Status | Description |
| :--- | :---: | :--- |
| **M1: Foundation & Infrastructure** | 🔄 In Progress | Repo setup, Docker Compose (Postgres, Redis, Qdrant, MLflow), DB schema/migrations, Synthetic generator skeleton, Architecture docs & ADRs. |
| **M2: Feature Store & Entity Graph** | ⏳ Pending | Single-source feature definitions, Redis online pipeline, PyArrow offline builder, NetworkX entity graph. |
| **M3: Model Training & MLOps** | ⏳ Pending | Supervised XGBoost/LightGBM models, isotonic calibration, MLflow tracking, champion/challenger policy. |
| **M4: Scoring Microservice & Case Engine** | ⏳ Pending | Real-time scoring API (<100ms SLA, SHAP explainer, rules layer), Alert/Case clustering engine. |
| **M5: Agentic AML Investigator** | ⏳ Pending | LangGraph 6-agent team, adverse-media RAG pipeline, versioned SAR narrative editor API. |
| **M6: Workbench Console & Hardening** | ⏳ Pending | React dashboard (Graph view, Case workspace), RBAC/Audit/PII hardening, E2E integration tests. |

---

## 📚 Documentation & ADRs

- [System Architecture Specification](docs/architecture.md)
- [ADR 0001: Single-Source Dual Online/Offline Feature Store](docs/adr/0001-feature-store.md)
- [ADR 0002: LangGraph Multi-Agent Architecture for AML Investigations](docs/adr/0002-multi-agent-design.md)
