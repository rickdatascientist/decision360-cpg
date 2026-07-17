const fields = [
  "forecast_units", "available_inventory_units", "confirmed_inbound_units",
  "unit_margin", "expedite_unit_cost", "max_expedite_units"
];
let apiKey = sessionStorage.getItem("decision360-api-key") || "";
let currentEvaluation = null;

const $ = (id) => document.getElementById(id);
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
