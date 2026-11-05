"""Проверки DFS и тестового репозитория."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from graph import read_graph, traverse


class GraphTests(unittest.TestCase):
    def setUp(self):
        self.data = read_graph(Path("examples/graph.json"))

    def test_cycle_and_shared_child(self):
        graph = traverse("A", self.data.__getitem__, "")
        self.assertEqual(list(graph), ["A", "B", "D", "C"])
        self.assertEqual(graph, {k: self.data[k] for k in "ABCD"})

    def test_filter_before_lookup(self):
        graph = traverse("A", self.data.__getitem__, "B")
        self.assertEqual(graph, {"A": ["C"], "C": ["D"], "D": []})

    def test_isolated_and_filtered_roots(self):
        self.assertEqual(traverse("E", self.data.__getitem__, ""), {"E": []})
        self.assertEqual(traverse("E", self.data.__getitem__, "E"), {})

    def test_invalid_graph_files(self):
        """Отклонить неверную структуру и отсутствующие вершины."""
        import tempfile

        examples = [
            "[]", '{"a": []}', '{"A": "B"}',
            '{"A": ["B"]}', '{"A": [42]}', "{",
        ]
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "graph.json"
            for source in examples:
                with self.subTest(source=source):
                    path.write_text(source)
                    with self.assertRaises(ValueError):
                        read_graph(path)

    def test_self_cycle(self):
        """Самоссылка сохраняется без повторного раскрытия вершины."""
        self.assertEqual(traverse("A", lambda _: ["A"], ""), {"A": ["A"]})
