"""Чтение метаданных из sparse-индекса Cargo."""

import json
from urllib.request import urlopen


def index_path(name):
    """Сформировать относительный путь записи sparse-индекса."""
    name = name.lower()
    prefixes = {1: "1", 2: "2", 3: f"3/{name[:1]}"}
    prefix = prefixes.get(len(name), f"{name[:2]}/{name[2:4]}")
    return f"{prefix}/{name}"


def dependencies(base, name):
    """Вернуть имена зависимостей последней опубликованной активной версии."""
    url = f"{base.rstrip('/')}/{index_path(name)}"
    with urlopen(url, timeout=20) as response:
        records = [json.loads(line) for line in response if line.strip()]
    for record in reversed(records):
        if not record.get("yanked", False):
            names = {dep.get("package") or dep["name"] for dep in
                     record["deps"]}
            return sorted(names)
    raise ValueError(f"{name}: отсутствуют доступные версии")
