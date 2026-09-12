# ADR 0001: Single-Source Dual Online/Offline Feature Store

**Date:** 2026-09-12  
**Status:** Accepted  
**Context:** Payment fraud detection systems suffer heavily from **training-serving skew** — a situation where features computed in batch for ML training differ subtly from features computed in real-time during transaction scoring, leading to degraded model performance in production.

---

## Decision

We adopt a **Single-Source Dual Feature Store Architecture**:
1. All feature logic (velocity windows, behavioral z-scores, graph proximity) is declared **once** in a single Python specification module (`ml/features/definitions.py`).
2. The **Online Path** compiles these definitions into Redis LUA scripts and sorted sets for sub-millisecond real-time feature retrieval during transaction scoring.
3. The **Offline Path** compiles the exact same definitions into PyArrow / Pandas batch queries for point-in-time correct training set assembly.

---

## Alternatives Considered

1. **Separate Pipelines (Spark for offline, Flink for online):**
   - *Pros:* High throughput streaming processing.
   - *Cons:* High operational overhead, duplicate feature logic written in Scala/Java vs Python, high risk of training-serving skew.

2. **Database-only Feature Serving (PostgreSQL queries for online scoring):**
   - *Pros:* Simpler infrastructure.
   - *Cons:* SQL aggregation queries over large sliding windows violate the < 100 ms latency budget under load.

---

## Consequences

- **Positive:** Guarantees 100% feature definition parity between training and online inference.
- **Positive:** Meets < 100 ms p95 latency requirement via Redis pipelining.
- **Negative:** Feature definitions must be written strictly within the DSL/specification framework supported by both Redis and PyArrow compilers.
