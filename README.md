# LogicForge-Steam-GUI

Local-first GUI shell for **Logic Forge**. Lists headless Ada exercise cores and launches `make play` against a checkout of [LogicForge-Exercises](https://github.com/RobertBoettcherSF/LogicForge-Exercises).

Steamworks, Deck fullscreen, and JSON i18n are stubbed for later epics — v0.1 is meant to be tryable on a Linux desktop today.

## Locales (JSON i18n)

```bash
export LOGICFORGE_LOCALE=en   # or de
python3 -m logicforge_gui --locale de
```

String tables live in `data/locales/*.json` (shell UI + `exercise_id.instruction` / `.prompt` keys matching the Ada cores).

## Steamworks (optional)

Local runs stay Steam-free. Optional probes:

```bash
export LOGICFORGE_STEAM=0          # force off
export LOGICFORGE_STEAM=force      # dry-run "available" without SDK
export LOGICFORGE_STEAM_APP_ID=480 # or place steam_appid.txt in cwd
```

When `libsteam_api.so` (or platform equivalent) is on the library path, the shell reports it loaded. Full `SteamAPI_Init` waits on linking the official SDK — not redistributed here.

## Deck / fullscreen

```bash
export LOGICFORGE_DECK_FULLSCREEN=1   # or SteamDeck=1
python3 -m logicforge_gui
```

Escape exits fullscreen. Auto-detects `SteamDeck=1` / gamescope desktop hints.

## Requirements

- Python 3.10+ with tkinter (`python3-tk` on Debian/Ubuntu)
- A local clone of LogicForge-Exercises with GNAT available for `make play`

## Quick start

```bash
export LOGICFORGE_EXERCISES_ROOT=/path/to/LogicForge-Exercises
python3 -m logicforge_gui
```

Or:

```bash
LOGICFORGE_EXERCISES_ROOT=/path/to/LogicForge-Exercises ./run.sh
```

Pick an exercise (e.g. Sequence Match), click **Play**, and complete the CLI session in the spawned terminal process. The shell shows the exit status when it finishes.

## Layout

| Path | Role |
|------|------|
| `logicforge_gui/` | Tk list/launch shell |
| `data/exercises.json` | Catalog of core ids/titles |
| `stubs/` | Placeholders for Steamworks / Deck / i18n |

## Next epics

1. Steamworks init + achievements hooks (`stubs/steamworks.py`)
2. Steam Deck / Linux fullscreen path (`stubs/deck.py`)
3. JSON i18n string table (`stubs/i18n.py`)
