# Tests and evaluation

- `unit/` — isolated calculations, policies, provenance, ledger invariants, and benchmark logic
- `component/` — package and command-line behavior
- `integration/` — evaluation, approval, outcome, and persistence lifecycle

Workflow, agent evaluation, security, performance/cost, recovery, browser/accessibility, and human-validation suites will be added with the corresponding product layers. Critical safety or governance failures remain visible and cannot be averaged away by a composite score.

See [`docs/TEST_STRATEGY.md`](../docs/TEST_STRATEGY.md) for level definitions, thresholds, and release gates.
