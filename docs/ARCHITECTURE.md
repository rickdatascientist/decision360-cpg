# Deterministic decision spine

## Purpose

The first vertical slice proves an auditable decision lifecycle before any Gemini or ADK integration:

```text
evidence-backed case
        ↓
deterministic calculations
        ↓
no-action and expedite scenarios
        ↓
recommendation + reason codes
        ↓
named human approval or rejection
        ↓
realized outcome ledger
```

## Reference calculation

This slice uses a synthetic single-SKU shortfall case. It is not a validated planning policy.

- `projected supply = available inventory + confirmed inbound`
- `shortfall = max(forecast - projected supply, 0)`
- `expedite units = min(shortfall, maximum expedite capacity)`
- `protected margin = expedite units × unit margin`
- `incremental cost = expedite units × expedite unit cost`
- `reference net benefit = protected margin - incremental cost`

The engine recommends expedite only when the shortfall crosses a configurable ratio, expedite is allowed, capacity exists, and reference net benefit exceeds the configurable threshold. Every output carries reason codes and the assumptions used.

## Safety and governance invariants

1. Every numeric input requires an evidence reference.
2. Negative inputs are rejected.
3. The engine never writes to a planning or execution system.
4. Every recommendation requires a named human approval or rejection with rationale.
5. An outcome cannot be recorded unless the recommendation was approved.
6. The JSONL ledger is append-only at the application layer and each event is linked to the previous event with a SHA-256 hash chain.
7. Synthetic assumptions are visible in every evaluation.

## Deliberately deferred

- validated buyer workflows and real business rules;
- authentication, authorization, signing, and durable production storage;
- multi-process ledger concurrency and external immutable storage;
- scenario probability and uncertainty calibration;
- multi-SKU, network, supplier, and constraint optimization;
- Gemini/ADK tools and natural-language interaction;
- BigQuery, Cloud Run, Agent Runtime, and observability;
- user interface and systems-of-record integrations.

These are deferred until the relevant evidence and product decisions exist.
