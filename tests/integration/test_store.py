import json
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from decision360.engine import evaluate_case
from decision360.models import DecisionCase, Policy
from decision360.store import SQLiteStore


ROOT = Path(__file__).resolve().parents[2]


class StoreIntegrationTests(unittest.TestCase):
    def test_concurrent_idempotent_evaluation_has_one_effect(self) -> None:
        payload = json.loads((ROOT / "examples" / "case_shortfall.json").read_text(encoding="utf-8"))
        evaluation = evaluate_case(DecisionCase.from_dict(payload), Policy.from_dict(payload["policy"]))
        with tempfile.TemporaryDirectory() as temp_dir:
            store = SQLiteStore(Path(temp_dir) / "store.db")
            request_hash = store.request_hash(payload)

            def save(_: int):
                return store.save_evaluation(
                    evaluation,
                    idempotency_key="concurrent-idempotency-001",
                    request_hash=request_hash,
                    actor="Concurrency Test",
                )

            with ThreadPoolExecutor(max_workers=5) as executor:
                results = list(executor.map(save, range(5)))
            self.assertEqual(sum(not replayed for _, replayed in results), 1)
            self.assertEqual(len(store.audit_events()), 1)
            self.assertTrue(store.verify_audit_integrity())

    def test_database_audit_tampering_is_detected(self) -> None:
        payload = json.loads((ROOT / "examples" / "case_shortfall.json").read_text(encoding="utf-8"))
        evaluation = evaluate_case(DecisionCase.from_dict(payload))
        with tempfile.TemporaryDirectory() as temp_dir:
            store = SQLiteStore(Path(temp_dir) / "store.db")
            store.save_evaluation(
                evaluation,
                idempotency_key="tamper-test-001",
                request_hash=store.request_hash(payload),
                actor="Tamper Test",
            )
            with store.connect() as connection:
                connection.execute("UPDATE audit_events SET actor = 'Tampered Actor' WHERE sequence = 1")
            self.assertFalse(store.verify_audit_integrity())


if __name__ == "__main__":
    unittest.main()
