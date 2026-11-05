"""Локальный репозиторий и рекурсивный обход зависимостей."""

import json
import re


def read_graph(path):
    """Прочитать JSON-объект, проверить имена вершин и ссылки."""
    with path.open(encoding="utf-8") as stream:
        graph = json.load(stream)
    if not isinstance(graph, dict):
        raise ValueError("ожидается объект с описаниями пакетов")
    for name, children in graph.items():
        if not re.fullmatch(r"[A-Z]+", name):
            raise ValueError(f"неверное имя вершины: {name}")
        if not isinstance(children, list):
            raise ValueError(f"{name}: нужен список зависимостей")
        for child in children:
            if not isinstance(child, str) or child not in graph:
                raise ValueError(f"{name}: неизвестная зависимость {child}")
    return graph


def traverse(root, lookup, exclude):
    """Построить списки смежности рекурсивным DFS, сохраняя обратные рёбра."""
    graph = {}

    def visit(name):
        """Зарегистрировать вершину до рекурсивного спуска."""
        if name in graph or (exclude and exclude in name):
            return
        children = sorted(set(lookup(name)))
        graph[name] = [child for child in children
                       if not exclude or exclude not in child]
        for child in graph[name]:
            visit(child)

    visit(root)
    return graph
