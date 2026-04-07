# Sims 4 Mod Conflict Detector

A Python desktop tool for diagnosing, scanning, and managing large Sims 4 mod collections. Built to solve a real problem: when you have 28,000+ mod files, finding what's broken, conflicting, or outdated manually is nearly impossible.

This tool automates the entire process using binary-level analysis of EA's proprietary DBPF file format.

---

## What it does

- **DBPF binary parsing** — reads `.package` files at the binary level using EA's proprietary format to extract resource entries (Type/Group/Instance keys)
- **TGI conflict detection** — identifies mods that override the same game resource, which causes unpredictable behavior
- **Version detection** — reads actual version strings from inside `.ts4script` files (which are ZIP archives) and compares against known safe versions for major mods
- **Duplicate & integrity checks** — SHA-256 hash verification across the entire mod library to find corrupted or duplicate files
- **LOD/GEOM mesh analysis** — detects high-polygon mesh mods that hurt game performance
- **Merged package breakdown** — for packages over 100MB, generates a full resource table with CAS counts, texture sizes, and optimization suggestions
- **Exception log analysis** — parses Better Exceptions and MCCC log files to correlate crash data with specific mods
- **Freeze isolator** — binary search tool that narrows down which mod is causing loading screen crashes without manual 50/50 testing
- **Excel cleanup report** — auto-generates a formatted `.xlsx` checklist after every scan with actionable removal/update recommendations

---

## Technical stack

- **Language:** Python 3.10+
- **File format:** DBPF (Database Packed File) — binary parsing using `struct` and `zlib`
- **Script mod reading:** `.ts4script` files parsed as ZIP archives to extract embedded Python version strings
- **Parallel processing:** `multiprocessing.Pool` with `cpu_count()` for scanning large collections
- **GUI:** `tkinter` (built-in) — no additional dependencies required for basic use
- **Reporting:** `openpyxl` for Excel output, `csv` for portable export
- **Progress display:** `tqdm` with graceful fallback if not installed

---

## Files

| File | Purpose |
|------|---------|
| `mod_detector_v6.py` | Main application — scanner, parser, GUI, and report generator |
| `sims4_freeze_finder.py` | Binary search isolator for crash/freeze diagnosis |
| `FULL_SCAN.bat` | One-click full scan launcher (Windows) |
| `QUICK_SCAN.bat` | Fast scan — integrity, duplicates, outdated (no DBPF parsing) |
| `FULL_SCAN_WITH_LOG.bat` | Full scan + drag-and-drop exception log analysis |
| `FULL_SCAN_WITH_ALL.bat` | Full scan + exception log + Scarlet Mod Checker CSV cross-reference |
| `MERGED_ANALYSIS.bat` | Deep breakdown of large merged package files |
| `VERSION_CHECK.bat` | Standalone version check against known safe mod versions |
| `GUI_LAUNCH.bat` | Launch the tkinter GUI |
| `UPDATE_DATABASE.bat` | Update the local broken mod hash database |

---

## Setup

**Requirements:** Python 3.10+ — [download here](https://www.python.org/downloads/)
> During install, check **"Add Python to PATH"**

**Optional dependencies:**
```bash
pip install tqdm      # progress bars
pip install openpyxl  # Excel report generation
```

**Usage:**
1. Place all files in the same folder
2. Double-click any `.bat` file to run the corresponding scan
3. Or use the GUI: double-click `GUI_LAUNCH.bat`

**CLI:**
```bash
# Full scan with parallel processing
python mod_detector_v6.py --mods "C:/Users/YourName/Documents/Electronic Arts/The Sims 4/Mods" --full --parallel

# Full scan with exception log analysis
python mod_detector_v6.py --mods "path/to/Mods" --full --parallel --log "better_exceptions_log.txt"

# Merged package analysis only
python mod_detector_v6.py --mods "path/to/Mods" --analyze-merged --merged-threshold 50

# Launch GUI
python mod_detector_v6.py --gui
```

**Custom Mods path** — if your Mods folder is not in the default location, edit the `MODS_PATH` line in any `.bat` file:
```batch
set "MODS_PATH=D:\Games\The Sims 4\Mods"
```

---

## Scan modes

| Mode | What it checks | Typical time (28K mods) |
|------|---------------|------------------------|
| Quick scan | Integrity, duplicates, outdated, broken, performance flags | 3–5 min |
| Full scan | Everything: DBPF parsing, TGI conflicts, LOD analysis, version detection, merged breakdown | 15–25 min |
| Merged analysis | Resource table for packages over threshold size | 5–10 min |
| Version check | Reads version strings from .ts4script and .package files | 1–2 min |

---

## Why this exists

The Sims 4 modding community is technically sophisticated — mods are distributed as DBPF binary packages or Python script archives, and a large modded installation easily reaches 28,000+ files. When the game breaks, EA provides no diagnostic tooling. The existing community tools (BetterExceptions, Scarlet Mod Checker) are valuable but limited — they tell you *something* is wrong, not *what* or *why*.

This tool was built to fill that gap: a local, offline diagnostic suite that reads the actual binary data, understands the file format, and gives actionable answers instead of just a list of suspects.

---

## Version history

- **v8.0** — Full rewrite: DBPF binary parser, TGI conflict engine, Scarlet Mod Checker CSV integration, WickedWhims false positive fix, MCCC folder version detection
- **v6.2** — Script mod version detection, merged package breakdown, Better Exceptions log parser
- Earlier versions — basic duplicate detection and integrity checking

---

*Built by Meca Dismukes · [github.com/mecadismukes](https://github.com/mecadismukes)*
