"""RESULTS store — append session outcomes as JSONL."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from logicforge_gui.paths import results_dir


def _store_path() -> Path:
    return results_dir() / "sessions.jsonl"


def record_session(
    exercise_id: str,
    exit_code: int,
    *,
    locale: str = "en",
    extra: dict[str, Any] | None = None,
) -> Path:
    entry = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "exercise_id": exercise_id,
        "exit_code": exit_code,
        "locale": locale,
    }
    if extra:
        entry["extra"] = extra
    path = _store_path()
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return path


def recent(limit: int = 20) -> list[dict[str, Any]]:
    path = _store_path()
    if not path.is_file():
        return []
    lines = path.read_text(encoding="utf-8").splitlines()
    out: list[dict[str, Any]] = []
    for line in lines[-limit:]:
        line = line.strip()
        if not line:
            continue
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return list(reversed(out))
