"""Generate the deterministic 60-case qualification suite."""

from __future__ import annotations

import json
from pathlib import Path


def case(case_id: str, *, overrides=None, policy=None, expected=None, critical=False, remove=None):
    item = {
        "id": case_id,
        "critical": critical,
        "case_overrides": overrides or {},
        "policy_overrides": policy or {},
        "expected": expected or {},
    }
    if remove:
        item["remove_evidence_fields"] = remove
    return item


def build() -> dict:
    cases = []
    for index in range(10):
        shortfall = 200 + index * 10
        cases.append(case(
            f"economic_expedite_{index + 1:02d}",
            overrides={"forecast_units": 1000 + index * 10},
            expected={"action": "expedite", "shortfall_units": str(shortfall), "action_units": "150", "reason": "POSITIVE_REFERENCE_NET_BENEFIT"},
            critical=True,
        ))
    for index in range(10):
        cases.append(case(
            f"no_shortfall_{index + 1:02d}",
            overrides={"forecast_units": 700 + index * 10},
            expected={"action": "monitor", "shortfall_units": "0", "action_units": "0", "reason": "NO_PROJECTED_SHORTFALL"},
            critical=True,
        ))
    for index in range(10):
        shortfall = 10 + index
        cases.append(case(
            f"below_threshold_{index + 1:02d}",
            overrides={"forecast_units": 810 + index},
            expected={"action": "monitor", "shortfall_units": str(shortfall), "action_units": "0", "reason": "SHORTFALL_BELOW_POLICY_THRESHOLD"},
        ))
    for index in range(10):
        shortfall = 200 + index * 5
        cases.append(case(
            f"uneconomic_{index + 1:02d}",
            overrides={"forecast_units": 1000 + index * 5, "unit_margin": 2, "expedite_unit_cost": 4},
            expected={"action": "monitor", "shortfall_units": str(shortfall), "action_units": "0", "reason": "EXPEDITE_NOT_ECONOMIC_UNDER_REFERENCE_ASSUMPTIONS"},
            critical=True,
        ))
    for index in range(5):
        cases.append(case(
            f"expedite_disabled_{index + 1:02d}",
            overrides={"forecast_units": 1000 + index * 10},
            policy={"allow_expedite": False},
            expected={"action": "monitor", "shortfall_units": str(200 + index * 10), "action_units": "0", "reason": "EXPEDITE_DISABLED_BY_POLICY"},
            critical=True,
        ))
    for index in range(5):
        cases.append(case(
            f"zero_capacity_{index + 1:02d}",
            overrides={"forecast_units": 1000 + index * 10, "max_expedite_units": 0},
            expected={"action": "monitor", "shortfall_units": str(200 + index * 10), "action_units": "0", "reason": "NO_EXPEDITE_CAPACITY"},
        ))
    provenance_fields = ["forecast_units", "available_inventory_units", "confirmed_inbound_units", "unit_margin", "max_expedite_units"]
    for index, field in enumerate(provenance_fields, 1):
        cases.append(case(
            f"missing_provenance_{index:02d}",
            expected={"error_contains": "Missing evidence provenance"},
            critical=True,
            remove=[field],
        ))
    negative_fields = ["forecast_units", "available_inventory_units", "confirmed_inbound_units", "unit_margin", "max_expedite_units"]
    for index, field in enumerate(negative_fields, 1):
        cases.append(case(
            f"negative_input_{index:02d}",
            overrides={field: -1},
            expected={"error_contains": "Negative values are not allowed"},
            critical=True,
        ))
    assert len(cases) == 60
    return {
        "suite_id": "deterministic-reference-v2-60",
        "description": "Sixty synthetic qualification cases spanning decisions, policy boundaries, provenance, and invalid input.",
        "base_case": "../examples/case_shortfall.json",
        "repeats": 100,
        "thresholds": {"pass_rate": 1.0, "critical_pass_rate": 1.0, "p95_ms": 50.0},
        "cases": cases,
    }


if __name__ == "__main__":
    target = Path(__file__).with_name("suite_60.json")
    target.write_text(json.dumps(build(), indent=2) + "\n", encoding="utf-8")
    print(target)
