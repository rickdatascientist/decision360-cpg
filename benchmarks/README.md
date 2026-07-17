# Decision360 benchmarks

Run the current deterministic reference suite:

```bash
python -m decision360.benchmark --suite benchmarks/suite.json --fail-on-threshold
```

The suite combines numeric reconciliation, policy boundaries, provenance enforcement, invalid input, and a repeat-run latency measurement. It is intentionally synthetic and does not measure real decision accuracy.

Future immutable suite versions will add reviewer-labeled decision quality, five workflows, agent trajectories, grounding/refusal, security/resilience, system cost/latency, and release holdouts. See [`docs/TEST_STRATEGY.md`](../docs/TEST_STRATEGY.md).
