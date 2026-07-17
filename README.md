# Decision360 CPG

> Status: **technical reference beta** — synthetic, governed, and publicly reviewable; not validated planning policy or a production service.

Decision360 CPG is a decision-review layer for a synthetic inventory-shortfall workflow. It evaluates an explicit expedite policy, presents alternatives and assumptions, requires an authorized human decision, records outcomes, and preserves a tamper-evident audit trail.

## What is working

- deterministic Decimal-based evaluation with evidence provenance and reason codes;
- authenticated FastAPI service with operator, approver, viewer, and auditor roles;
- transactional SQLite persistence, schema versioning, idempotent writes, and audit integrity checks;
- browser decision-review interface for evaluation, approval/rejection, and outcome capture;
- allow-listed analysis tools that refuse approvals, outcomes, and external writes;
- reproducible 60-case qualification benchmark plus unit, component, integration, security, performance, concurrency, tamper, and backup/restore tests;
- non-root container image, health check, persistent volume, and operations/security runbooks.

## Public proof boundary

This repository contains only synthetic or independently authored material. The calculations are reference assumptions for engineering validation. They are not a demand-planning accuracy claim, a customer-value claim, or evidence that the workflow is useful to practitioners. The product gate still requires interviews, five approved real workflows, three unguided reviewers, security review, and named human release approval.

## Run locally

Python 3.10 or later is required.

```bash
python -m pip install -e ".[dev]"
```

Set an API-key map in the environment. The values in `.env.example` are local examples and must be replaced for any shared environment.

PowerShell:

```powershell
$env:DECISION360_API_KEYS='{"local-operator-key-change-me":{"actor":"Local Operator","roles":["operator"]},"local-approver-key-change-me":{"actor":"Local Approver","roles":["approver"]},"local-auditor-key-change-me":{"actor":"Local Auditor","roles":["auditor"]}}'
python -m decision360.api
```

Open `http://127.0.0.1:8000`. API documentation is available at `/docs`; health and audit-chain status are public at `/healthz`.

Container:

```bash
export DECISION360_API_KEYS='{"replace-with-long-secret":{"actor":"Operator","roles":["operator"]}}'
docker compose up --build
```

## Verify the technical beta

```bash
python -m pytest -q
python -m decision360.benchmark --suite benchmarks/suite_60.json --output benchmark-report-60.json --fail-on-threshold
python -m compileall -q src tests
```

The qualification gate requires all 60 cases and all critical cases to pass, with engine p95 below 50 ms. The API performance test requires p95 below 500 ms in the local reference environment.

## Repository map

- `src/decision360/` — engine, service, persistence, authentication, tools, UI, and maintenance utilities
- `benchmarks/` — immutable reference suite and deterministic 60-case suite generator
- `tests/` — unit through performance/security qualification
- `docs/EXECUTION_PLAN.md` — ordered product gates and definition of done
- `docs/TEST_STRATEGY.md` — L0–L7 quality model and thresholds
- `docs/OPERATIONS.md` — deployment, backup, restore, incident, and rollback procedures
- `docs/SECURITY.md` — controls, trust boundaries, and known limitations
- `evidence/` — public evidence and claim limits

## Licensing

The repository is public for review, but no reuse license has been selected. Do not assume permission to reuse code or content.
