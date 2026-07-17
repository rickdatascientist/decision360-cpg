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

    def test_ui_uses_safe_text_rendering_and_role_separation_guidance(self) -> None:
        html = (ROOT / "src" / "decision360" / "static" / "index.html").read_text(encoding="utf-8")
        script = (ROOT / "src" / "decision360" / "static" / "app.js").read_text(encoding="utf-8")
        self.assertIn("separate approver key", html)
        self.assertIn("textContent", script)
        self.assertNotIn("innerHTML", script)
        self.assertNotIn("localStorage", script)


if __name__ == "__main__":
    unittest.main()
