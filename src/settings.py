"""Чтение и проверка параметров графа."""

import configparser
import re
from pathlib import Path
from urllib.parse import urlsplit

KEYS = ("package", "repository", "test_mode", "image", "exclude")


def check_source(value, local, folder):
    """Проверить адрес индекса или путь относительно INI."""
    if local:
        if not (folder / value).is_file():
            raise ValueError("repository: файл не найден")
    else:
        url = urlsplit(value)
        if url.scheme not in {"https", "http"} or not url.hostname:
            raise ValueError("repository: нужен HTTP(S) URL")
        if url.query or url.fragment:
            raise ValueError("repository: нужен базовый URL индекса")
        _ = url.port


def load_settings(path):
    """Прочитать обязательные поля секции graph."""
    parser = configparser.ConfigParser(interpolation=None)
    with path.open(encoding="utf-8") as stream:
        parser.read_file(stream)
    if not parser.has_section("graph"):
        raise ValueError("отсутствует секция [graph]")
    section = parser["graph"]
    for key in KEYS:
        if key not in section:
            raise ValueError(f"отсутствует параметр {key}")
    mode = section.getboolean("test_mode")
    pattern = r"[A-Z]+" if mode else r"[A-Za-z0-9][A-Za-z0-9_-]*"
    if not re.fullmatch(pattern, section["package"]):
        raise ValueError("package: неверное имя пакета")
    check_source(section["repository"], mode, path.parent)
    if Path(section["image"]).suffix.lower() != ".svg":
        raise ValueError("image: укажите имя файла с расширением .svg")
    return dict(section), mode
