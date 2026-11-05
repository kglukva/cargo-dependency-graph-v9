"""Пограничные случаи конфигурации без обращения к сети."""

import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from settings import KEYS, load_settings


class ValidationTests(unittest.TestCase):
    """Проверить обязательные поля и некорректные значения."""

    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        self.path = Path(self.folder.name) / "config.ini"
        self.values = {
            "package": "itoa",
            "repository": "https://index.crates.io",
            "test_mode": "false",
            "image": "graph.svg",
            "exclude": "",
        }

    def write_config(self):
        lines = [f"{key} = {value}" for key, value in self.values.items()]
        self.path.write_text("[graph]\n" + "\n".join(lines), encoding="utf-8")

    def test_missing_each_key(self):
        for key in KEYS:
            with self.subTest(key=key):
                value = self.values.pop(key)
                self.write_config()
                with self.assertRaisesRegex(ValueError, key):
                    load_settings(self.path)
                self.values[key] = value

    def test_bad_values(self):
        cases = [
            ("package", ""), ("package", "!"),
            ("repository", ""), ("repository", "ftp://example.org"),
            ("repository", "https://example.org:bad"),
            ("repository", "https://example.org/#fragment"),
            ("repository", "https://example.org/?query=yes"),
            ("repository", "https://user:password@example.org"),
            ("repository", "https://example .org"),
            ("repository", "https:///"),
            ("repository", "https://example.org:99999"),
            ("test_mode", "maybe"), ("image", ""),
            ("image", "graph.png"), ("image", "absent/graph.svg"),
            ("image", "directory.svg"), ("exclude", "A\x00B"),
        ]
        (self.path.parent / "directory.svg").mkdir()
        for key, value in cases:
            with self.subTest(key=key, value=value):
                original = self.values[key]
                self.values[key] = value
                self.write_config()
                with self.assertRaisesRegex(ValueError, key):
                    load_settings(self.path)
                self.values[key] = original

    def test_local_path_and_mode(self):
        self.values.update(package="A", test_mode="true",
                           repository="graph.json")
        self.write_config()
        with self.assertRaisesRegex(ValueError, "repository"):
            load_settings(self.path)
        (self.path.parent / "graph.json").write_text('{"A": []}')
        settings, local = load_settings(self.path)
        self.assertTrue(local)
        self.assertEqual(settings["package"], "A")

    def test_image_permissions(self):
        self.write_config()
        with patch("settings.os.access", return_value=False):
            with self.assertRaisesRegex(ValueError, "image"):
                load_settings(self.path)

    def test_valid_configuration(self):
        self.write_config()
        settings, local = load_settings(self.path)
        self.assertEqual(settings, self.values)
        self.assertFalse(local)
