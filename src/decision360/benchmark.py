"""Versioned benchmark runner for deterministic Decision360 reference cases."""

from __future__ import annotations

import argparse
import json
import math
from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path
from time import perf_counter_ns
from typing import Any

from .engine import DecisionInputError, evaluate_case
from .models import DecisionCase, Policy, to_primitive, utc_now


@dataclass(frozen=True)
class CaseResult:
    case_id: str
    critical: bool
    passed: bool
    message: str
    samples: int


def _percentile(values: list[float], percentile: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    index = max(0, math.ceil(percentile * len(ordered)) - 1)
    return ordered[index]


def _payload_for_case(base: dict[str, Any], case_spec: dict[str, Any]) -> dict[str, Any]:
    payload = deepcopy(base)
    payload.update(case_spec.get("case_overrides", {}))
    policy = deepcopy(payload.get("policy", {}))
    policy.update(case_spec.get("policy_overrides", {}))
    payload["policy"] = policy
    removed = set(case_spec.get("remove_evidence_fields", []))
    payload["evidence"] = [item for item in payload.get("evidence", []) if item.get("field") not in removed]
    return payload


def _check_expected(evaluation: Any, expected: dict[str, Any]) -> tuple[bool, str]:
    checks = {
        "action": evaluation.recommendation.action.value,
        "shortfall_units": str(evaluation.shortfall_units),
        "action_units": str(evaluation.recommendation.action_units),
    }
    mismatches = [f"{key}: expected {expected[key]}, got {actual}" for key, actual in checks.items() if key in expected and str(expected[key]) != actual]
    if "reason" in expected and expected["reason"] not in evaluation.recommendation.reason_codes:
        mismatches.append(f"reason missing: {expected['reason']}")
    return (not mismatches, "; ".join(mismatches) if mismatches else "matched reference")


def run_suite(suite_path: str | Path) -> dict[str, Any]:
    suite_path = Path(suite_path).resolve()
    suite = json.loads(suite_path.read_text(encoding="utf-8"))
    base_path = (suite_path.parent / suite["base_case"]).resolve()
    base = json.loads(base_path.read_text(encoding="utf-8"))
    repeats = int(suite.get("repeats", 1))
    results: list[CaseResult] = []
    latency_ms: list[float] = []

    for case_spec in suite["cases"]:
        payload = _payload_for_case(base, case_spec)
        expected = case_spec["expected"]
        case_id = str(case_spec["id"])
        critical = bool(case_spec.get("critical", False))
        if "error_contains" in expected:
            try:
                evaluate_case(DecisionCase.from_dict(payload), Policy.from_dict(payload.get("policy")))
            except (DecisionInputError, ValueError) as error:
                passed = expected["error_contains"] in str(error)
                results.append(CaseResult(case_id, critical, passed, str(error), 1))
            else:
                results.append(CaseResult(case_id, critical, False, "expected an input error", 1))
            continue

        decision_case = DecisionCase.from_dict(payload)
        policy = Policy.from_dict(payload.get("policy"))
        evaluation = None
        for _ in range(repeats):
            started = perf_counter_ns()
            evaluation = evaluate_case(decision_case, policy)
            latency_ms.append((perf_counter_ns() - started) / 1_000_000)
        assert evaluation is not None
        passed, message = _check_expected(evaluation, expected)
        results.append(CaseResult(case_id, critical, passed, message, repeats))

    passed_count = sum(result.passed for result in results)
    critical = [result for result in results if result.critical]
    critical_passed = sum(result.passed for result in critical)
    pass_rate = passed_count / len(results) if results else 0.0
    critical_pass_rate = critical_passed / len(critical) if critical else 1.0
    p95_ms = _percentile(latency_ms, 0.95)
    thresholds = suite["thresholds"]
    threshold_checks = {
        "pass_rate": pass_rate >= float(thresholds["pass_rate"]),
        "critical_pass_rate": critical_pass_rate >= float(thresholds["critical_pass_rate"]),
        "p95_ms": p95_ms <= float(thresholds["p95_ms"]),
    }
    return {
        "suite_id": suite["suite_id"],
        "generated_at": utc_now(),
        "source": str(suite_path),
        "case_count": len(results),
        "passed_count": passed_count,
        "pass_rate": pass_rate,
        "critical_case_count": len(critical),
        "critical_passed_count": critical_passed,
        "critical_pass_rate": critical_pass_rate,
        "latency": {"sample_count": len(latency_ms), "p95_ms": p95_ms},
        "thresholds": thresholds,
        "threshold_checks": threshold_checks,
        "passed": all(threshold_checks.values()),
        "cases": [to_primitive(result) for result in results],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--suite", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--fail-on-threshold", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = run_suite(args.suite)
    rendered = json.dumps(report, indent=2, sort_keys=True)
    print(rendered)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
    return 1 if args.fail_on_threshold and not report["passed"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
