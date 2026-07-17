# Decision360 CPG — thin slice 1

Status: **working reference slice; buyer validation pending**

## User and decision

A supply-chain decision owner reviews a projected SKU shortfall and decides whether to approve an expedite action. The current role name, workflow frequency, thresholds, evidence expectations, and authority model are hypotheses that must be validated.

## User value hypothesis

Make the calculation, evidence, alternatives, assumptions, approval, and realized outcome visible in one trace so the decision can be challenged and learned from.

## Acceptance criteria

- Given complete synthetic evidence, calculations reconcile exactly.
- Both no-action and expedite scenarios show residual risk, cost, lost margin, and reference net benefit.
- A recommendation has machine-readable reason codes and cannot execute.
- Approval requires a named person and rationale.
- Outcomes are blocked before approval and appended after approval.
- A fresh clone runs the example and tests without cloud credentials.

## Non-goals

- production-ready planning logic;
- autonomous action;
- forecast generation or optimization;
- customer savings claims;
- replacement of a planning engine or system of record.

## Validation questions

1. Is expedite the right first decision, and who owns it?
2. Which evidence is actually available and trusted at decision time?
3. Which constraints or alternatives make this reference calculation misleading?
4. What is the approval authority and escalation path?
5. Which outcome is observed later, and after what lag?
6. What failure would make this workflow unsafe or commercially irrelevant?

The answers must replace or remove reference assumptions before this slice is described as buyer-validated.
