"""Optional Steamworks hooks — local try stays SDK-free.

Enable when:
  - LOGICFORGE_STEAM is not 0/false, and
  - steam_api / libsteam_api is loadable, or LOGICFORGE_STEAM=force for dry-run True

This does not ship the proprietary Steamworks SDK. It only probes the
environment and exposes init/shutdown/status for the shell.
"""
from __future__ import annotations

import ctypes
import os
from dataclasses import dataclass
from pathlib import Path


@dataclass
class SteamStatus:
    available: bool
    reason: str
    app_id: str | None = None


_initialized = False
_lib = None
_status = SteamStatus(False, "not initialized")


def _env_force_off() -> bool:
    return os.environ.get("LOGICFORGE_STEAM", "1").strip().lower() in {
        "0",
        "false",
        "no",
        "off",
    }


def _env_force_dry() -> bool:
    return os.environ.get("LOGICFORGE_STEAM", "").strip().lower() in {
        "force",
        "dry",
        "simulate",
    }


def _find_app_id() -> str | None:
    for key in ("SteamAppId", "SteamGameId", "LOGICFORGE_STEAM_APP_ID"):
        val = os.environ.get(key, "").strip()
        if val:
            return val
    for base in (Path.cwd(), Path(__file__).resolve().parents[1]):
        marker = base / "steam_appid.txt"
        if marker.is_file():
            return marker.read_text(encoding="utf-8").strip().splitlines()[0].strip() or None
    return None


def _try_load_lib() -> tuple[object | None, str]:
    names = [
        os.environ.get("LOGICFORGE_STEAM_API", "").strip(),
        "libsteam_api.so",
        "steam_api64.dll",
        "steam_api.dll",
        "libsteam_api.dylib",
    ]
    for name in names:
        if not name:
            continue
        try:
            return ctypes.CDLL(name), name
        except OSError:
            continue
    return None, "steam_api library not found"


def status() -> SteamStatus:
    return _status


def init() -> bool:
    """Attempt Steam API init. Always safe for local non-Steam runs."""
    global _initialized, _lib, _status

    if _env_force_off():
        _status = SteamStatus(False, "disabled via LOGICFORGE_STEAM=0")
        return False

    app_id = _find_app_id()

    if _env_force_dry():
        _initialized = True
        _status = SteamStatus(True, "dry-run (LOGICFORGE_STEAM=force)", app_id)
        return True

    lib, how = _try_load_lib()
    if lib is None:
        _status = SteamStatus(False, how, app_id)
        return False

    _lib = lib
    # Real SteamAPI_Init would be called here once the SDK is linked.
    # Without official headers/bindings we only report library presence.
    _initialized = True
    _status = SteamStatus(
        True,
        f"library loaded ({how}); wire SteamAPI_Init when SDK is available",
        app_id,
    )
    return True


def shutdown() -> None:
    global _initialized, _lib, _status
    if not _initialized:
        return
    _lib = None
    _initialized = False
    _status = SteamStatus(False, "shutdown")


def achievement_unlock(api_name: str) -> bool:
    """Placeholder achievement write — no-op until SDK is linked."""
    if not _initialized or _env_force_off():
        return False
    # Future: SteamUserStats()->SetAchievement(api_name); StoreStats()
    _ = api_name
    return _env_force_dry()
