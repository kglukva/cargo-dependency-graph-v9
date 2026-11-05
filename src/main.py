"""Точка входа CLI."""

import argparse
import configparser
import sys
from pathlib import Path

from settings import KEYS, load_settings


def run(path):
    """Вывести параметры прототипа."""
    settings, _ = load_settings(path)
    for key in KEYS:
        print(f"{key}={settings[key]}")


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
