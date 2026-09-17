# LogicForge-Steam-GUI

Local-first GUI shell for **Logic Forge**. Lists headless Ada exercise cores and launches `make play` against a checkout of [LogicForge-Exercises](https://github.com/RobertBoettcherSF/LogicForge-Exercises).

Steamworks, Deck fullscreen, and JSON i18n are stubbed for later epics — v0.1 is meant to be tryable on a Linux desktop today.

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
