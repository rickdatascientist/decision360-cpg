"""Append-only JSONL ledger for evaluations, approvals, and realized outcomes."""

from __future__ import annotations

import json
import os
from decimal import Decimal, InvalidOperation
from hashlib import sha256
from pathlib import Path
from typing import Any, Literal
from uuid import uuid4

from .models import Evaluation, to_primitive, utc_now


class LedgerStateError(RuntimeError):
    """An event would violate the human-approval lifecycle."""


class DecisionLedger:
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)

    def _append(self, event: dict[str, Any]) -> dict[str, Any]:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        current_events = self.events()
        event = to_primitive(event)
        event["previous_event_hash"] = current_events[-1]["event_hash"] if current_events else None
        canonical = json.dumps(event, sort_keys=True, separators=(",", ":"))
        event["event_hash"] = sha256(canonical.encode("utf-8")).hexdigest()
        payload = json.dumps(event, sort_keys=True, separators=(",", ":"))
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(payload + "\n")
            handle.flush()
            os.fsync(handle.fileno())
        return event

    def events(self) -> list[dict[str, Any]]:
        if not self.path.exists():
            return []
        with self.path.open("r", encoding="utf-8") as handle:
            return [json.loads(line) for line in handle if line.strip()]

    def verify_integrity(self) -> bool:
        previous_hash: str | None = None
        for event in self.events():
            stored_hash = event.get("event_hash")
            if event.get("previous_event_hash") != previous_hash or not stored_hash:
                return False
            unsigned = {key: value for key, value in event.items() if key != "event_hash"}
            canonical = json.dumps(unsigned, sort_keys=True, separators=(",", ":"))
            if sha256(canonical.encode("utf-8")).hexdigest() != stored_hash:
                return False
            previous_hash = stored_hash
        return True

    def record_evaluation(self, evaluation: Evaluation) -> dict[str, Any]:
        return self._append(
            {
                "event_id": str(uuid4()),
                "event_type": "evaluation_created",
                "recorded_at": utc_now(),
                "evaluation": evaluation,
            }
        )

    def record_approval(
        self,
        recommendation_id: str,
        *,
        decided_by: str,
        decision: Literal["approved", "rejected"],
        rationale: str,
    ) -> dict[str, Any]:
        if not decided_by.strip() or not rationale.strip():
            raise LedgerStateError("Approval requires a named decision maker and rationale")
        if not self._has_recommendation(recommendation_id):
            raise LedgerStateError("Recommendation must be recorded before approval")
        if self._latest_approval(recommendation_id) is not None:
            raise LedgerStateError("Recommendation already has an approval decision")
        return self._append(
            {
                "event_id": str(uuid4()),
                "event_type": "approval_recorded",
                "recorded_at": utc_now(),
                "recommendation_id": recommendation_id,
                "decision": decision,
                "decided_by": decided_by,
                "rationale": rationale,
            }
        )

    def record_outcome(
        self,
        recommendation_id: str,
        *,
        actual_recovered_units: str,
        realized_net_value: str,
        recorded_by: str,
        note: str = "",
    ) -> dict[str, Any]:
        approval = self._latest_approval(recommendation_id)
        if not approval or approval["decision"] != "approved":
            raise LedgerStateError("Outcome requires an approved recommendation")
        if not recorded_by.strip():
            raise LedgerStateError("Outcome requires a named recorder")
        try:
            recovered = Decimal(str(actual_recovered_units))
            realized = Decimal(str(realized_net_value))
        except InvalidOperation as error:
            raise LedgerStateError("Outcome values must be numeric") from error
        if not recovered.is_finite() or not realized.is_finite() or recovered < 0:
            raise LedgerStateError("Recovered units must be non-negative and outcome values must be finite")
        return self._append(
            {
                "event_id": str(uuid4()),
                "event_type": "outcome_recorded",
                "recorded_at": utc_now(),
                "recommendation_id": recommendation_id,
                "actual_recovered_units": str(recovered),
                "realized_net_value": str(realized),
                "recorded_by": recorded_by,
                "note": note,
            }
        )

    def _has_recommendation(self, recommendation_id: str) -> bool:
        for event in self.events():
            recommendation = event.get("evaluation", {}).get("recommendation", {})
            if recommendation.get("recommendation_id") == recommendation_id:
                return True
        return False

    def _latest_approval(self, recommendation_id: str) -> dict[str, Any] | None:
        approvals = [
            event
            for event in self.events()
            if event.get("event_type") == "approval_recorded"
            and event.get("recommendation_id") == recommendation_id
        ]
        return approvals[-1] if approvals else None
