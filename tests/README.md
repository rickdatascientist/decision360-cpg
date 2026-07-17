# Tests and evaluation

- `unit/` — isolated calculations, policies, provenance, ledger invariants, and benchmark logic
- `component/` — package, API, UI contract, and command-line behavior
- `integration/` — evaluation, approval, outcome, persistence, concurrency, and backup/restore lifecycle
- `security/` — fail-closed authentication and credential/role boundaries
- `performance/` — deterministic API p95 qualification

Run implemented automated gates with `python -m pytest -q`, then run the versioned corpus with `python -m decision360.benchmark --suite benchmarks/suite_60.json --fail-on-threshold`. Human validation, real agent/model evaluation, cost, and multi-tenant production suites remain future product gates. Critical safety or governance failures remain visible and cannot be averaged away by a composite score.

See [`docs/TEST_STRATEGY.md`](../docs/TEST_STRATEGY.md) for level definitions, thresholds, and release gates.
