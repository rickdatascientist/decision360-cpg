import json
import math
import tempfile
import time
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

from decision360.api import create_app
from decision360.auth import ApiKeyAuth


ROOT = Path(__file__).resolve().parents[2]
TOKEN = "performance-token-0001"


class ApiPerformanceTests(unittest.TestCase):
    def test_reference_api_p95_is_below_500_ms(self) -> None:
        payload = json.loads((ROOT / "examples" / "case_shortfall.json").read_text(encoding="utf-8"))
        auth = ApiKeyAuth.from_mapping({TOKEN: {"actor": "Load Test", "roles": ["operator"]}})
        with tempfile.TemporaryDirectory() as temp_dir:
            client = TestClient(create_app(database_path=Path(temp_dir) / "performance.db", auth=auth))
            latencies = []
            for index in range(40):
                started = time.perf_counter()
                response = client.post(
                    "/api/v1/evaluations",
                    json={**payload, "case_id": f"PERF-{index:03d}"},
                    headers={"X-API-Key": TOKEN, "Idempotency-Key": f"performance-{index:04d}"},
                )
                latencies.append((time.perf_counter() - started) * 1000)
                self.assertEqual(response.status_code, 201)
        p95 = sorted(latencies)[math.ceil(0.95 * len(latencies)) - 1]
        self.assertLess(p95, 500.0, f"reference API p95 was {p95:.2f} ms")


if __name__ == "__main__":
    unittest.main()
