# Research-backed simulated workflows

Status: synthetic prototype specifications; not buyer-validated

Evidence: `evidence/PUBLIC_PROXY_RESEARCH_2026-07-17.md`

## Shared prototype contract

Every workflow must display the decision owner, trigger, evidence and freshness, baseline, alternatives, assumptions, constraints, expected upside/downside, confidence limits, required human authority, reason codes, and later outcome. Missing or conflicting critical evidence produces a refusal or escalation state. No workflow executes an external action.

## WF-SIM-01 — Shortfall intervention

- **Persona:** supply planner preparing a near-term exception review.
- **Trigger:** projected supply falls below demand inside the intervention lead-time window.
- **Decision:** monitor, expedite a bounded quantity, substitute, reallocate, or escalate.
- **Evidence:** forecast and uncertainty, inventory freshness, confirmed inbound and ETA, margin/service exposure, expedite capacity and landed cost, customer priority.
- **Authority:** separate approver for premium freight or customer-priority changes.
- **Outcome:** recovered units, service result, premium cost, residual shortage, and whether the signal arrived early enough.
- **Unsafe state:** stale inventory/inbound evidence, unavailable capacity, or hidden customer allocation.
- **Sources:** PX-01, PX-09, PX-10.
- **Interview falsifier:** planners say expedite is not their decision, is too infrequent, or is governed entirely elsewhere.

## WF-SIM-02 — Constrained inventory allocation

- **Persona:** CPG supply-chain analyst allocating scarce warehouse inventory across retailers or locations.
- **Trigger:** available supply cannot satisfy all store/customer demand.
- **Decision:** allocation by service tier, incremental demand, store need, contractual priority, or explicit holdback.
- **Evidence:** POS, on-hand, stockout-corrected demand, open orders, warehouse inventory, lead time, retailer constraints, and allocation policy.
- **Authority:** commercial/supply approval when priorities or customer commitments change.
- **Outcome:** fill rate, lost sales, residual imbalance, aged inventory, and override fairness.
- **Unsafe state:** store inventory or retailer logistics visibility is absent; aggregate demand masks local shortages.
- **Sources:** PX-01, PX-02, PX-05, PX-07.
- **Interview falsifier:** CPG planners cannot influence allocation or cannot obtain decision-grade downstream data.

## WF-SIM-03 — Promotion exception review

- **Persona:** demand planner reconciling a commercial promotion with supply and finance.
- **Trigger:** planned uplift, discount, timing, or actual early sell-through differs materially from baseline.
- **Decision:** accept/modify the uplift, constrain the promotion, reposition inventory, or escalate a supply gap.
- **Evidence:** baseline demand, promotion calendar and mechanics, price/discount, POS, inventory, comparable events, cannibalization, margin, funding, and supply feasibility.
- **Authority:** consensus sign-off from demand/commercial, with supply or finance approval for material constraints.
- **Outcome:** incremental units and margin, stockouts, residual inventory/waste, cannibalization, and forecast bias.
- **Unsafe state:** promotion is communicated late, baseline is overwritten, or cannibalization and capacity are omitted.
- **Sources:** PX-02, PX-03, PX-06, PX-07.
- **Interview falsifier:** promotion decisions live entirely in another tool/process or the necessary event data arrives after action is possible.

## WF-SIM-04 — Forecast override and consensus

- **Persona:** demand planner challenging a system or commercial forecast.
- **Trigger:** an override exceeds a materiality threshold or conflicts with historical/external signals.
- **Decision:** retain baseline, accept the override, narrow it, time-box it, or request evidence.
- **Evidence:** system baseline, historical error and bias, commercial rationale, external drivers, comparable periods, inventory/service impact, and dissenting scenario.
- **Authority:** named consensus owner; system must preserve who changed what and why.
- **Outcome:** baseline-versus-override error, inventory/service consequence, and recurring bias by reason/owner—not a blame score.
- **Unsafe state:** unsupported targets replace the baseline, explanation is missing, or one metric rewards systematic bias.
- **Sources:** PX-01, PX-04, PX-08.
- **Interview falsifier:** override governance creates more effort than value or political ownership makes transparent comparison unusable.

## WF-SIM-05 — Seasonal or new-product uncertainty review

- **Persona:** planner preparing launch/seasonal inventory with weak history.
- **Trigger:** new item, lifecycle transition, seasonal peak, price change, or short-term demand regime shift.
- **Decision:** select a low/base/high commitment, stage inventory, delay, run a limited test, or escalate capacity.
- **Evidence:** analog products, attributes, lifecycle stage, launch/promotion plan, price, external signals, lead time, residual value/obsolescence, and replenishment flexibility.
- **Authority:** cross-functional approval for commitment and downside exposure.
- **Outcome:** service, sell-through, residual/obsolete stock, forecast interval coverage, and learning captured for the next launch.
- **Unsafe state:** a point forecast is presented without a range, analog provenance, downside, or exit condition.
- **Sources:** PX-03, PX-04, PX-07, PX-08.
- **Interview falsifier:** users cannot act on ranges or the launch decision occurs before planning evidence exists.

## UI acceptance tests for the next slice

1. A user can select any simulated workflow and immediately see that it is synthetic and unvalidated.
2. The first screen answers: what changed, why now, who owns the decision, and when action becomes impossible.
3. Evidence is grouped by owner/source and shows observed time, freshness, missing fields, and conflicts.
4. Baseline and alternative scenarios remain side by side; an override never erases the baseline.
5. Risks show both shortage/service harm and excess/cost/waste harm where applicable.
6. Approval requires the correct role and a rationale tied to an assumption or evidence item.
7. Keyboard-only completion, focus visibility, error recovery, narrow-screen layout, and readable contrast pass.
8. Every screen offers a visible “challenge this assumption” path for later research sessions.
9. No simulated action can write to an external planning, procurement, logistics, or retailer system.
10. The outcome view compares realized results against both the baseline and approved scenario.
