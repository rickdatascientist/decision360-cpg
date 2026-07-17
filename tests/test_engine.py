import json
import tempfile
import unittest
from dataclasses import replace
from decimal import Decimal
from pathlib import Path

from decision360.engine import DecisionInputError, evaluate_case
from decision360.ledger import DecisionLedger, LedgerStateError
from decision360.models import Action, DecisionCase, Policy


ROOT = Path(__file__).resolve().parents[1]


def sample_case() -> DecisionCase:
    payload = json.loads((ROOT / "examples" / "case_shortfall.json").read_text(encoding="utf-8"))
    return DecisionCase.from_dict(payload)


class EngineTests(unittest.TestCase):
    def test_shortfall_recommends_economic_expedite(self) -> None:
        evaluation = evaluate_case(sample_case())
        self.assertEqual(evaluation.projected_supply_units, Decimal("800"))
        self.assertEqual(evaluation.shortfall_units, Decimal("200"))
        self.assertEqual(evaluation.shortfall_ratio, Decimal("0.2"))
        self.assertEqual(evaluation.recommendation.action, Action.EXPEDITE)
        self.assertEqual(evaluation.recommendation.action_units, Decimal("150"))
        expedite = evaluation.scenarios[1]
        self.assertEqual(expedite.residual_shortfall_units, Decimal("50"))
        self.assertEqual(expedite.incremental_cost, Decimal("600"))
        self.assertEqual(expedite.estimated_net_benefit, Decimal("1200"))

    def test_policy_can_disable_expedite(self) -> None:
        evaluation = evaluate_case(sample_case(), Policy(allow_expedite=False))
        self.assertEqual(evaluation.recommendation.action, Action.MONITOR)
        self.assertIn("EXPEDITE_DISABLED_BY_POLICY", evaluation.recommendation.reason_codes)

    def test_uneconomic_expedite_is_not_recommended(self) -> None:
        case = replace(sample_case(), unit_margin=Decimal("2"), expedite_unit_cost=Decimal("4"))
        evaluation = evaluate_case(case)
        self.assertEqual(evaluation.recommendation.action, Action.MONITOR)
        self.assertIn("EXPEDITE_NOT_ECONOMIC_UNDER_REFERENCE_ASSUMPTIONS", evaluation.recommendation.reason_codes)

    def test_zero_forecast_has_no_shortfall(self) -> None:
        case = replace(sample_case(), forecast_units=Decimal("0"))
        evaluation = evaluate_case(case)
        self.assertEqual(evaluation.coverage_ratio, Decimal("1"))
        self.assertEqual(evaluation.shortfall_units, Decimal("0"))
        self.assertEqual(evaluation.recommendation.action, Action.MONITOR)

    def test_missing_provenance_is_rejected(self) -> None:
        case = sample_case()
        case = DecisionCase(**{**case.__dict__, "evidence": case.evidence[:-1]})
        with self.assertRaisesRegex(DecisionInputError, "max_expedite_units"):
            evaluate_case(case)

    def test_outcome_requires_human_approval(self) -> None:
        evaluation = evaluate_case(sample_case())
        with tempfile.TemporaryDirectory() as temp_dir:
            ledger = DecisionLedger(Path(temp_dir) / "ledger.jsonl")
            ledger.record_evaluation(evaluation)
            with self.assertRaises(LedgerStateError):
                ledger.record_outcome(
                    evaluation.recommendation.recommendation_id,
                    actual_recovered_units="100",
                    realized_net_value="500",
                    recorded_by="Rick",
                )
            ledger.record_approval(
                evaluation.recommendation.recommendation_id,
                decided_by="Rick",
                decision="approved",
                rationale="Synthetic reference approval for lifecycle testing",
            )
            ledger.record_outcome(
                evaluation.recommendation.recommendation_id,
                actual_recovered_units="100",
                realized_net_value="500",
                recorded_by="Rick",
            )
            self.assertEqual([event["event_type"] for event in ledger.events()], [
                "evaluation_created",
                "approval_recorded",
                "outcome_recorded",
            ])
            self.assertTrue(ledger.verify_integrity())

    def test_hash_chain_detects_tampering(self) -> None:
        evaluation = evaluate_case(sample_case())
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "ledger.jsonl"
            ledger = DecisionLedger(path)
            ledger.record_evaluation(evaluation)
            self.assertTrue(ledger.verify_integrity())
            content = path.read_text(encoding="utf-8").replace("SYNTHETIC-SKU-A", "TAMPERED-SKU")
            path.write_text(content, encoding="utf-8")
            self.assertFalse(ledger.verify_integrity())


if __name__ == "__main__":
    unittest.main()
