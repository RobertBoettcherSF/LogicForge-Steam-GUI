"""Tk / CLI shell: list Logic Forge cores and launch make play (JSON i18n)."""
from __future__ import annotations

import json
import os
import subprocess
import threading
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk

from logicforge_gui.deck import apply_window
from logicforge_gui import steamworks as steam
from logicforge_gui import results as results_store
from logicforge_gui.menu import filter_catalog, theme_for, theme_names
from logicforge_gui.paths import exercises_root as paths_exercises_root, results_dir
from logicforge_gui.i18n import (
    available_locales,
    get_locale,
    instruction_key,
    set_locale,
    t,
)

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "data" / "exercises.json"


def exercises_root() -> Path | None:
    return paths_exercises_root()


def load_catalog() -> list[dict]:
    with CATALOG.open(encoding="utf-8") as f:
        return json.load(f)


class ShellApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title(t("shell.title"))
        self.geometry("720x520")
        apply_window(self)
        steam.init()
        st = steam.status()
        self._steam_var = tk.StringVar(
            value=f"Steam: {'on' if st.available else 'off'} — {st.reason}"
        )
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self._busy = False

        top = ttk.Frame(self, padding=8)
        top.pack(fill=tk.X)
        self.root_var = tk.StringVar(
            value=str(exercises_root() or "(set LOGICFORGE_EXERCISES_ROOT)")
        )
        ttk.Label(top, text=t("shell.cores_root")).pack(side=tk.LEFT)
        ttk.Entry(top, textvariable=self.root_var, width=56).pack(
            side=tk.LEFT, fill=tk.X, expand=True, padx=4
        )
        ttk.Label(top, text=t("shell.locale")).pack(side=tk.LEFT, padx=(8, 0))
        self.locale_var = tk.StringVar(value=get_locale())
        loc = ttk.Combobox(
            top,
            textvariable=self.locale_var,
            values=available_locales() or ["en"],
            width=6,
            state="readonly",
        )
        loc.pack(side=tk.LEFT)
        loc.bind("<<ComboboxSelected>>", self._on_locale)
        ttk.Label(top, text="Theme:").pack(side=tk.LEFT, padx=(8, 0))
        self.theme_var = tk.StringVar(value="All")
        theme = ttk.Combobox(
            top,
            textvariable=self.theme_var,
            values=theme_names(),
            width=14,
            state="readonly",
        )
        theme.pack(side=tk.LEFT)
        theme.bind("<<ComboboxSelected>>", self._on_theme)

        mid = ttk.Frame(self, padding=8)
        mid.pack(fill=tk.BOTH, expand=True)
        self.listbox = tk.Listbox(mid, font=("TkDefaultFont", 11))
        scroll = ttk.Scrollbar(mid, orient=tk.VERTICAL, command=self.listbox.yview)
        self.listbox.configure(yscrollcommand=scroll.set)
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.listbox.bind("<<ListboxSelect>>", self._on_select)

        preview = ttk.LabelFrame(self, text=t("shell.instruction_preview"), padding=8)
        preview.pack(fill=tk.X, padx=8, pady=(0, 4))
        self.preview_var = tk.StringVar(value="")
        ttk.Label(preview, textvariable=self.preview_var, wraplength=680).pack(fill=tk.X)

        self._items = load_catalog()
        self._refill_list()
        for i, item in enumerate(self._items):
            if item["id"] == "sequence_match":
                self.listbox.selection_set(i)
                self.listbox.see(i)
                break
        else:
            if self._items:
                self.listbox.selection_set(0)
        self._on_select()

        bottom = ttk.Frame(self, padding=8)
        bottom.pack(fill=tk.X)
        self.status = tk.StringVar(value=t("shell.ready"))
        self.play_btn = ttk.Button(bottom, text=t("shell.play"), command=self.on_play)
        self.play_btn.pack(side=tk.LEFT)
        ttk.Button(bottom, text="Results", command=self.on_results).pack(
            side=tk.LEFT, padx=6
        )
        ttk.Label(bottom, textvariable=self.status).pack(side=tk.LEFT, padx=12)
        ttk.Label(bottom, textvariable=self._steam_var).pack(side=tk.RIGHT)

    def _refill_list(self) -> None:
        theme = self.theme_var.get() if hasattr(self, "theme_var") else "All"
        self._items = filter_catalog(self._all_items, theme)
        self.listbox.delete(0, tk.END)
        for item in self._items:
            label = f"{item['title']}  [{theme_for(item['id'])}]  ({item['id']})"
            self.listbox.insert(tk.END, label)
        if self._items:
            self.listbox.selection_set(0)
            self._on_select()

    def _on_theme(self, _event=None) -> None:
        self._refill_list()

    def _on_locale(self, _event=None) -> None:
        set_locale(self.locale_var.get())
        self.title(t("shell.title"))
        self.play_btn.configure(text=t("shell.play"))
        if not self._busy:
            self.status.set(t("shell.ready"))
        self._on_select()

    def _on_select(self, _event=None) -> None:
        sel = self.listbox.curselection()
        if not sel:
            self.preview_var.set("")
            return
        eid = self._items[sel[0]]["id"]
        self.preview_var.set(t(instruction_key(eid)))

    def on_results(self) -> None:
        rows = results_store.recent(15)
        if not rows:
            messagebox.showinfo("Results", f"No sessions yet.\nStore: {results_dir()}")
            return
        lines = [
            f"{r.get('ts', '?')}  {r.get('exercise_id')}  exit={r.get('exit_code')}"
            for r in rows
        ]
        messagebox.showinfo(
            "Results",
            f"Store: {results_dir()}\n\n" + "\n".join(lines),
        )

    def _on_close(self) -> None:
        steam.shutdown()
        self.destroy()

    def on_play(self) -> None:
        if self._busy:
            return
        sel = self.listbox.curselection()
        if not sel:
            messagebox.showinfo(t("shell.app_name"), t("shell.select_first"))
            return
        item = self._items[sel[0]]
        root = Path(self.root_var.get()).expanduser()
        if not root.is_dir():
            messagebox.showerror(t("shell.app_name"), t("shell.missing_root"))
            return
        exercise_dir = root / item["id"]
        if not exercise_dir.is_dir():
            messagebox.showerror(
                t("shell.app_name"),
                t("shell.missing_folder", path=str(exercise_dir)),
            )
            return
        self._busy = True
        self.status.set(t("shell.playing", id=item["id"]))
        threading.Thread(
            target=self._run_play, args=(exercise_dir, item["id"]), daemon=True
        ).start()

    def _run_play(self, exercise_dir: Path, exercise_id: str) -> None:
        try:
            proc = subprocess.run(
                ["make", "play"],
                cwd=str(exercise_dir),
                check=False,
            )
            code = proc.returncode
            msg = t("shell.finished", id=exercise_id, code=code)
        except Exception as exc:  # noqa: BLE001
            code = -1
            msg = t("shell.failed", id=exercise_id, error=str(exc))
        self.after(0, lambda: self._done(msg, code, exercise_id))

    def _done(self, msg: str, code: int, exercise_id: str = "") -> None:
        self._busy = False
        self.status.set(msg)
        if exercise_id:
            path = results_store.record_session(
                exercise_id, code, locale=get_locale()
            )
            self.status.set(f"{msg} · saved {path.name}")
        if code == 0:
            messagebox.showinfo(t("shell.app_name"), msg)
        else:
            messagebox.showwarning(t("shell.app_name"), msg)


def main_cli() -> None:
    import sys

    steam.init()
    st = steam.status()
    print(f"Steam: {st.available} — {st.reason}")
    items = load_catalog()
    root = exercises_root()
    print(f"{t('shell.title')} — {len(items)} exercises [{get_locale()}]")
    print(f"Cores root: {root or '(unset LOGICFORGE_EXERCISES_ROOT)'}")
    for i, item in enumerate(items, 1):
        print(f"  {i:3d}. {item['id']}")
    if not root:
        print(t("shell.missing_root"), file=sys.stderr)
        raise SystemExit(2)
    choice = input("Number to play (blank=quit): ").strip()
    if not choice:
        return
    idx = int(choice) - 1
    item = items[idx]
    print(t(instruction_key(item["id"])))
    exercise_dir = root / item["id"]
    print(f"Running make play in {exercise_dir} …")
    raise SystemExit(subprocess.call(["make", "play"], cwd=str(exercise_dir)))


def main() -> None:
    import sys

    # Optional: --locale de
    if "--locale" in sys.argv:
        i = sys.argv.index("--locale")
        if i + 1 < len(sys.argv):
            set_locale(sys.argv[i + 1])
    if "--cli" in sys.argv or not os.environ.get("DISPLAY"):
        main_cli()
        return
    app = ShellApp()
    app.mainloop()


if __name__ == "__main__":
    main()
