"""Точка входа CLI."""

import argparse
import configparser
import sys
from functools import partial
from pathlib import Path

from graph import read_graph, traverse
from registry import dependencies
from settings import load_settings


def run(path):
    """Построить граф и вывести его списки смежности."""
    settings, local = load_settings(path)
    root = settings["package"]
    if local:
        records = read_graph(path.parent / settings["repository"])
        if root not in records:
            raise ValueError(f"пакет {root} отсутствует в репозитории")
        lookup = records.__getitem__
    else:
        lookup = partial(dependencies, settings["repository"])
    graph = traverse(root, lookup, settings["exclude"])
    for name, children in graph.items():
        print(f"{name}: {' '.join(children)}".rstrip())


def main():
    """Прочитать аргумент и сообщить об ошибках в stderr."""
    parser = argparse.ArgumentParser()
    parser.add_argument("config", type=Path, help="путь к INI")
    args = parser.parse_args()
    try:
        run(args.config)
    except (ValueError, OSError, configparser.Error) as error:
        sys.exit(f"Ошибка: {error}")


if __name__ == "__main__":
    main()
