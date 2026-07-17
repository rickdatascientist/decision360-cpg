import unittest
from pathlib import Path

from decision360.benchmark import run_suite


ROOT = Path(__file__).resolve().parents[2]


class BenchmarkTests(unittest.TestCase):
    def test_reference_suite_meets_all_thresholds(self) -> None:
        report = run_suite(ROOT / "benchmarks" / "suite.json")
        self.assertTrue(report["passed"])
        self.assertEqual(report["pass_rate"], 1.0)
        self.assertEqual(report["critical_pass_rate"], 1.0)
        self.assertEqual(report["case_count"], 8)
        self.assertLessEqual(report["latency"]["p95_ms"], 50.0)


if __name__ == "__main__":
    unittest.main()
