#!/usr/bin/env python3
"""
Sims 4 Freeze Finder - Automated Binary Search Mod Isolator
============================================================
Instead of manually doing 50/50, this tool automates the entire process.
It moves mods in/out of your folder in smart batches and tracks which
group causes the freeze so you can pinpoint the exact culprit.

Works for freezes, infinite loads, and crashes that don't generate
lastException logs.

Author: Built for Meca's ~28K mod collection
"""

import os
import sys
import json
import shutil
import time
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from pathlib import Path
from datetime import datetime
from collections import defaultdict
import threading
import math

# ============================================================
# CONFIG
# ============================================================
CONFIG_FILE = "freeze_finder_config.json"
STATE_FILE = "freeze_finder_state.json"
QUARANTINE_FOLDER_NAME = "_FreezeFinder_Quarantine"

# Known script mods that have caused issues before (prioritize these)
KNOWN_PROBLEMATIC = [
    "chingyu_randomsocialcompatibility",
    "turbodriver_simulationtimelineunclogger",
    "wickedwhims",
    "wonderfulwhims",
    "mccc",
    "lumpinou",
    "adeepindigo",
    "basemental",
    "sacrificial",
    "polarbearsims",
    "kiarasims",
    "littlemssam",
    "simrealist",
    "ravasheen",
    "icemunmun",
]


class ModInfo:
    """Represents a single mod file with metadata."""
    def __init__(self, path: Path, relative_path: str):
        self.path = path
        self.relative_path = relative_path
        self.name = path.name
        self.size = path.stat().st_size if path.exists() else 0
        self.is_script = path.suffix.lower() == ".ts4script"
        self.is_package = path.suffix.lower() == ".package"
        self.priority = self._calc_priority()

    def _calc_priority(self):
        """Higher priority = more likely to cause freezes. Test these first."""
        name_lower = self.name.lower()
        # Script mods are far more likely to cause freezes
        score = 100 if self.is_script else 0
        # Known problematic mods get boosted
        for known in KNOWN_PROBLEMATIC:
            if known in name_lower:
                score += 50
                break
        # Large merged packages can cause issues
        if self.size > 500 * 1024 * 1024:  # >500MB
            score += 20
        elif self.size > 100 * 1024 * 1024:  # >100MB
            score += 10
        return score


class FreezeFinder:
    """Core logic for the binary search mod isolator."""

    def __init__(self):
        self.mods_path = None
        self.quarantine_path = None
        self.all_mods = []
        self.script_mods = []
        self.package_mods = []
        self.current_round = 0
        self.max_rounds = 0
        self.state = {
            "phase": "idle",  # idle, script_test, binary_search, done
            "suspects": [],   # current suspect list (relative paths)
            "cleared": [],    # mods confirmed not causing the issue
            "quarantined": [],  # currently moved out
            "round": 0,
            "history": [],    # log of actions
            "culprits_found": [],
        }

    def load_config(self):
        """Load saved config (mods path etc)."""
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
        return {}

    def save_config(self, config):
        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f, indent=2)

    def save_state(self):
        with open(STATE_FILE, "w") as f:
            json.dump(self.state, f, indent=2, default=str)

    def load_state(self):
        if os.path.exists(STATE_FILE):
            with open(STATE_FILE, "r") as f:
                self.state = json.load(f)
                return True
        return False

    def scan_mods(self, mods_path: str):
        """Scan the mods folder and categorize everything."""
        self.mods_path = Path(mods_path)
        self.quarantine_path = self.mods_path / QUARANTINE_FOLDER_NAME

        if not self.mods_path.exists():
            raise FileNotFoundError(f"Mods folder not found: {mods_path}")

        self.all_mods = []
        self.script_mods = []
        self.package_mods = []

        for root, dirs, files in os.walk(self.mods_path):
            # Skip quarantine folder and Resource.cfg
            root_path = Path(root)
            if QUARANTINE_FOLDER_NAME in root_path.parts:
                continue
            # Skip depth > 1 subfolder for .package (game only reads 1 deep)
            # but scan all for .ts4script
            for fname in files:
                fpath = root_path / fname
                ext = fpath.suffix.lower()
                if ext not in (".package", ".ts4script"):
                    continue
                # Get path relative to mods folder
                rel = fpath.relative_to(self.mods_path)
                mod = ModInfo(fpath, str(rel))
                self.all_mods.append(mod)
                if mod.is_script:
                    self.script_mods.append(mod)
                else:
                    self.package_mods.append(mod)

        # Sort by priority (most likely culprits first)
        self.script_mods.sort(key=lambda m: m.priority, reverse=True)
        self.package_mods.sort(key=lambda m: m.priority, reverse=True)

        return {
            "total": len(self.all_mods),
            "scripts": len(self.script_mods),
            "packages": len(self.package_mods),
        }

    def quarantine_mods(self, mod_list: list):
        """Move mods to quarantine folder, preserving subfolder structure."""
        self.quarantine_path.mkdir(exist_ok=True)
        moved = []
        for rel_path in mod_list:
            src = self.mods_path / rel_path
            dst = self.quarantine_path / rel_path
            if src.exists():
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(src), str(dst))
                moved.append(rel_path)
        self.state["quarantined"] = list(set(self.state.get("quarantined", []) + moved))
        self.save_state()
        return moved

    def restore_mods(self, mod_list: list):
        """Move mods back from quarantine to their original location."""
        restored = []
        for rel_path in mod_list:
            src = self.quarantine_path / rel_path
            dst = self.mods_path / rel_path
            if src.exists():
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(src), str(dst))
                restored.append(rel_path)
        self.state["quarantined"] = [
            m for m in self.state.get("quarantined", []) if m not in restored
        ]
        self.save_state()
        return restored

    def restore_all(self):
        """Emergency restore - put everything back."""
        if not self.quarantine_path or not self.quarantine_path.exists():
            return 0
        count = 0
        for root, dirs, files in os.walk(self.quarantine_path):
            for fname in files:
                src = Path(root) / fname
                rel = src.relative_to(self.quarantine_path)
                dst = self.mods_path / rel
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(src), str(dst))
                count += 1
        # Clean up quarantine folder
        try:
            shutil.rmtree(str(self.quarantine_path))
        except Exception:
            pass
        self.state["quarantined"] = []
        self.state["phase"] = "idle"
        self.save_state()
        return count

    def start_search(self, mode="smart"):
        """
        Start the binary search process.
        
        Mode 'smart': Test scripts first (since they cause most freezes),
        then do binary search on packages if needed.
        
        Mode 'scripts_only': Only test script mods.
        Mode 'packages_only': Only test package mods.
        Mode 'all': Binary search everything together.
        """
        if mode == "smart":
            # Phase 1: Quarantine ALL script mods first
            suspects = [m.relative_path for m in self.script_mods]
            self.state["phase"] = "script_test"
        elif mode == "scripts_only":
            suspects = [m.relative_path for m in self.script_mods]
            self.state["phase"] = "binary_search"
        elif mode == "packages_only":
            suspects = [m.relative_path for m in self.package_mods]
            self.state["phase"] = "binary_search"
        else:
            suspects = [m.relative_path for m in self.all_mods]
            self.state["phase"] = "binary_search"

        self.state["suspects"] = suspects
        self.state["cleared"] = []
        self.state["round"] = 0
        self.state["history"] = []
        self.state["culprits_found"] = []
        self.state["mode"] = mode

        total = len(suspects)
        self.max_rounds = math.ceil(math.log2(max(total, 1))) + 1

        self.save_state()
        return {
            "suspects": total,
            "estimated_rounds": self.max_rounds,
            "phase": self.state["phase"],
        }

    def get_next_action(self):
        """Determine what to do next based on current state."""
        phase = self.state["phase"]
        suspects = self.state["suspects"]

        if phase == "done" or (phase != "script_test" and len(suspects) <= 0):
            return {"action": "done", "culprits": self.state["culprits_found"]}

        if phase == "script_test":
            # Quarantine all scripts, ask user to test
            return {
                "action": "quarantine_and_test",
                "description": "Removing ALL script mods (.ts4script) to test if freeze is script-related",
                "mods_to_quarantine": [m.relative_path for m in self.script_mods],
                "count": len(self.script_mods),
            }

        if phase == "binary_search":
            if len(suspects) == 1:
                return {
                    "action": "found_suspect",
                    "mod": suspects[0],
                    "description": f"Narrowed down to 1 mod: {suspects[0]}",
                }

            # Split suspects in half
            mid = len(suspects) // 2
            group_a = suspects[:mid]
            group_b = suspects[mid:]

            self.state["round"] += 1
            round_num = self.state["round"]

            return {
                "action": "binary_split",
                "round": round_num,
                "total_suspects": len(suspects),
                "group_a": group_a,
                "group_b": group_b,
                "description": (
                    f"Round {round_num}: Splitting {len(suspects)} suspects in half.\n"
                    f"  Group A: {len(group_a)} mods (keeping IN game)\n"
                    f"  Group B: {len(group_b)} mods (quarantining)"
                ),
            }

        return {"action": "error", "message": "Unknown state"}

    def report_result(self, still_freezing: bool):
        """
        User reports whether the game still froze.
        This advances the search.
        """
        phase = self.state["phase"]
        suspects = self.state["suspects"]
        timestamp = datetime.now().isoformat()

        if phase == "script_test":
            if not still_freezing:
                # Scripts caused it! Now binary search just scripts
                self.state["phase"] = "binary_search"
                self.state["suspects"] = [m.relative_path for m in self.script_mods]
                # Restore scripts so we can do proper binary search
                self.restore_mods([m.relative_path for m in self.script_mods])
                self.state["history"].append({
                    "time": timestamp,
                    "event": "Scripts confirmed as cause. Starting binary search on scripts.",
                })
            else:
                # Not scripts - it's a package mod. Restore scripts, search packages
                self.restore_mods([m.relative_path for m in self.script_mods])
                self.state["phase"] = "binary_search"
                self.state["suspects"] = [m.relative_path for m in self.package_mods]
                self.state["history"].append({
                    "time": timestamp,
                    "event": "Scripts cleared. Freeze is from a .package mod. Starting binary search on packages.",
                })
            self.save_state()
            return

        if phase == "binary_search":
            mid = len(suspects) // 2
            group_a = suspects[:mid]   # These were IN the game
            group_b = suspects[mid:]   # These were quarantined

            if still_freezing:
                # Freeze persists = Group A has the culprit (those still in game)
                # Restore Group B (they're cleared), narrow to Group A
                self.restore_mods(group_b)
                self.state["cleared"].extend(group_b)
                self.state["suspects"] = group_a
                self.state["history"].append({
                    "time": timestamp,
                    "round": self.state["round"],
                    "event": f"Still freezing → culprit is in Group A ({len(group_a)} mods). Cleared {len(group_b)}.",
                })
            else:
                # No freeze = Group B had the culprit (those we removed)
                # Group A is cleared, narrow to Group B
                # But Group B is in quarantine - restore them and quarantine Group A instead
                self.restore_mods(group_b)
                self.quarantine_mods(group_a)
                self.state["cleared"].extend(group_a)
                self.state["suspects"] = group_b
                self.state["history"].append({
                    "time": timestamp,
                    "round": self.state["round"],
                    "event": f"No freeze → culprit is in Group B ({len(group_b)} mods). Cleared {len(group_a)}.",
                })

            # Check if we've found it
            if len(self.state["suspects"]) == 1:
                culprit = self.state["suspects"][0]
                self.state["culprits_found"].append(culprit)
                self.state["phase"] = "done"
                self.state["history"].append({
                    "time": timestamp,
                    "event": f"FOUND CULPRIT: {culprit}",
                })

            self.save_state()


# ============================================================
# GUI
# ============================================================
class FreezeFinderGUI:
    def __init__(self):
        self.finder = FreezeFinder()
        self.root = tk.Tk()
        self.root.title("Sims 4 Freeze Finder — Binary Search Mod Isolator")
        self.root.geometry("900x700")
        self.root.configure(bg="#1a1a2e")
        self.root.resizable(True, True)

        # Style
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.colors = {
            "bg": "#1a1a2e",
            "surface": "#16213e",
            "accent": "#e94560",
            "accent2": "#0f3460",
            "text": "#eaeaea",
            "text_dim": "#8892a0",
            "success": "#4ecca3",
            "warning": "#f0a500",
            "danger": "#e94560",
        }

        self._configure_styles()
        self._build_ui()
        self._load_saved_state()

    def _configure_styles(self):
        c = self.colors
        self.style.configure("Title.TLabel", background=c["bg"], foreground=c["accent"],
                             font=("Segoe UI", 18, "bold"))
        self.style.configure("Header.TLabel", background=c["bg"], foreground=c["text"],
                             font=("Segoe UI", 12, "bold"))
        self.style.configure("Info.TLabel", background=c["bg"], foreground=c["text_dim"],
                             font=("Segoe UI", 10))
        self.style.configure("Status.TLabel", background=c["surface"], foreground=c["success"],
                             font=("Segoe UI", 11, "bold"))
        self.style.configure("Big.TButton", font=("Segoe UI", 11, "bold"), padding=(20, 10))
        self.style.configure("Action.TButton", font=("Segoe UI", 10), padding=(15, 8))
        self.style.configure("Danger.TButton", font=("Segoe UI", 10, "bold"), padding=(15, 8))
        self.style.configure("TFrame", background=c["bg"])
        self.style.configure("Surface.TFrame", background=c["surface"])
        self.style.configure("TLabelframe", background=c["bg"], foreground=c["text"])
        self.style.configure("TLabelframe.Label", background=c["bg"], foreground=c["accent"],
                             font=("Segoe UI", 11, "bold"))
        self.style.configure("TProgressbar", troughcolor=c["surface"],
                             background=c["accent"], thickness=20)

    def _build_ui(self):
        c = self.colors

        # Title bar
        title_frame = ttk.Frame(self.root)
        title_frame.pack(fill="x", padx=20, pady=(15, 5))
        ttk.Label(title_frame, text="🔍 Sims 4 Freeze Finder", style="Title.TLabel").pack(side="left")
        ttk.Label(title_frame, text="Automated Binary Search — No More 50/50!",
                  style="Info.TLabel").pack(side="left", padx=(15, 0))

        # Path selector
        path_frame = ttk.Frame(self.root)
        path_frame.pack(fill="x", padx=20, pady=5)
        ttk.Label(path_frame, text="Mods Folder:", style="Header.TLabel").pack(side="left")
        self.path_var = tk.StringVar()
        path_entry = ttk.Entry(path_frame, textvariable=self.path_var, width=60,
                               font=("Consolas", 10))
        path_entry.pack(side="left", padx=(10, 5), fill="x", expand=True)
        ttk.Button(path_frame, text="Browse", command=self._browse_folder,
                   style="Action.TButton").pack(side="left")
        ttk.Button(path_frame, text="Scan", command=self._scan_mods,
                   style="Action.TButton").pack(side="left", padx=(5, 0))

        # Stats bar
        stats_frame = ttk.Frame(self.root, style="Surface.TFrame")
        stats_frame.pack(fill="x", padx=20, pady=10)
        self.stats_label = ttk.Label(stats_frame, text="No mods scanned yet",
                                     style="Status.TLabel")
        self.stats_label.pack(padx=15, pady=8)

        # Progress
        prog_frame = ttk.Frame(self.root)
        prog_frame.pack(fill="x", padx=20, pady=(0, 5))
        self.progress = ttk.Progressbar(prog_frame, mode="determinate")
        self.progress.pack(fill="x")
        self.progress_label = ttk.Label(prog_frame, text="", style="Info.TLabel")
        self.progress_label.pack(pady=(3, 0))

        # Main action area
        action_frame = ttk.LabelFrame(self.root, text="Current Step", padding=15)
        action_frame.pack(fill="both", padx=20, pady=5, expand=False)

        self.action_text = tk.Text(action_frame, height=6, wrap="word",
                                   bg=self.colors["surface"], fg=self.colors["text"],
                                   font=("Consolas", 10), relief="flat",
                                   insertbackground=self.colors["text"])
        self.action_text.pack(fill="both", expand=True)
        self.action_text.config(state="disabled")

        # Buttons
        btn_frame = ttk.Frame(self.root)
        btn_frame.pack(fill="x", padx=20, pady=10)

        self.start_btn = ttk.Button(btn_frame, text="▶ Start Smart Search",
                                    command=self._start_smart, style="Big.TButton")
        self.start_btn.pack(side="left", padx=(0, 5))

        self.scripts_only_btn = ttk.Button(btn_frame, text="Scripts Only",
                                           command=self._start_scripts_only,
                                           style="Action.TButton")
        self.scripts_only_btn.pack(side="left", padx=5)

        self.packages_only_btn = ttk.Button(btn_frame, text="Packages Only",
                                            command=self._start_packages_only,
                                            style="Action.TButton")
        self.packages_only_btn.pack(side="left", padx=5)

        # Separator
        ttk.Separator(btn_frame, orient="vertical").pack(side="left", fill="y", padx=10)

        self.proceed_btn = ttk.Button(btn_frame, text="⏩ Quarantine & Proceed",
                                      command=self._proceed, style="Action.TButton",
                                      state="disabled")
        self.proceed_btn.pack(side="left", padx=5)

        # Result buttons (after testing game)
        result_frame = ttk.Frame(self.root)
        result_frame.pack(fill="x", padx=20, pady=5)

        ttk.Label(result_frame, text="After testing your game:",
                  style="Header.TLabel").pack(side="left")
        self.freeze_btn = ttk.Button(result_frame, text="😡 Still Freezing",
                                     command=lambda: self._report(True),
                                     style="Danger.TButton", state="disabled")
        self.freeze_btn.pack(side="left", padx=(15, 5))

        self.ok_btn = ttk.Button(result_frame, text="✅ Game Works!",
                                 command=lambda: self._report(False),
                                 style="Action.TButton", state="disabled")
        self.ok_btn.pack(side="left", padx=5)

        # Emergency restore
        ttk.Separator(result_frame, orient="vertical").pack(side="left", fill="y", padx=10)
        self.restore_btn = ttk.Button(result_frame, text="🔄 Restore ALL Mods",
                                      command=self._restore_all,
                                      style="Danger.TButton")
        self.restore_btn.pack(side="right")

        # Log
        log_frame = ttk.LabelFrame(self.root, text="Search Log", padding=10)
        log_frame.pack(fill="both", padx=20, pady=(5, 15), expand=True)

        self.log = scrolledtext.ScrolledText(log_frame, height=10, wrap="word",
                                              bg=self.colors["surface"],
                                              fg=self.colors["text"],
                                              font=("Consolas", 9), relief="flat",
                                              insertbackground=self.colors["text"])
        self.log.pack(fill="both", expand=True)

    def _load_saved_state(self):
        config = self.finder.load_config()
        if "mods_path" in config:
            self.path_var.set(config["mods_path"])

        if self.finder.load_state():
            phase = self.finder.state.get("phase", "idle")
            if phase not in ("idle", "done"):
                self._log(f"Resuming previous search session (phase: {phase})")
                self._log(f"Suspects remaining: {len(self.finder.state.get('suspects', []))}")
                self._log(f"Cleared so far: {len(self.finder.state.get('cleared', []))}")
                # Re-scan to rebuild mod objects
                if config.get("mods_path"):
                    try:
                        self.finder.scan_mods(config["mods_path"])
                        self._update_stats()
                    except Exception:
                        pass
                self._enable_result_buttons()

    def _browse_folder(self):
        # Try common Sims 4 paths
        default = ""
        for try_path in [
            Path.home() / "Documents" / "Electronic Arts" / "The Sims 4" / "Mods",
            Path("D:/") / "Electronic Arts" / "The Sims 4" / "Mods",
        ]:
            if try_path.exists():
                default = str(try_path)
                break

        folder = filedialog.askdirectory(title="Select your Sims 4 Mods folder",
                                         initialdir=default or str(Path.home()))
        if folder:
            self.path_var.set(folder)
            self.finder.save_config({"mods_path": folder})

    def _scan_mods(self):
        path = self.path_var.get().strip()
        if not path:
            messagebox.showwarning("No Path", "Please select your Mods folder first.")
            return

        try:
            stats = self.finder.scan_mods(path)
            self.finder.save_config({"mods_path": path})
            self._update_stats()
            self._log(f"Scanned: {stats['total']} mods ({stats['scripts']} scripts, {stats['packages']} packages)")

            # Show top suspects
            top = [m for m in self.finder.script_mods if m.priority >= 100][:10]
            if top:
                self._log("Top suspects (script mods, tested first):")
                for m in top:
                    self._log(f"  ⚠ {m.name} (priority: {m.priority})")

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _update_stats(self):
        f = self.finder
        suspects = len(f.state.get("suspects", []))
        cleared = len(f.state.get("cleared", []))
        quarantined = len(f.state.get("quarantined", []))
        phase = f.state.get("phase", "idle")

        text = (
            f"📦 {len(f.all_mods)} total mods  |  "
            f"📜 {len(f.script_mods)} scripts  |  "
            f"🎨 {len(f.package_mods)} packages  |  "
            f"🔍 {suspects} suspects  |  "
            f"✅ {cleared} cleared  |  "
            f"📤 {quarantined} quarantined  |  "
            f"Phase: {phase}"
        )
        self.stats_label.config(text=text)

        # Update progress
        total = suspects + cleared
        if total > 0:
            self.progress["value"] = (cleared / total) * 100
            rounds_done = f.state.get("round", 0)
            est_remaining = math.ceil(math.log2(max(suspects, 1)))
            self.progress_label.config(
                text=f"Round {rounds_done} — ~{est_remaining} rounds remaining to find culprit"
            )

    def _set_action(self, text):
        self.action_text.config(state="normal")
        self.action_text.delete("1.0", "end")
        self.action_text.insert("1.0", text)
        self.action_text.config(state="disabled")

    def _log(self, msg):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log.insert("end", f"[{timestamp}] {msg}\n")
        self.log.see("end")

    def _enable_result_buttons(self):
        self.freeze_btn.config(state="normal")
        self.ok_btn.config(state="normal")
        self.proceed_btn.config(state="disabled")

    def _disable_all_buttons(self):
        self.freeze_btn.config(state="disabled")
        self.ok_btn.config(state="disabled")
        self.proceed_btn.config(state="disabled")
        self.start_btn.config(state="disabled")

    def _start_smart(self):
        self._start_search("smart")

    def _start_scripts_only(self):
        self._start_search("scripts_only")

    def _start_packages_only(self):
        self._start_search("packages_only")

    def _start_search(self, mode):
        if not self.finder.all_mods:
            messagebox.showwarning("Scan First", "Please scan your Mods folder first.")
            return

        result = self.finder.start_search(mode)
        self._log(f"Search started ({mode}): {result['suspects']} suspects, "
                  f"~{result['estimated_rounds']} rounds estimated")
        self._show_next_step()

    def _show_next_step(self):
        action = self.finder.get_next_action()
        self._update_stats()

        if action["action"] == "done":
            culprits = action.get("culprits", [])
            if culprits:
                msg = "🎉 FOUND THE CULPRIT(S):\n\n"
                for c in culprits:
                    msg += f"  → {c}\n"
                msg += "\nThis mod is causing your freeze. You can:\n"
                msg += "1. Remove it permanently\n"
                msg += "2. Check for an updated version\n"
                msg += "3. Use 'Restore ALL' to put everything back and re-test to confirm"
            else:
                msg = "Search complete. No single culprit found — could be a multi-mod conflict."
            self._set_action(msg)
            self._log(msg.replace("\n", " | "))
            self._disable_all_buttons()
            self.start_btn.config(state="normal")
            return

        if action["action"] == "quarantine_and_test":
            self._set_action(
                f"{action['description']}\n\n"
                f"Will quarantine {action['count']} script mods.\n\n"
                f"Click 'Quarantine & Proceed' to move them, then test your game."
            )
            self._pending_quarantine = action["mods_to_quarantine"]
            self.proceed_btn.config(state="normal")
            self.freeze_btn.config(state="disabled")
            self.ok_btn.config(state="disabled")
            return

        if action["action"] == "binary_split":
            desc = action["description"]
            self._set_action(
                f"{desc}\n\n"
                f"Click 'Quarantine & Proceed' to remove Group B, then test your game.\n"
                f"After testing, tell me if it still froze or worked."
            )
            self._pending_quarantine = action["group_b"]
            self.proceed_btn.config(state="normal")
            self.freeze_btn.config(state="disabled")
            self.ok_btn.config(state="disabled")
            return

        if action["action"] == "found_suspect":
            mod = action["mod"]
            self._set_action(
                f"🎯 Narrowed down to ONE mod:\n\n"
                f"  {mod}\n\n"
                f"Quarantine this mod and test. If game works, this is your culprit!"
            )
            self._pending_quarantine = [mod]
            self.proceed_btn.config(state="normal")
            return

    def _proceed(self):
        """Execute the pending quarantine action."""
        if not hasattr(self, "_pending_quarantine"):
            return

        mods = self._pending_quarantine
        self._log(f"Quarantining {len(mods)} mods...")

        try:
            moved = self.finder.quarantine_mods(mods)
            self._log(f"Moved {len(moved)} mods to quarantine")
            self._set_action(
                f"✅ Done! {len(moved)} mods quarantined.\n\n"
                f"NOW:\n"
                f"1. Launch The Sims 4\n"
                f"2. Load your save\n"
                f"3. Press Resume/Play\n"
                f"4. Come back and tell me: did it freeze or work?"
            )
            self._enable_result_buttons()
            self.proceed_btn.config(state="disabled")
            self._update_stats()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to move mods: {e}")

    def _report(self, still_freezing):
        """User reports whether game still froze."""
        if still_freezing:
            self._log("❌ User reports: Still freezing")
        else:
            self._log("✅ User reports: Game works!")

        self.finder.report_result(still_freezing)
        self._show_next_step()

    def _restore_all(self):
        if not messagebox.askyesno("Restore All",
                                   "This will move ALL quarantined mods back to your Mods folder.\n"
                                   "The current search progress will be lost.\n\nContinue?"):
            return

        count = self.finder.restore_all()
        self._log(f"🔄 Restored {count} mods to Mods folder")
        self._set_action(f"All {count} mods restored. Search reset.")
        self._update_stats()
        self.start_btn.config(state="normal")

    def run(self):
        self.root.mainloop()


# ============================================================
# MAIN
# ============================================================
if __name__ == "__main__":
    app = FreezeFinderGUI()
    app.run()
