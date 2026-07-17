import json
import tempfile
import unittest
from pathlib import Path

from decision360.engine import evaluate_case
from decision360.maintenance import backup_database, verify_database
from decision360.models import DecisionCase
from decision360.store import SQLiteStore


ROOT = Path(__file__).resolve().parents[2]


class BackupRestoreTests(unittest.TestCase):
    def test_consistent_backup_restores_audited_evaluation(self) -> None:
        payload = json.loads((ROOT / "examples" / "case_shortfall.json").read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory() as temp_dir:
            source = Path(temp_dir) / "source.db"
            backup = Path(temp_dir) / "backup.db"
            store = SQLiteStore(source)
            evaluation = evaluate_case(DecisionCase.from_dict(payload))
            store.save_evaluation(evaluation, idempotency_key="backup-restore-001", request_hash=store.request_hash(payload), actor="Backup Test")
            backup_database(source, backup)
            restored = SQLiteStore(backup)
            self.assertEqual(restored.get_evaluation(evaluation.evaluation_id)["case"]["case_id"], payload["case_id"])
            self.assertEqual(restored.schema_version(), 1)
            self.assertTrue(verify_database(backup))


if __name__ == "__main__":
    unittest.main()
