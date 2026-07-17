# Decision360 CPG execution plan

Status: active product plan<br>
Owner: Rick<br>
Engineering agent: Codex<br>
Operating principle: evidence before scope, deterministic rules before agents, human authority before action

## Product objective

Deliver a public beta in which relevant supply-chain practitioners can complete five validated decision workflows without founder guidance, inspect the supporting evidence and alternatives, make or reject a recommendation, and record the realized outcome.

The first reference workflow is a synthetic SKU-shortfall expedite decision. It is a learning vehicle, not validated planning policy.

## Definition of beta-ready

Beta-ready means all of the following are true:

- six practitioner interviews support the buyer, problem, and selected workflows;
- five workflows have approved business rules, acceptance tests, non-goals, authority, and outcome definitions;
- three relevant reviewers complete the workflows without live founder guidance;
- deterministic numeric reconciliation, schema validity, provenance, and critical governance gates pass at 100%;
- end-to-end workflow completion is at least 90%;
- no high or critical security finding is open;
- every recommendation cites evidence and requires an authorized human decision;
- cost, latency, failure behavior, limitations, and unsupported claims are documented;
- public IP/clean-room and release checklists are approved.

## Workstream map

| ID | Workstream | Accountable owner | Output | Depends on |
|---|---|---|---|---|
| W0 | Buyer and workflow truth | Rick | Interview evidence and approved workflow set | None |
| W1 | Domain contract and deterministic engine | Rick + Codex | Versioned evidence/decision/approval/outcome contracts | W0 for real rules |
| W2 | Service API and durable ledger | Codex | Authenticated API, database, migrations, idempotency, audit | W1 |
| W3 | Decision-review experience | Rick + Codex | Operator UI for evidence, scenarios, approval, outcome | W1, W2 |
| W4 | Gemini/ADK interaction layer | Codex | Allow-listed read/analysis tools, structured output, refusal policy | W1–W3 |
| W5 | Evaluation and benchmark system | Rick + Codex | 60-case suite, scorecards, regression corpus | Starts with W1; expands through W4 |
| W6 | Platform, security, and operations | Codex + reviewer | IAM, deployment, observability, backups, threat model | W2–W5 |
| W7 | Commercial proof and public beta | Rick | Value model, unguided tests, launch package, limitations | W0–W6 |

## Phase and gate plan

### Phase 0 — Product truth

Deliverables:

- six comparable practitioner interviews;
- buyer, decision owner, current failure, evidence, authority, metric, and changed assumption per interview;
- five candidate workflow cards;
- clean-room exclusions and public evidence rules;
- approved flagship/no-go decision.

Gate G0 — Problem truth:

- at least six relevant practitioners interviewed;
- one accountable buyer and five workflows survive evidence review;
- each workflow has an explicit non-goal and kill condition;
- no confidential source is required to build a public demonstration.

Failure response: rewrite or narrow the workflow set; do not convert reference rules into production logic.

### Phase 1 — Contracts and deterministic correctness

Deliverables:

- versioned models for evidence, assumptions, risk, scenario, recommendation, approval, outcome, trace, cost, and latency;
- exact deterministic calculations with reason codes;
- append-only, tamper-evident decision ledger;
- synthetic data factory and reference cases;
- architecture decision records for numeric precision, identity, idempotency, and storage.

Gate G1 — Contract truth:

- schema validation and deterministic reconciliation pass at 100%;
- every numeric input has provenance;
- every recommendation exposes assumptions and alternatives;
- outcomes are impossible before authorized approval;
- benchmark results reproduce from a fresh clone.

Failure response: freeze UI and agent work until the contract and lifecycle are stable.

### Phase 2 — Usable deterministic vertical slice

Deliverables:

- API with database persistence, migrations, idempotent writes, authorization, and audit access;
- decision-review UI with evidence drill-down, scenario comparison, approval/rejection, and outcome capture;
- first approved workflow runnable end to end;
- structured error and recovery states.

Gate G2 — Workflow truth:

- one workflow completes without developer shortcuts;
- end-to-end reconciliation and audit trace pass at 100%;
- unauthorized and duplicate actions are rejected;
- p95 deterministic API latency is below 500 ms in the reference environment;
- accessibility and browser smoke tests pass.

Failure response: remove features until one reliable workflow remains.

### Phase 3 — Governed agent interaction

Deliverables:

- allow-listed ADK tools over validated services;
- structured output and evidence citations;
- refusal rules for missing evidence, unsafe actions, and insufficient authority;
- trace, token, latency, and cost capture;
- deterministic fallback path.

Gate G3 — Agent safety:

- correct tool path at least 90%;
- structured-output validity and evidence citation coverage at 100%;
- unsupported write actions and critical governance violations at 0%;
- deterministic fallback succeeds for all supported workflows;
- agent adds measurable user value over the non-agent baseline.

Failure response: keep the product deterministic or guided; do not ship an agent that reduces reliability.

### Phase 4 — Five workflows and evaluation hardening

Deliverables:

- five validated workflows;
- at least 60 normal, missing-data, ambiguous, unsafe, adversarial, disruption, and hybrid-integration cases;
- regression cases from every observed failure;
- performance, cost, security, accessibility, and recovery reports;
- baseline comparison and claim limits.

Gate G4 — Evidence truth:

- critical safety and governance pass at 100%;
- numeric reconciliation at 100%;
- workflow completion at least 90%;
- benchmark is reproducible and versioned;
- no high or critical security findings remain;
- failures and confidence limits remain visible rather than averaged away.

Failure response: block beta, reduce workflow scope, and rerun the full affected benchmark family.

### Phase 5 — Unguided beta and commercial proof

Deliverables:

- three unguided sessions with relevant practitioners across the five workflows;
- observed confusion, rejection, completion, and next-action interest;
- transparent low/base/high value and Google consumption model;
- security, privacy, IP, operations, limitations, and incident runbooks;
- public README, demo, architecture, evaluation report, and pilot guide.

Gate G5 — Public beta:

- three users complete the supported workflows without founder intervention, or scope is cut until they can;
- every public claim links to evidence;
- release, IP, security, and rollback approvals are recorded;
- known limitations and non-goals are prominent;
- a named human gives final release approval.

Failure response: remain a private/selective beta and publish evidence or a paper without overstating product readiness.

## Ordered backlog

| Sequence | Task | Exit artifact | Gate |
|---:|---|---|---|
| 1 | Complete six interviews and select five workflows | Sanitized evidence table and decision record | G0 |
| 2 | Replace reference assumptions with approved workflow rules | Five-workflow PRD | G0 |
| 3 | Version the shared decision contract | Contract package and ADRs | G1 |
| 4 | Expand deterministic benchmark to all approved rules | Versioned benchmark report | G1 |
| 5 | Build authenticated service and durable ledger | API, migrations, contract tests | G2 |
| 6 | Build decision-review UI | Browser-tested vertical slice | G2 |
| 7 | Run first unguided deterministic review | Observations and scope decision | G2 |
| 8 | Add allow-listed ADK tools and fallback | Agent trace and refusal tests | G3 |
| 9 | Expand to five workflows and 60 cases | Evaluation scorecards | G4 |
| 10 | Add deployment, IAM, monitoring, backup, and incident recovery | Operational readiness report | G4 |
| 11 | Run three unguided beta tests | Completion and confusion report | G5 |
| 12 | Publish approved beta package | Tagged public release | G5 |

## Definition of done for every task

- requirement and non-goal are explicit;
- acceptance test exists before or with implementation;
- deterministic and failure paths are covered;
- evidence/provenance and security impact are recorded;
- relevant benchmark family passes;
- documentation and decision log are updated;
- owner approves or rejects the output;
- no unsupported public claim is introduced.

## Weekly operating review

Review open gates, benchmark deltas, failure clusters, evidence gaps, security findings, cost/latency trends, user observations, decisions required, and scope cuts. The next task is selected by the earliest failing dependency—not by feature appeal.
