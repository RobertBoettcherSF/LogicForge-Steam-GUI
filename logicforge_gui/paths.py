"""DATA paths for Logic Forge shell (configurable via env / config.json)."""
from __future__ import annotations

import json
import os
from pathlib import Path

PKG_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = PKG_ROOT / "data" / "config.json"


def _load_file_config() -> dict:
    path = Path(os.environ.get("LOGICFORGE_CONFIG", str(DEFAULT_CONFIG))).expanduser()
    if not path.is_file():
        return {}
    try:
        with path.open(encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def config() -> dict:
    cfg = {
        "exercises_root": os.environ.get("LOGICFORGE_EXERCISES_ROOT", ""),
        "results_dir": os.environ.get("LOGICFORGE_RESULTS_DIR", ""),
        "locales_dir": os.environ.get("LOGICFORGE_LOCALES_DIR", ""),
        "locale": os.environ.get("LOGICFORGE_LOCALE", "en"),
    }
    file_cfg = _load_file_config()
    for key in cfg:
        if not cfg[key] and file_cfg.get(key):
            cfg[key] = str(file_cfg[key])
    if not cfg["results_dir"]:
        cfg["results_dir"] = str(Path.home() / ".logicforge" / "results")
    if not cfg["locales_dir"]:
        cfg["locales_dir"] = str(PKG_ROOT / "data" / "locales")
    return cfg


def exercises_root() -> Path | None:
    raw = config()["exercises_root"].strip()
    if not raw:
        return None
    p = Path(raw).expanduser().resolve()
    return p if p.is_dir() else None


def results_dir() -> Path:
    p = Path(config()["results_dir"]).expanduser().resolve()
    p.mkdir(parents=True, exist_ok=True)
    return p


def locales_dir() -> Path:
    return Path(config()["locales_dir"]).expanduser().resolve()
