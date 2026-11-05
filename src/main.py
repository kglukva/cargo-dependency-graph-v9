"""Точка входа CLI."""

import argparse
import configparser
import sys
from pathlib import Path

from registry import dependencies
from settings import load_settings


def run(path):
    """Напечатать прямые зависимости из индекса Cargo."""
    settings, local = load_settings(path)
    if local:
        raise ValueError("тестовый репозиторий доступен с этапа 3")
    for name in dependencies(settings["repository"], settings["package"]):
        print(name)


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
