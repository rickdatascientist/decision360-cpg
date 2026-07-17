import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class CliComponentTests(unittest.TestCase):
    def test_cli_emits_structured_reference_evaluation(self) -> None:
        completed = subprocess.run(
            [sys.executable, "-m", "decision360.cli", "evaluate", "examples/case_shortfall.json"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["recommendation"]["action"], "expedite")
        self.assertTrue(payload["recommendation"]["human_approval_required"])
        self.assertEqual(payload["shortfall_units"], "200")
        self.assertEqual(len(payload["case"]["evidence"]), 6)


if __name__ == "__main__":
    unittest.main()
