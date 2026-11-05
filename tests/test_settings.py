"""Проверки параметров через CLI."""

import subprocess
import tempfile
import unittest
from pathlib import Path


class SettingsTests(unittest.TestCase):
    def test_invalid_fields(self):
        """Для каждого параметра показать ошибку входных данных."""
        source = Path("examples/cargo.ini").read_text()
        cases = {
            "package = itoa": "package = !",
            "repository = https://index.crates.io": "repository = nowhere",
            "test_mode = false": "test_mode = sometimes",
            "image = graph.svg": "image = graph",
            "exclude =": "",
        }
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "test.ini"
            for original, replacement in cases.items():
                with self.subTest(field=original):
                    path.write_text(source.replace(original, replacement))
                    result = subprocess.run(
                        ["./run.sh", path], capture_output=True, text=True
                    )
                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn("Ошибка:", result.stderr)
