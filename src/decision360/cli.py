"""Command-line entry point for the deterministic reference case."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .engine import evaluate_case
from .ledger import DecisionLedger
from .models import DecisionCase, Policy, to_primitive


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    evaluate = subparsers.add_parser("evaluate", help="Evaluate one JSON case")
    evaluate.add_argument("case", type=Path)
    evaluate.add_argument("--ledger", type=Path, help="Append the evaluation to a JSONL ledger")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = json.loads(args.case.read_text(encoding="utf-8"))
    case = DecisionCase.from_dict(payload)
    policy = Policy.from_dict(payload.get("policy"))
    evaluation = evaluate_case(case, policy)
    if args.ledger:
        DecisionLedger(args.ledger).record_evaluation(evaluation)
    print(json.dumps(to_primitive(evaluation), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
