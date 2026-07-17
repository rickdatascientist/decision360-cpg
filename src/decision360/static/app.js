const fields = [
  "forecast_units", "available_inventory_units", "confirmed_inbound_units",
  "unit_margin", "expedite_unit_cost", "max_expedite_units"
];
let apiKey = sessionStorage.getItem("decision360-api-key") || "";
let currentEvaluation = null;

const workflows = [
  {id: "shortfall", name: "Shortfall intervention", question: "Do we absorb, expedite, substitute, reallocate, or escalate this near-term gap?", trigger: "Projected supply falls below demand inside the intervention lead-time window.", sources: "PX-01 · PX-09 · PX-10", falsifier: "Planners do not own this decision, it is too infrequent, or premium freight is governed entirely elsewhere.", executable: true},
  {id: "allocation", name: "Constrained allocation", question: "Where should scarce inventory go, and which service promise are we choosing not to meet?", trigger: "Available warehouse supply cannot satisfy every retailer or location.", sources: "PX-01 · PX-02 · PX-05 · PX-07", falsifier: "CPG planners cannot influence allocation or cannot obtain decision-grade downstream data.", executable: false},
  {id: "promotion", name: "Promotion exception", question: "Should we accept, constrain, or re-shape the uplift before inventory and margin are committed?", trigger: "Promotion uplift, timing, discount, or early sell-through materially differs from baseline.", sources: "PX-02 · PX-03 · PX-06 · PX-07", falsifier: "The decision lives wholly elsewhere or event data arrives after action is possible.", executable: false},
  {id: "override", name: "Forecast override", question: "What evidence justifies changing the baseline, and who owns the downside if it is wrong?", trigger: "A system or commercial override exceeds materiality or conflicts with observed signals.", sources: "PX-01 · PX-04 · PX-08", falsifier: "Transparent override governance adds effort without value or cannot survive political ownership.", executable: false},
  {id: "lifecycle", name: "New / seasonal item", question: "How much should we commit when history is weak and the cost of being wrong is asymmetric?", trigger: "Launch, seasonal peak, price change, or lifecycle transition creates a new demand regime.", sources: "PX-03 · PX-04 · PX-07 · PX-08", falsifier: "Users cannot act on ranges or the commitment predates all usable planning evidence.", executable: false}
];

const $ = (id) => document.getElementById(id);

function selectWorkflow(workflow) {
  document.querySelectorAll(".workflow-button").forEach((button) => button.setAttribute("aria-pressed", String(button.dataset.workflow === workflow.id)));
  $("workflow-brief-title").textContent = workflow.name;
  $("workflow-question").textContent = workflow.question;
  $("workflow-trigger").textContent = workflow.trigger;
  $("workflow-sources").textContent = workflow.sources;
  $("workflow-falsifier").textContent = workflow.falsifier;
  $("workflow-status").textContent = workflow.executable ? "Executable governed reference" : "Research specification — no encoded decision rule";
  $("case-panel").classList.toggle("hidden", !workflow.executable);
  $("prototype-panel").classList.toggle("hidden", workflow.executable);
  $("prototype-copy").textContent = `${workflow.name} is ready for evidence and usability research. Its rule remains deliberately unimplemented until a practitioner can challenge the trigger, authority, alternatives, and outcome.`;
  $("result-panel").classList.add("hidden");
  $("outcome-panel").classList.add("hidden");
}

$("workflow-nav").replaceChildren(...workflows.map((workflow, index) => {
  const button = document.createElement("button");
  button.type = "button";
  button.className = "workflow-button";
  button.dataset.workflow = workflow.id;
  button.setAttribute("aria-pressed", "false");
  const number = document.createElement("span"); number.className = "workflow-number"; number.textContent = `0${index + 1}`;
  const name = document.createElement("span"); name.className = "workflow-name"; name.textContent = workflow.name;
  button.append(number, name);
  button.addEventListener("click", () => selectWorkflow(workflow));
  return button;
}));
selectWorkflow(workflows[0]);

$("api-key").value = apiKey;
$("save-key").addEventListener("click", () => {
  apiKey = $("api-key").value.trim();
  sessionStorage.setItem("decision360-api-key", apiKey);
  $("access-status").textContent = apiKey ? "Key stored for this browser tab." : "Key cleared.";
});

async function api(path, options = {}) {
  const response = await fetch(path, {
    ...options,
    headers: {"Content-Type": "application/json", "X-API-Key": apiKey, ...(options.headers || {})}
  });
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) {
    const detail = Array.isArray(payload.detail)
      ? payload.detail.map((item) => item.msg || JSON.stringify(item)).join("; ")
      : payload.detail;
    throw new Error(detail || `Request failed (${response.status})`);
  }
  return payload;
}

function syntheticEvidence() {
  const observed = new Date().toISOString();
  return fields.map((field) => ({field, source: `synthetic://web/${field}`, observed_at: observed, note: "Public reference UI"}));
}

$("case-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  $("case-error").textContent = "";
  const values = Object.fromEntries(new FormData(event.target));
  const numeric = (name) => Number(values[name]);
  const body = {
    case_id: values.case_id, sku: values.sku, period: values.period,
    forecast_units: numeric("forecast_units"),
    available_inventory_units: numeric("available_inventory_units"),
    confirmed_inbound_units: numeric("confirmed_inbound_units"),
    unit_margin: numeric("unit_margin"),
    expedite_unit_cost: numeric("expedite_unit_cost"),
    max_expedite_units: numeric("max_expedite_units"),
    evidence: syntheticEvidence(),
    policy: {min_shortfall_ratio: numeric("min_shortfall_ratio"), min_net_benefit: numeric("min_net_benefit"), allow_expedite: true}
  };
  try {
    const result = await api("/api/v1/evaluations", {method: "POST", body: JSON.stringify(body), headers: {"Idempotency-Key": crypto.randomUUID()}});
    currentEvaluation = result.evaluation;
    renderEvaluation(currentEvaluation);
  } catch (error) { $("case-error").textContent = error.message; }
});

function renderEvaluation(evaluation) {
  const metrics = [
    ["Projected supply", evaluation.projected_supply_units], ["Shortfall", evaluation.shortfall_units],
    ["Coverage", `${(Number(evaluation.coverage_ratio) * 100).toFixed(1)}%`],
    ["Recommendation", evaluation.recommendation.action]
  ];
  $("summary").replaceChildren(...metrics.map(([label, value]) => {
    const card = document.createElement("div"); card.className = "metric";
    const text = document.createElement("span"); text.textContent = label;
    const strong = document.createElement("strong"); strong.textContent = value;
    card.append(text, strong); return card;
  }));
  $("scenarios").replaceChildren(...evaluation.scenarios.map((scenario) => {
    const card = document.createElement("article"); card.className = "scenario";
    const title = document.createElement("h4"); title.textContent = scenario.name.replaceAll("_", " ");
    const text = document.createElement("p");
    text.textContent = `Action ${scenario.action_units} units · residual ${scenario.residual_shortfall_units} · cost ${scenario.incremental_cost} · net benefit ${scenario.estimated_net_benefit}`;
    card.append(title, text); return card;
  }));
  $("assumptions").replaceChildren(...evaluation.assumptions.map((value) => { const item = document.createElement("li"); item.textContent = value; return item; }));
  $("result-panel").classList.remove("hidden");
  $("outcome-panel").classList.add("hidden");
  $("decision-status").textContent = `Reason codes: ${evaluation.recommendation.reason_codes.join(", ")}`;
}

async function decide(decision) {
  const rationale = $("rationale").value.trim();
  if (!rationale) { $("decision-status").textContent = "A rationale is required."; return; }
  try {
    const id = currentEvaluation.recommendation.recommendation_id;
    await api(`/api/v1/recommendations/${id}/approval`, {method: "POST", body: JSON.stringify({decision, rationale})});
    $("decision-status").textContent = `Recommendation ${decision}.`;
    if (decision === "approved") $("outcome-panel").classList.remove("hidden");
  } catch (error) { $("decision-status").textContent = error.message; }
}
$("approve").addEventListener("click", () => decide("approved"));
$("reject").addEventListener("click", () => decide("rejected"));
$("record-outcome").addEventListener("click", async () => {
  try {
    const id = currentEvaluation.recommendation.recommendation_id;
    const body = {actual_recovered_units: Number($("actual-units").value), realized_net_value: Number($("actual-value").value), note: $("outcome-note").value};
    const result = await api(`/api/v1/recommendations/${id}/outcomes`, {method: "POST", body: JSON.stringify(body), headers: {"Idempotency-Key": crypto.randomUUID()}});
    $("outcome-status").textContent = `Outcome ${result.outcome.outcome_id} recorded in the audit chain.`;
  } catch (error) { $("outcome-status").textContent = error.message; }
});
