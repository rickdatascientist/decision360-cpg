# Decision360 CPG

> Status: **pre-alpha** · 90-day target: **Public beta target**

A governed decision layer above or alongside systems of record and planning engines.

## Product decision

- **Primary buyer:** CSCO / VP Demand Planning
- **Core decision:** Which demand or inventory intervention should we take, with what confidence and value?
- **Platform foundation:** BigQuery, Gemini, ADK, Cloud Run or Agent Runtime, with explicit hybrid-cloud interoperability.
- **Distinct contribution:** Decision value, probabilistic scenarios, human approval, outcome learning, and evidence traceability.

## Public proof standard

This repository is public for transparent product development and review. It contains no confidential employer, customer, interviewee, or production data. Claims remain hypotheses until linked evidence exists in `evidence/`.

## Repository boundaries

- `docs/` — charter, roadmap, architecture decisions, and product decisions
- `evidence/` — public-source provenance, validation summaries, and claim limits
- `src/` — implementation owned by this product
- `tests/` — product-specific acceptance and evaluation tests

Shared contracts may be consumed as versioned dependencies later. Product code, evidence, and decisions must not be copied between repositories without provenance.

## Current gate

**Validation minimum:** Six practitioner interviews, three repeat reviewers, and three unguided tests across five workflows.

**Kill or narrow rule:** If relevant users cannot independently complete five workflows, narrow the product until they can.

## First deterministic slice

The first working slice evaluates one fully synthetic SKU shortfall without an AI model. It compares no action with a configurable expedite scenario, emits explicit reason codes, requires human approval, and records realized outcomes in an append-only JSONL ledger.

This is reference logic for product learning—not validated planning policy or a customer value claim.

```bash
python -m pip install -e .
python -m unittest discover -s tests -v
decision360 evaluate examples/case_shortfall.json --ledger var/decision-ledger.jsonl
```

If the console-script directory is not on your `PATH`, use `python -m decision360.cli evaluate examples/case_shortfall.json`.

See [`docs/PRD.md`](docs/PRD.md) for the hypothesis and acceptance criteria and [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) for calculations, invariants, and deferred scope.

## Licensing

The repository is public for review, but no reuse license has been selected yet. Do not assume permission to reuse code or content.
