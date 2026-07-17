# Technical reference beta report

Release candidate: `v0.2.0-reference`

Assessment date: 2026-07-17

Data boundary: synthetic public fixtures only

## Delivered scope

The release candidate completes one inventory-shortfall decision lifecycle from evidence-backed evaluation through distinct human approval and outcome recording. It includes an authenticated API, browser interface, schema-versioned SQLite store, idempotent transactional writes, hash-chained audit events, governed read/analysis tools, maintenance commands, container packaging, and public operating/security documentation.

## Qualification result

| Gate | Threshold | Result |
|---|---:|---:|
| Automated tests | 100% | 26/26 passed locally |
| 60-case suite | 100% overall | 60/60 |
| Critical benchmark cases | 100% | 45/45 |
| Engine p95 | <50 ms | ~0.02 ms, 5,000 samples |
| Reference API p95 | <500 ms | Passed automated local gate |
| Unsupported governed writes | 0 | 0; tool boundary refuses them |
| Audit tamper detection | Required | Passed |
| Concurrent duplicate effects | 0 | 0 |
| Backup/restore integrity | Required | Passed |
| Known dependency vulnerabilities | 0 | 0 in pinned runtime inventory at assessment |

GitHub Actions independently repeats compilation, Python 3.12/3.13 unit tests, component/integration/security/performance tests, both benchmark suites, the dependency audit, and the container build.

## Claim limits and open product gates

This is a technical reference beta, not the public product beta defined by G5. One synthetic workflow and reference policy cannot establish decision quality or practitioner usefulness. The following remain human/evidence gates:

- six relevant practitioner interviews and selection of five approved workflows;
- replacement of reference assumptions with reviewed business rules;
- three unguided practitioner reviews and at least 90% supported-workflow completion;
- external security review and production identity/tenant/ingress controls;
- cloud deployment credentials, operational owner, and named release approval;
- reviewer-labeled decision-quality and commercial-value evidence.

Until these gates pass, do not describe the product as production-ready, autonomous, validated, accurate, or value-proven.
