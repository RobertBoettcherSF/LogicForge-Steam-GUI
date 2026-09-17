"""Steam Deck / Linux display helpers for the Logic Forge shell."""
from __future__ import annotations

import os
from typing import Any


def prefer_deck_fullscreen() -> bool:
    """True when Deck-like env or LOGICFORGE_DECK_FULLSCREEN=1."""
    if os.environ.get("LOGICFORGE_DECK_FULLSCREEN", "").strip() in {"1", "true", "yes"}:
        return True
    # Steam Deck / gamescope hints
    if os.environ.get("SteamDeck", "").strip() == "1":
        return True
    if "gamescope" in os.environ.get("XDG_CURRENT_DESKTOP", "").lower():
        return True
    # Common Deck resolution when unset override
    return False


def apply_window(app: Any) -> None:
    """Apply fullscreen / geometry to a Tk root if preferred."""
    if not prefer_deck_fullscreen():
        # Comfortable windowed default; still honor explicit geometry
        return
    try:
        app.attributes("-fullscreen", True)
    except Exception:
        try:
            app.state("zoomed")
        except Exception:
            app.geometry("1280x800")
    # Escape leaves fullscreen on Deck-ish sessions
    def _leave(_event=None) -> None:
        try:
            app.attributes("-fullscreen", False)
        except Exception:
            pass

    app.bind("<Escape>", _leave)
