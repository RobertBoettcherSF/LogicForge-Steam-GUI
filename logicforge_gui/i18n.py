"""JSON i18n loader for Logic Forge shell and exercise string keys."""
from __future__ import annotations

import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOCALES_DIR = ROOT / "data" / "locales"

_cache: dict[str, dict[str, str]] = {}
_locale = os.environ.get("LOGICFORGE_LOCALE", "en").strip() or "en"


def set_locale(locale: str) -> None:
    global _locale
    _locale = (locale or "en").strip() or "en"


def get_locale() -> str:
    return _locale


def available_locales() -> list[str]:
    return sorted(p.stem for p in LOCALES_DIR.glob("*.json"))


def _load(locale: str) -> dict[str, str]:
    if locale in _cache:
        return _cache[locale]
    path = LOCALES_DIR / f"{locale}.json"
    if not path.is_file():
        path = LOCALES_DIR / "en.json"
    with path.open(encoding="utf-8") as f:
        data = json.load(f)
    _cache[locale] = {str(k): str(v) for k, v in data.items()}
    return _cache[locale]


def t(key: str, locale: str | None = None, **kwargs: object) -> str:
    loc = locale or _locale
    table = _load(loc)
    text = table.get(key)
    if text is None and loc != "en":
        text = _load("en").get(key)
    if text is None:
        text = key
    if kwargs:
        try:
            return text.format(**kwargs)
        except (KeyError, ValueError):
            return text
    return text


def instruction_key(exercise_id: str) -> str:
    return f"{exercise_id}.instruction"
