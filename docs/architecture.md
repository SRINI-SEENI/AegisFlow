# AegisFlow Architecture Specification

## Overview

AegisFlow is designed to solve two core challenges in modern financial crime detection:
1. **Sub-100ms Fraud Scoring:** Scoring high-volume payment streams with real-time velocity, graph proximity, and explainable SHAP reason codes.
2. **Automated AML Case Investigation:** Reducing compliance analyst investigation time from hours to < 15 minutes by orchestrating a team of specialized AI agents.

---

## High-Level Component Map

### 1. Ingestion Service (`services/ingestion`)
- Exposes `POST /api/v1/transactions`.
- Validates transaction schema with Pydantic.
- Persists raw transaction records and entity relationships to PostgreSQL.
- Updates Redis online feature store atomically using LUA scripts.

### 2. Online/Offline Feature Store (`ml/features`)
- **Single-Source Feature Definitions (`definitions.py`):** Single Python module defining window aggregations (1m, 1h, 24h, 7d), velocity counters, and z-scores.
- **Online Path:** Pipelined Redis read/write for millisecond lookup.
- **Offline Path:** PyArrow/Pandas point-in-time batch queries for model training without training-serving skew.

### 3. Real-Time Scoring Microservice (`services/scoring`)
- FastAPI service executing < 100ms p95 latency budget.
- Evaluates deterministic safety rules (sanctions list, impossible travel).
- Loads XGBoost champion model and challenger shadow model from MLflow.
- Precomputes TreeSHAP top-5 reason codes per decision.

### 4. Alert Correlation & Case Engine (`services/casework`)
- Clusters related transaction alerts sharing entity IDs or device fingerprints into unified **Cases**.
- Assigns priority scores and SLA timers.
- Writes immutable audit events via the Transactional Outbox pattern.

### 5. Multi-Agent AML Investigator (`services/investigator`)
- Orchestrated by **LangGraph** with 6 specialized agents:
  - **Supervisor:** Plans investigation and dispatches specialists.
  - **Link Analyst:** Executes entity graph queries and fraud ring detection.
  - **Pattern Analyst:** Analyzes transaction timelines and money laundering typologies (*smurfing*, *layering*, *round-tripping*).
  - **Adverse-Media Researcher:** Hybrid RAG over Qdrant vector database.
  - **Narrative Writer:** Drafts FinCEN-style SAR narrative from typed findings.
  - **QA Reviewer:** Adversarial audit verifying narrative claims against evidence.
- Exposes tools over **Model Context Protocol (MCP)** server interface.

### 6. React Compliance Workbench (`frontend`)
- React + TypeScript + Vite console.
- Interactive entity graph visualization (`react-force-graph` / `d3`).
- Tracked-changes SAR narrative editor with evidence citation chips.
