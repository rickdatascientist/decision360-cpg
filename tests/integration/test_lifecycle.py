import json
import tempfile
import unittest
from pathlib import Path

from decision360.engine import evaluate_case
from decision360.ledger import DecisionLedger, LedgerStateError
from decision360.models import DecisionCase, Policy


ROOT = Path(__file__).resolve().parents[2]


class DecisionLifecycleTests(unittest.TestCase):
    def test_evaluation_approval_outcome_is_a_valid_hash_chain(self) -> None:
        payload = json.loads((ROOT / "examples" / "case_shortfall.json").read_text(encoding="utf-8"))
        evaluation = evaluate_case(DecisionCase.from_dict(payload), Policy.from_dict(payload["policy"]))
        with tempfile.TemporaryDirectory() as temp_dir:
            ledger = DecisionLedger(Path(temp_dir) / "ledger.jsonl")
            ledger.record_evaluation(evaluation)
            ledger.record_approval(
                evaluation.recommendation.recommendation_id,
                decided_by="Synthetic Approver",
                decision="approved",
                rationale="Lifecycle integration test",
            )
            ledger.record_outcome(
                evaluation.recommendation.recommendation_id,
                actual_recovered_units="125",
                realized_net_value="900",
                recorded_by="Synthetic Operator",
            )
            self.assertTrue(ledger.verify_integrity())
            self.assertEqual(len(ledger.events()), 3)

    def test_rejected_recommendation_cannot_receive_outcome(self) -> None:
        payload = json.loads((ROOT / "examples" / "case_shortfall.json").read_text(encoding="utf-8"))
        evaluation = evaluate_case(DecisionCase.from_dict(payload))
        with tempfile.TemporaryDirectory() as temp_dir:
            ledger = DecisionLedger(Path(temp_dir) / "ledger.jsonl")
            ledger.record_evaluation(evaluation)
            ledger.record_approval(
                evaluation.recommendation.recommendation_id,
                decided_by="Synthetic Approver",
                decision="rejected",
                rationale="Capacity assumption rejected",
            )
            with self.assertRaises(LedgerStateError):
                ledger.record_outcome(
                    evaluation.recommendation.recommendation_id,
                    actual_recovered_units="0",
                    realized_net_value="0",
                    recorded_by="Synthetic Operator",
                )


if __name__ == "__main__":
    unittest.main()
