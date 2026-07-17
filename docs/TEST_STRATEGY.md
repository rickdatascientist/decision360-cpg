# Test and benchmark strategy

## Quality model

Decision360 must be correct at three distinct layers:

1. **Calculation correctness** — inputs, rules, scenarios, and economics reconcile.
2. **Decision governance** — provenance, authority, refusals, audit, and outcomes remain enforceable.
3. **Product usefulness** — relevant users complete validated workflows and make better-informed decisions without hidden founder intervention.

Passing lower levels is necessary but cannot prove usefulness.

## Test levels

| Level | Purpose | Examples | When run | Required gate |
|---|---|---|---|---|
| L0 Static and schema | Catch invalid code/contracts early | compile, formatting, type/schema compatibility, secret scan | Every change | 100% |
| L1 Unit | Prove isolated rules and invariants | arithmetic, thresholds, reason codes, provenance, hash chain | Every change, Python matrix | 100% critical rules |
| L2 Component | Prove package/CLI/service behavior | JSON parsing, CLI output, persistence adapter, error contract | Every PR | 100% supported paths |
| L3 Contract and integration | Prove boundaries work together | API↔database, migrations, identity, idempotency, tool contracts | Every PR when relevant | 100% critical contracts |
| L4 Workflow/E2E | Prove user-visible lifecycle | evidence→scenario→approval→outcome, browser and accessibility | Merge/nightly | ≥90% overall; 100% critical |
| L5 Evaluation benchmark | Measure decision and agent quality | 60-case suite, baseline, trajectories, refusals, citations | Merge/nightly/release | Threshold table below |
| L6 Non-functional | Prove production behavior | security, load, latency, cost, recovery, backup, concurrency | Nightly/release | No critical failure |
| L7 Human validation | Prove usefulness | unguided completion, confusion, rejection, qualitative value | Gate reviews | 3 relevant users |

## Benchmark families

### B1 Deterministic reconciliation

- scenario arithmetic and reference economics;
- thresholds, capacity, zero demand, missing data, negative/non-finite input;
- identical input and policy produce equivalent decision content;
- expected action and reason codes match the versioned reference.

Thresholds: 100% pass; 100% critical pass; p95 engine evaluation under 50 ms in CI reference runs.

### B2 Provenance and governance

- missing evidence is rejected;
- unauthorized or duplicate approvals are rejected;
- outcomes before approval are rejected;
- ledger mutation is detected;
- public output contains assumptions and human-approval requirement.

Thresholds: 100% pass; zero bypasses.

### B3 Decision quality

- regret against a reviewed reference action;
- calibration where probabilities are introduced;
- constraint violations and evidence sufficiency;
- override quality and realized value after outcomes exist.

Thresholds are not set until reviewer-labeled cases exist. Do not publish an accuracy claim before then.

### B4 Agent trajectory and grounding

- correct allow-listed tool path;
- structured-output validity;
- claim-to-evidence coverage;
- refusal on missing evidence or authority;
- deterministic fallback success;
- comparison with the non-agent workflow.

Thresholds: ≥90% correct tool path; 100% schema validity; 100% evidence coverage; 0 unsupported write actions; 100% critical refusals.

### B5 System performance and cost

- deterministic API p50/p95/p99;
- agent latency separated from deterministic service latency;
- token/model/tool cost per completed workflow;
- concurrent approval and idempotency behavior;
- database recovery and backup restore.

Initial thresholds: deterministic API p95 <500 ms; no duplicate side effect; successful restore test. Agent latency and cost receive baselines before release thresholds.

### B6 Security and resilience

- authentication and least-privilege authorization;
- tenant/data isolation;
- injection, unsafe tool arguments, secret/PII leakage, dependency and container scan;
- timeout, retry, partial failure, corrupted input, unavailable dependency;
- audit retention and tamper detection.

Thresholds: 0 open critical/high findings; 100% critical authorization and isolation tests; documented recovery for every injected dependency failure.

### B7 Product usability

- task completion without founder guidance;
- time to decision, confusion, rejection, evidence drill-down, and next-action interest;
- accessibility and keyboard completion;
- user trust in assumptions, alternatives, and authority.

Thresholds: three relevant users; ≥90% supported workflow completion; any critical confusion or unsafe interpretation blocks beta.

## Failure severity

- **Critical:** unauthorized action, data/tenant exposure, incorrect numeric reconciliation, hidden critical risk, audit break, unsupported public claim.
- **High:** supported workflow cannot complete, evidence citation missing, recovery path fails, material benchmark regression.
- **Medium:** non-critical error handling, accessibility defect, confusing but recoverable interaction.
- **Low:** cosmetic or documentation defect without decision impact.

Critical and high failures cannot be averaged away by an overall score.

## Test data rules

- public CI uses only synthetic or independently created data;
- every case has an ID, purpose, source/provenance, expected behavior, severity, and owner;
- a production failure becomes a sanitized regression case before the fix is considered complete;
- benchmark versions are immutable after publication; changes create a new version and explain score movement;
- train/tune examples, development tests, and release holdouts remain separated once model behavior is introduced.

## CI lanes

- **PR fast lane:** compile, L1, L2, L3 where available, deterministic benchmark.
- **Main/nightly:** full workflow suite, security/dependency checks, performance trends, expanded benchmark.
- **Release:** clean environment, full 60-case suite, browser matrix, recovery/restore, security, cost, human evidence, release checklist.

The current repository implements the first PR fast lane. Later levels remain planned gates, not implied capabilities.
