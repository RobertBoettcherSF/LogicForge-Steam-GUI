"""v0.1 Tk shell: list Logic Forge cores and launch make play."""
from __future__ import annotations

import json
import os
import subprocess
import threading
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "data" / "exercises.json"


def exercises_root() -> Path | None:
    raw = os.environ.get("LOGICFORGE_EXERCISES_ROOT", "").strip()
    if not raw:
        return None
    p = Path(raw).expanduser().resolve()
    return p if p.is_dir() else None


def load_catalog() -> list[dict]:
    with CATALOG.open(encoding="utf-8") as f:
        return json.load(f)


class ShellApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Logic Forge — Exercise Shell v0.1")
        self.geometry("720x480")
        self._busy = False

        top = ttk.Frame(self, padding=8)
        top.pack(fill=tk.X)
        self.root_var = tk.StringVar(
            value=str(exercises_root() or "(set LOGICFORGE_EXERCISES_ROOT)")
        )
        ttk.Label(top, text="Cores root:").pack(side=tk.LEFT)
        ttk.Entry(top, textvariable=self.root_var, width=70).pack(
            side=tk.LEFT, fill=tk.X, expand=True, padx=4
        )

        mid = ttk.Frame(self, padding=8)
        mid.pack(fill=tk.BOTH, expand=True)
        self.listbox = tk.Listbox(mid, font=("TkDefaultFont", 11))
        scroll = ttk.Scrollbar(mid, orient=tk.VERTICAL, command=self.listbox.yview)
        self.listbox.configure(yscrollcommand=scroll.set)
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self._items = load_catalog()
        for item in self._items:
            self.listbox.insert(tk.END, f"{item['title']}  ({item['id']})")
        # Prefer sequence_match if present
        for i, item in enumerate(self._items):
            if item["id"] == "sequence_match":
                self.listbox.selection_set(i)
                self.listbox.see(i)
                break
        else:
            if self._items:
                self.listbox.selection_set(0)

        bottom = ttk.Frame(self, padding=8)
        bottom.pack(fill=tk.X)
        self.status = tk.StringVar(value="Ready")
        ttk.Button(bottom, text="Play", command=self.on_play).pack(side=tk.LEFT)
        ttk.Label(bottom, textvariable=self.status).pack(side=tk.LEFT, padx=12)

    def on_play(self) -> None:
        if self._busy:
            return
        sel = self.listbox.curselection()
        if not sel:
            messagebox.showinfo("Logic Forge", "Select an exercise first.")
            return
        item = self._items[sel[0]]
        root = Path(self.root_var.get()).expanduser()
        if not root.is_dir():
            messagebox.showerror(
                "Logic Forge",
                "Set LOGICFORGE_EXERCISES_ROOT to your LogicForge-Exercises clone.",
            )
            return
        exercise_dir = root / item["id"]
        if not exercise_dir.is_dir():
            messagebox.showerror(
                "Logic Forge",
                f"Missing folder: {exercise_dir}",
            )
            return
        self._busy = True
        self.status.set(f"Playing {item['id']}… (finish the CLI, then return here)")
        threading.Thread(target=self._run_play, args=(exercise_dir, item["id"]), daemon=True).start()

    def _run_play(self, exercise_dir: Path, exercise_id: str) -> None:
        try:
            proc = subprocess.run(
                ["make", "play"],
                cwd=str(exercise_dir),
                check=False,
            )
            code = proc.returncode
            msg = f"{exercise_id} finished — exit {code}"
        except Exception as exc:  # noqa: BLE001
            code = -1
            msg = f"{exercise_id} failed: {exc}"
        self.after(0, lambda: self._done(msg, code))

    def _done(self, msg: str, code: int) -> None:
        self._busy = False
        self.status.set(msg)
        if code == 0:
            messagebox.showinfo("Logic Forge", msg)
        else:
            messagebox.showwarning("Logic Forge", msg)


def main_cli() -> None:
    """Headless list + launch (no display required)."""
    import sys

    items = load_catalog()
    root = exercises_root()
    print(f"Logic Forge shell v0.1 — {len(items)} exercises")
    print(f"Cores root: {root or '(unset LOGICFORGE_EXERCISES_ROOT)'}")
    for i, item in enumerate(items, 1):
        print(f"  {i:3d}. {item['id']}")
    if not root:
        print("Set LOGICFORGE_EXERCISES_ROOT to launch.", file=sys.stderr)
        raise SystemExit(2)
    choice = input("Number to play (blank=quit): ").strip()
    if not choice:
        return
    idx = int(choice) - 1
    item = items[idx]
    exercise_dir = root / item["id"]
    print(f"Running make play in {exercise_dir} …")
    raise SystemExit(subprocess.call(["make", "play"], cwd=str(exercise_dir)))


def main() -> None:
    import sys

    if "--cli" in sys.argv or not os.environ.get("DISPLAY"):
        main_cli()
        return
    app = ShellApp()
    app.mainloop()


if __name__ == "__main__":
    main()
