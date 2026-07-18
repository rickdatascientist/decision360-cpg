# Public proxy research for simulated workflows

Status: proxy gate passed for prototype and UI development only

Research date: 2026-07-17

Evidence type: public sources and anonymous public anecdotes; no interviews or customer data

## What this evidence can and cannot do

This dossier supports research-backed simulation. It can justify synthetic personas, workflow hypotheses, UI fields, failure cases, and questions for later interviews. It cannot establish buyer demand, workflow frequency, authority, willingness to pay, decision accuracy, usability, or customer value. Vendor case-study outcomes are reported claims, not independently audited results. Anonymous community posts are anecdotes, not representative samples.

The proxy gate passes when each simulated workflow has at least two independent public signals, at least one non-community source, explicit counterevidence or uncertainty, synthetic-only fixtures, and a falsifiable later interview question. Passing unlocks prototype work; it does not close G0 or G5.

## Evidence ledger

| ID | Source and quality | Public observation | Product implication | Limitation |
|---|---|---|---|---|
| PX-01 | [ASCM, CPG demand-forecasting edge](https://www.ascm.org/ascm-insights/beyond-the-shelf--the-cpg-demand-forecasting-edge/) — industry association | CPG planning balances product availability against cost and depends on timely, cross-functional S&OP. | Show service/cost trade-offs, evidence owners, and approval—not only a forecast. | Industry guidance, not a workflow study. |
| PX-02 | [Google Cloud/Anaplan customer story](https://cloud.google.com/customers/anaplan) — named vendor case | Beverage and cold/flu proofs of concept combined sales, inventory, promotions, demographics, weather, competitor promotions, and health signals; the story reports both missed-sales and excess-inventory opportunities. | Preserve signal provenance and compare alternatives at local/product granularity. | Commercial case study; reported benefits are not independently verified. |
| PX-03 | [Google Cloud/OTTO customer story](https://cloud.google.com/customers/otto) — named customer case | Stable and dynamic items behaved differently; seasonal patterns, price changes, promotions, weather, and lifecycle stage mattered. | Segment stable versus volatile/lifecycle cases and show which drivers changed. | Retail rather than CPG manufacturing; model accuracy does not prove better decisions. |
| PX-04 | [Google Cloud/Cainz customer story](https://cloud.google.com/customers/cainz) — named customer case | Moving-average replenishment struggled with seasonal and short-term demand; experience levels produced different accuracy, and explanations were considered important. | Include an explainable override/review workflow and protect against blind automation. | Retail setting and vendor-published narrative. |
| PX-05 | [Microsoft ISE CPG allocation case](https://devblogs.microsoft.com/ise/store-inventory-allocation-cpg/) — engineering case | A CPG lacked store-level demand visibility; useful decisions required POS, store inventory, stockout adjustment, warehouse aggregation, and a visualization for inventory movement. | Add constrained allocation with explicit missing-data states and store/warehouse granularity. | Healthcare CPG context; source documents a solution, not broad buyer validation. |
| PX-06 | [Google Cloud/RELEX customer story](https://cloud.google.com/customers/relex) — named vendor case | Promotion planning involves large volumes and manual repetition; poor plans can create overstock/waste or out-of-stocks, and promotions can shift demand between products. | Add promotion exception review with cannibalization, margin, inventory, and objective visibility. | Retail/vendor marketing claims; agent speed is not evidence of decision quality. |
| PX-07 | [Public supply-chain discussion: demand-planner role](https://www.reddit.com/r/supplychain/comments/1h6pf4r/what_does_a_demand_planner_do_explain_it_like_im_5/) — anonymous anecdote | Contributors describe coordinating base demand, promotions, finance, launches, supply, inventory, obsolete stock, customers, and locations. One anecdote reports a promotion communicated too late and sales far above forecast. | Simulate cross-functional evidence handoffs, late promotion signals, and approval accountability. | Anonymous, self-selected, unverifiable, and not necessarily CPG-representative. |
| PX-08 | [Public supply-chain discussion: forecast and decision silos](https://www.reddit.com/r/supplychain/comments/1uisrp3/the_forecast_is_never_the_problem/) — anonymous anecdote | Contributors describe disconnected decisions, unsupported growth overrides, consensus sign-off, new products without history, and the need to retain a baseline comparison. | Always show baseline versus override, named rationale, dissent, and later outcome. | Anonymous discussion; recent thread may reflect selection and recency bias. |
| PX-09 | [Public supply-chain discussion: missed material risk](https://www.reddit.com/r/supplychain/comments/1jh9d7i/ran_out_of_a_critical_material_last_week_shouldve/) — anonymous anecdote | A poster describes technically available but fragmented inventory, forecast, and PO data, followed by expedite cost and delayed orders when the gap was noticed late. | Retain the shortfall-intervention workflow, but expose freshness, lead time, source conflicts, and no-action cost. | Single anonymous story and not specifically CPG finished goods. |
| PX-10 | [McKinsey, advanced planning in CPG](https://www.mckinsey.com/industries/consumer-packaged-goods/our-insights/digitization-and-advanced-planning-in-cpg) — industry analysis | Disconnected planning/manufacturing systems, inaccurate commercial forecasts, lead times, and schedule noncompliance can raise costs, weaken inventory, and lower service. | Treat system boundaries, lead time, and execution feasibility as first-class constraints. | Advisory analysis; examples and impact claims require independent validation. |

## Convergent themes

1. **The decision is cross-functional.** Forecast, commercial, promotion, finance, inventory, procurement, and execution evidence arrive from different owners and cadences.
2. **A single forecast hides materially different cases.** Stable, seasonal, promoted, price-sensitive, new, and low-velocity items require different uncertainty treatment.
3. **Availability and excess are competing harms.** A useful review must show both service/lost-margin exposure and inventory/cost/waste exposure.
4. **Granularity changes the action.** National or warehouse totals can hide store/customer shortages and misallocation.
5. **Overrides need memory.** The baseline, changed assumption, approver, rationale, dissent, and realized outcome must remain visible.
6. **Explainability is operational, not decorative.** Users need to know which source or change caused the exception and whether the data is current enough to act.

## Counterevidence and cautions

- Better forecast accuracy may not improve a constrained operational decision.
- A deterministic rule can be explainable and still be commercially wrong.
- Community anecdotes emphasize painful exceptions and cannot establish prevalence.
- Retail examples do not automatically transfer to a CPG manufacturer, distributor, or a particular region.
- A fast agent may accelerate a bad or unauthorized action; speed is not a success metric by itself.
- Five simulated workflows are research instruments, not five supported product workflows.

## Proxy-gate result

**PASS — UI/prototype scope only.** Five workflow hypotheses have multi-source public support and explicit limitations. The next step is to build a simulated workflow selector and evidence-first review experience, then use the prototype to obtain practitioner disagreement. G0, G4 human completion, and G5 remain open.
