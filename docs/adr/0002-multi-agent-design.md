# ADR 0002: LangGraph Multi-Agent Architecture for AML Investigations

**Date:** 2026-09-12  
**Status:** Accepted  
**Context:** Investigating flagged Anti-Money-Laundering (AML) cases requires gathering evidence across multiple domains: analyzing entity graph relationships, reviewing temporal transaction timelines, running adverse-media RAG searches, drafting regulator-compliant Suspicious Activity Reports (SAR), and verifying facts against raw evidence. Single-prompt LLM calls produce inconsistent narratives and suffer from hallucinated claims.

---

## Decision

We implement an **Agentic Supervisor Pattern using LangGraph** with 6 specialized roles:
1. **Supervisor Agent:** Plans investigation workflow and routes state based on evidence completeness.
2. **Link Analyst:** Executes entity graph expansion and ring detection tools.
3. **Pattern Analyst:** Scans transaction timelines for laundering typologies (*smurfing*, *layering*, *round-tripping*).
4. **Adverse-Media Researcher:** Runs hybrid vector search (Qdrant) over adverse news.
5. **Narrative Writer:** Consumes typed findings to produce FinCEN-format SAR text with evidence citations.
6. **QA Reviewer:** Adversarially checks draft text against typed evidence items; triggers revision loops if claims are uncited or inaccurate.

All tool capabilities are additionally exposed via a **Model Context Protocol (MCP)** server interface.

---

## Consequences

- **Positive:** Reduces manual AML investigation time from hours to < 15 minutes.
- **Positive:** Zero-autonomy filing policy — human analysts review, edit, and sign off on all SAR drafts.
- **Positive:** QA Reviewer prevents hallucinated claims from entering official filings.
- **Negative:** Increased LLM token cost per investigation case (~6 agent execution turns).
