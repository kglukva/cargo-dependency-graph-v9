"""Тесты чтения записей sparse-индекса."""

import io
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from registry import dependencies, index_path


class RegistryTests(unittest.TestCase):
    def test_paths(self):
        """Проверить все четыре схемы размещения."""
        paths = ["1/a", "2/ab", "3/a/abc", "ab/cd/abcd"]
        self.assertEqual([index_path(p.split("/")[-1]) for p in paths], paths)

    def test_dependencies(self):
        """Пропустить отозванную запись и раскрыть псевдоним пакета."""
        data = (b'{"deps":[{"name":"alias","package":"real"}]}\n'
                b'{"yanked":true,"deps":[]}\n')
        with patch("registry.urlopen", return_value=io.BytesIO(data)):
            self.assertEqual(dependencies("https://example.org", "a"), ["real"])
