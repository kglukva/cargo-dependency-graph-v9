"""Чтение и проверка параметров графа."""

import configparser
import os
import re
from pathlib import Path
from urllib.parse import urlsplit

KEYS = ("package", "repository", "test_mode", "image", "exclude")


def check_source(value, local, folder):
    """Проверить адрес индекса или путь относительно INI."""
    if not value:
        raise ValueError("repository: требуется адрес или путь")
    if local:
        if not (folder / value).is_file():
            raise ValueError("repository: файл не найден")
        return
    check_url(value)


def check_url(value):
    """Проверить базовый HTTP(S) URL sparse-индекса."""
    if any(char.isspace() for char in value):
        raise ValueError("repository: пробелы в URL")
    url = urlsplit(value)
    if url.scheme not in {"https", "http"} or not url.hostname:
        raise ValueError("repository: нужен HTTP(S) URL")
    if any((url.query, url.fragment, url.username, url.password)):
        raise ValueError("repository: нужен базовый URL без учётных данных")
    try:
        _ = url.port
    except ValueError as error:
        raise ValueError("repository: неверный номер порта") from error


def check_text(value, key):
    """Отклонить управляющие символы в текстовом параметре."""
    if any(not char.isprintable() for char in value):
        raise ValueError(f"{key}: недопустимые управляющие символы")


def check_image(value, folder):
    """Проверить имя SVG и доступность каталога без создания файла."""
    path = folder / value
    if not value or value.endswith(("/", "\\")):
        raise ValueError("image: требуется имя SVG-файла")
    if path.suffix.lower() != ".svg":
        raise ValueError("image: укажите имя файла с расширением .svg")
    if not path.parent.is_dir():
        raise ValueError("image: каталог не существует")
    if path.exists() and not path.is_file():
        raise ValueError("image: путь занят каталогом")
    target = path if path.exists() else path.parent
    if not os.access(target, os.W_OK):
        raise ValueError("image: отсутствует доступ для записи")


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
        check_text(section[key], key)
    try:
        mode = section.getboolean("test_mode")
    except ValueError as error:
        raise ValueError("test_mode: ожидается true или false") from error
    pattern = r"[A-Z]+" if mode else r"[A-Za-z0-9][A-Za-z0-9_-]*"
    if not re.fullmatch(pattern, section["package"]):
        raise ValueError("package: неверное имя пакета")
    check_source(section["repository"], mode, path.parent)
    check_image(section["image"], path.parent)
    return dict(section), mode
