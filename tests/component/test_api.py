import json
import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

from decision360.api import create_app
from decision360.auth import ApiKeyAuth


ROOT = Path(__file__).resolve().parents[2]
OPERATOR = "operator-token-123456"
APPROVER = "approver-token-123456"
AUDITOR = "auditor-token-1234567"


def auth() -> ApiKeyAuth:
    return ApiKeyAuth.from_mapping(
        {
            OPERATOR: {"actor": "Synthetic Operator", "roles": ["operator", "viewer"]},
            APPROVER: {"actor": "Synthetic Approver", "roles": ["approver", "viewer"]},
            AUDITOR: {"actor": "Synthetic Auditor", "roles": ["auditor", "viewer"]},
        }
    )


def case_payload() -> dict:
    return json.loads((ROOT / "examples" / "case_shortfall.json").read_text(encoding="utf-8"))


class ApiComponentTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        app = create_app(database_path=Path(self.temp.name) / "api.db", auth=auth())
        self.client = TestClient(app)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_static_ui_and_health_are_public(self) -> None:
        self.assertEqual(self.client.get("/healthz").json(), {"status": "ok", "audit_integrity": True})
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("PUBLIC REFERENCE BETA", response.text)

    def test_authentication_and_role_boundaries(self) -> None:
        response = self.client.post(
            "/api/v1/evaluations",
            json=case_payload(),
            headers={"Idempotency-Key": "auth-boundary-001"},
        )
        self.assertEqual(response.status_code, 401)
        created = self.client.post(
            "/api/v1/evaluations",
            json=case_payload(),
            headers={"X-API-Key": OPERATOR, "Idempotency-Key": "auth-boundary-002"},
        ).json()["evaluation"]
        forbidden = self.client.post(
            f"/api/v1/recommendations/{created['recommendation']['recommendation_id']}/approval",
            json={"decision": "approved", "rationale": "Operator must not approve"},
            headers={"X-API-Key": OPERATOR},
        )
        self.assertEqual(forbidden.status_code, 403)

    def test_idempotent_evaluation_and_conflict(self) -> None:
        headers = {"X-API-Key": OPERATOR, "Idempotency-Key": "same-request-001"}
        first = self.client.post("/api/v1/evaluations", json=case_payload(), headers=headers)
        second = self.client.post("/api/v1/evaluations", json=case_payload(), headers=headers)
        changed = case_payload()
        changed["forecast_units"] = 1100
        conflict = self.client.post("/api/v1/evaluations", json=changed, headers=headers)
        self.assertEqual(first.status_code, 201)
        self.assertEqual(second.status_code, 200)
        self.assertTrue(second.json()["replayed"])
        self.assertEqual(first.json()["evaluation"]["evaluation_id"], second.json()["evaluation"]["evaluation_id"])
        self.assertEqual(conflict.status_code, 409)

    def test_full_api_lifecycle_and_audit(self) -> None:
        evaluation = self.client.post(
            "/api/v1/evaluations",
            json=case_payload(),
            headers={"X-API-Key": OPERATOR, "Idempotency-Key": "lifecycle-eval-001"},
        ).json()["evaluation"]
        recommendation_id = evaluation["recommendation"]["recommendation_id"]
        approval = self.client.post(
            f"/api/v1/recommendations/{recommendation_id}/approval",
            json={"decision": "approved", "rationale": "Synthetic lifecycle approval"},
            headers={"X-API-Key": APPROVER},
        )
        outcome = self.client.post(
            f"/api/v1/recommendations/{recommendation_id}/outcomes",
            json={"actual_recovered_units": 125, "realized_net_value": 900, "note": "Synthetic outcome"},
            headers={"X-API-Key": OPERATOR, "Idempotency-Key": "lifecycle-outcome-001"},
        )
        audit = self.client.get("/api/v1/audit/integrity", headers={"X-API-Key": AUDITOR})
        self.assertEqual(approval.status_code, 201)
        self.assertEqual(outcome.status_code, 201)
        self.assertEqual(audit.json(), {"valid": True, "event_count": 3})

    def test_governed_tool_boundary_refuses_writes(self) -> None:
        response = self.client.post(
            "/api/v1/tools/record_approval",
            json={"arguments": {}},
            headers={"X-API-Key": OPERATOR},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "refused")
        self.assertEqual(response.json()["reason"], "TOOL_NOT_ALLOW_LISTED")


if __name__ == "__main__":
    unittest.main()
