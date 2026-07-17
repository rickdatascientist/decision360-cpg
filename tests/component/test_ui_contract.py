import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class UiContractTests(unittest.TestCase):
    def test_accessible_reference_landmarks_and_status_regions_exist(self) -> None:
        html = (ROOT / "src" / "decision360" / "static" / "index.html").read_text(encoding="utf-8")
        self.assertIn('<html lang="en">', html)
        self.assertIn('<main>', html)
        self.assertIn('role="alert"', html)
        self.assertGreaterEqual(html.count('role="status"'), 3)
        self.assertIn('aria-labelledby="result-title"', html)
        self.assertIn('type="password"', html)
        self.assertIn('id="workflow-nav"', html)
        self.assertIn('role="group"', html)

    def test_ui_uses_safe_text_rendering_and_role_separation_guidance(self) -> None:
        html = (ROOT / "src" / "decision360" / "static" / "index.html").read_text(encoding="utf-8")
        script = (ROOT / "src" / "decision360" / "static" / "app.js").read_text(encoding="utf-8")
        self.assertIn("separate approver key", html)
        self.assertIn("textContent", script)
        self.assertNotIn("innerHTML", script)
        self.assertNotIn("localStorage", script)
        self.assertEqual(script.count('executable: false'), 4)
        self.assertEqual(script.count('executable: true'), 1)
        self.assertIn('aria-pressed', script)


if __name__ == "__main__":
    unittest.main()
