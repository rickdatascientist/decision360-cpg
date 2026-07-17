"""Governed, allow-listed tool boundary suitable for a future ADK adapter."""

from __future__ import annotations

from typing import Any

from .auth import Principal
from .engine import DecisionInputError, evaluate_case
from .models import DecisionCase, Policy, to_primitive
from .store import SQLiteStore, StoreNotFound


class DecisionTools:
    """Read/analysis tools only; approval and outcome writes remain human API actions."""

    ALLOWED = frozenset({"evaluate_reference_case", "get_evaluation", "audit_integrity"})

    def __init__(self, store: SQLiteStore) -> None:
        self.store = store

    def execute(self, name: str, arguments: dict[str, Any], principal: Principal) -> dict[str, Any]:
        if name not in self.ALLOWED:
            return {
                "status": "refused",
                "reason": "TOOL_NOT_ALLOW_LISTED",
                "message": "Approval, outcome, and external write actions require the human API workflow.",
            }
        if name == "evaluate_reference_case":
            if "operator" not in principal.roles and "admin" not in principal.roles:
                return {"status": "refused", "reason": "ROLE_NOT_AUTHORIZED"}
            try:
                case = DecisionCase.from_dict(arguments)
                evaluation = evaluate_case(case, Policy.from_dict(arguments.get("policy")))
            except (DecisionInputError, ValueError, KeyError) as error:
                return {"status": "refused", "reason": "INVALID_OR_INCOMPLETE_EVIDENCE", "message": str(error)}
            return {"status": "ok", "evaluation": to_primitive(evaluation)}
        if name == "get_evaluation":
            if not principal.roles.intersection({"viewer", "operator", "approver", "auditor", "admin"}):
                return {"status": "refused", "reason": "ROLE_NOT_AUTHORIZED"}
            try:
                return {"status": "ok", "evaluation": self.store.get_evaluation(str(arguments["evaluation_id"]))}
            except (StoreNotFound, KeyError) as error:
                return {"status": "refused", "reason": "EVALUATION_NOT_FOUND", "message": str(error)}
        if "auditor" not in principal.roles and "admin" not in principal.roles:
            return {"status": "refused", "reason": "ROLE_NOT_AUTHORIZED"}
        return {
            "status": "ok",
            "valid": self.store.verify_audit_integrity(),
            "event_count": len(self.store.audit_events()),
        }
