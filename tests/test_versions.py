"""Проверки версий локальных пакетов и вывода CLI."""

import contextlib
import io
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from graph import read_package
from main import run


class VersionTests(unittest.TestCase):
    """Проверить новые объекты, старые списки и вывод цикла."""

    def test_package_versions(self):
        self.assertEqual(read_package([]), ([], "1.0.0"))
        self.assertEqual(
            read_package({"version": "2.3.4", "dependencies": ["B"]}),
            (["B"], "2.3.4"),
        )

    def test_invalid_version(self):
        for version in [None, 1, "", "1.0", "wrong"]:
            with self.subTest(version=version):
                with self.assertRaises(ValueError):
                    read_package({"version": version, "dependencies": []})

    def test_local_output(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            run(Path("examples/local.ini"))
        self.assertEqual(output.getvalue().splitlines(), [
            "A@1.0.0: B@1.0.0 C@1.0.0",
            "B@1.0.0: D@1.0.0",
            "D@1.0.0: B@1.0.0",
            "C@1.0.0: D@1.0.0",
        ])
