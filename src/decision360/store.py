"""Transactional SQLite persistence for the Decision360 reference beta."""

from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from hashlib import sha256
from pathlib import Path
from typing import Any, Iterator
from uuid import uuid4

from .models import Evaluation, to_primitive, utc_now


class StoreConflict(RuntimeError):
    pass


class StoreNotFound(RuntimeError):
    pass


class SQLiteStore:
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.initialize()

    @contextmanager
    def connect(self) -> Iterator[sqlite3.Connection]:
        connection = sqlite3.connect(self.path, timeout=10)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute("PRAGMA journal_mode = WAL")
        connection.execute("PRAGMA busy_timeout = 10000")
        try:
            with connection:
                yield connection
        finally:
            connection.close()

    def initialize(self) -> None:
        with self.connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS evaluations (
                    evaluation_id TEXT PRIMARY KEY,
                    recommendation_id TEXT NOT NULL UNIQUE,
                    case_id TEXT NOT NULL,
                    request_hash TEXT NOT NULL,
                    idempotency_key TEXT NOT NULL UNIQUE,
                    payload TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS approvals (
                    approval_id TEXT PRIMARY KEY,
                    recommendation_id TEXT NOT NULL UNIQUE,
                    decision TEXT NOT NULL CHECK(decision IN ('approved', 'rejected')),
                    decided_by TEXT NOT NULL,
                    rationale TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY(recommendation_id) REFERENCES evaluations(recommendation_id)
                );
                CREATE TABLE IF NOT EXISTS outcomes (
                    outcome_id TEXT PRIMARY KEY,
                    recommendation_id TEXT NOT NULL,
                    idempotency_key TEXT NOT NULL UNIQUE,
                    request_hash TEXT NOT NULL,
                    actual_recovered_units TEXT NOT NULL,
                    realized_net_value TEXT NOT NULL,
                    recorded_by TEXT NOT NULL,
                    note TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY(recommendation_id) REFERENCES evaluations(recommendation_id)
                );
                CREATE TABLE IF NOT EXISTS audit_events (
                    sequence INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_id TEXT NOT NULL UNIQUE,
                    event_type TEXT NOT NULL,
                    actor TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    previous_event_hash TEXT,
                    event_hash TEXT NOT NULL UNIQUE,
                    created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS schema_migrations (
                    version INTEGER PRIMARY KEY,
                    applied_at TEXT NOT NULL
                );
                """
            )
            connection.execute(
                "INSERT OR IGNORE INTO schema_migrations(version, applied_at) VALUES (1, ?)",
                (utc_now(),),
            )
            connection.execute("PRAGMA user_version = 1")

    def schema_version(self) -> int:
        with self.connect() as connection:
            row = connection.execute("PRAGMA user_version").fetchone()
        return int(row[0])

    @staticmethod
    def request_hash(payload: dict[str, Any]) -> str:
        canonical = json.dumps(to_primitive(payload), sort_keys=True, separators=(",", ":"))
        return sha256(canonical.encode("utf-8")).hexdigest()

    def _audit(self, connection: sqlite3.Connection, event_type: str, actor: str, payload: dict[str, Any]) -> None:
        previous = connection.execute(
            "SELECT event_hash FROM audit_events ORDER BY sequence DESC LIMIT 1"
        ).fetchone()
        event = {
            "event_id": str(uuid4()),
            "event_type": event_type,
            "actor": actor,
            "payload": to_primitive(payload),
            "previous_event_hash": previous["event_hash"] if previous else None,
            "created_at": utc_now(),
        }
        canonical = json.dumps(event, sort_keys=True, separators=(",", ":"))
        event_hash = sha256(canonical.encode("utf-8")).hexdigest()
        connection.execute(
            """INSERT INTO audit_events
               (event_id, event_type, actor, payload, previous_event_hash, event_hash, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                event["event_id"],
                event_type,
                actor,
                json.dumps(event["payload"], sort_keys=True, separators=(",", ":")),
                event["previous_event_hash"],
                event_hash,
                event["created_at"],
            ),
        )

    def save_evaluation(
        self,
        evaluation: Evaluation,
        *,
        idempotency_key: str,
        request_hash: str,
        actor: str,
    ) -> tuple[dict[str, Any], bool]:
        payload = to_primitive(evaluation)
        with self.connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            existing = connection.execute(
                "SELECT request_hash, payload FROM evaluations WHERE idempotency_key = ?", (idempotency_key,)
            ).fetchone()
            if existing:
                if existing["request_hash"] != request_hash:
                    raise StoreConflict("Idempotency key was already used with a different evaluation request")
                return json.loads(existing["payload"]), True
            connection.execute(
                """INSERT INTO evaluations
                   (evaluation_id, recommendation_id, case_id, request_hash, idempotency_key, payload, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (
                    evaluation.evaluation_id,
                    evaluation.recommendation.recommendation_id,
                    evaluation.case.case_id,
                    request_hash,
                    idempotency_key,
                    json.dumps(payload, sort_keys=True, separators=(",", ":")),
                    evaluation.generated_at,
                ),
            )
            self._audit(connection, "evaluation_created", actor, payload)
            return payload, False

    def get_evaluation(self, evaluation_id: str) -> dict[str, Any]:
        with self.connect() as connection:
            row = connection.execute(
                "SELECT payload FROM evaluations WHERE evaluation_id = ?", (evaluation_id,)
            ).fetchone()
        if not row:
            raise StoreNotFound("Evaluation not found")
        return json.loads(row["payload"])

    def record_approval(
        self,
        recommendation_id: str,
        *,
        decision: str,
        actor: str,
        rationale: str,
    ) -> dict[str, Any]:
        if decision not in {"approved", "rejected"}:
            raise StoreConflict("Decision must be approved or rejected")
        if not rationale.strip():
            raise StoreConflict("Approval rationale is required")
        approval = {
            "approval_id": str(uuid4()),
            "recommendation_id": recommendation_id,
            "decision": decision,
            "decided_by": actor,
            "rationale": rationale.strip(),
            "created_at": utc_now(),
        }
        with self.connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            if not connection.execute(
                "SELECT 1 FROM evaluations WHERE recommendation_id = ?", (recommendation_id,)
            ).fetchone():
                raise StoreNotFound("Recommendation not found")
            if connection.execute(
                "SELECT 1 FROM approvals WHERE recommendation_id = ?", (recommendation_id,)
            ).fetchone():
                raise StoreConflict("Recommendation already has an approval decision")
            connection.execute(
                """INSERT INTO approvals
                   (approval_id, recommendation_id, decision, decided_by, rationale, created_at)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                tuple(approval.values()),
            )
            self._audit(connection, "approval_recorded", actor, approval)
        return approval

    def record_outcome(
        self,
        recommendation_id: str,
        *,
        idempotency_key: str,
        request_hash: str,
        actual_recovered_units: str,
        realized_net_value: str,
        actor: str,
        note: str,
    ) -> tuple[dict[str, Any], bool]:
        outcome = {
            "outcome_id": str(uuid4()),
            "recommendation_id": recommendation_id,
            "actual_recovered_units": actual_recovered_units,
            "realized_net_value": realized_net_value,
            "recorded_by": actor,
            "note": note,
            "created_at": utc_now(),
        }
        with self.connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            existing = connection.execute(
                "SELECT request_hash, outcome_id, recommendation_id, actual_recovered_units, realized_net_value, recorded_by, note, created_at FROM outcomes WHERE idempotency_key = ?",
                (idempotency_key,),
            ).fetchone()
            if existing:
                if existing["request_hash"] != request_hash:
                    raise StoreConflict("Idempotency key was already used with a different outcome request")
                return dict(existing), True
            approval = connection.execute(
                "SELECT decision FROM approvals WHERE recommendation_id = ?", (recommendation_id,)
            ).fetchone()
            if not approval or approval["decision"] != "approved":
                raise StoreConflict("Outcome requires an approved recommendation")
            connection.execute(
                """INSERT INTO outcomes
                   (outcome_id, recommendation_id, idempotency_key, request_hash, actual_recovered_units,
                    realized_net_value, recorded_by, note, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    outcome["outcome_id"], recommendation_id, idempotency_key, request_hash,
                    actual_recovered_units, realized_net_value, actor, note, outcome["created_at"],
                ),
            )
            self._audit(connection, "outcome_recorded", actor, outcome)
        return outcome, False

    def audit_events(self) -> list[dict[str, Any]]:
        with self.connect() as connection:
            rows = connection.execute("SELECT * FROM audit_events ORDER BY sequence").fetchall()
        return [dict(row) for row in rows]

    def verify_audit_integrity(self) -> bool:
        previous_hash: str | None = None
        for row in self.audit_events():
            if row["previous_event_hash"] != previous_hash:
                return False
            event = {
                "event_id": row["event_id"],
                "event_type": row["event_type"],
                "actor": row["actor"],
                "payload": json.loads(row["payload"]),
                "previous_event_hash": row["previous_event_hash"],
                "created_at": row["created_at"],
            }
            canonical = json.dumps(event, sort_keys=True, separators=(",", ":"))
            if sha256(canonical.encode("utf-8")).hexdigest() != row["event_hash"]:
                return False
            previous_hash = row["event_hash"]
        return True
