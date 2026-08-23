#!/usr/bin/env python3
"""
Mirrors Sonia's OneDrive folder Pictures/Jaxie-drawings into images/AAAA/MM/DD.
The OneDrive folder is the single source of truth:
  - New files there -> imported into the gallery.
  - Files deleted there -> removed from the gallery.
  - Files renamed there -> old name removed, new name imported
    (a rename looks like a delete + an add).
Tracked via a JSON ledger (.onedrive-sync-ledger.json) mapping each
OneDrive filename to where it currently lives under images/.
Runs both locally and in GitHub Actions (uses $GITHUB_WORKSPACE if set).
"""
import os
import json
import subprocess
import shutil
import sys
import tempfile
from pathlib import Path
from datetime import datetime

REPO = Path(os.environ.get("GITHUB_WORKSPACE", "/home/andlo/Work/jaxie-art"))
IS_CI = "GITHUB_WORKSPACE" in os.environ
STAGING = Path(tempfile.mkdtemp()) if IS_CI else Path("/home/andlo/staging-jaxie-drawings")
STAGING.mkdir(exist_ok=True)
LEDGER = REPO / ".onedrive-sync-ledger.json"
EXTS = {".png", ".jpg", ".jpeg", ".webp", ".gif"}
REMOTE = "sonia-onedrive:Pictures/Jaxie-drawings"


def log(msg):
    print(f"[{datetime.now().isoformat(timespec='seconds')}] {msg}", flush=True)


def run(cmd, **kw):
    return subprocess.run(cmd, check=True, capture_output=True, text=True, **kw)

def load_ledger():
    if LEDGER.exists():
        return json.loads(LEDGER.read_text())
    return {}


def main():
    log("Henter fra OneDrive...")
    run(["rclone", "copy", REMOTE, str(STAGING), "--transfers", "8"])

    ledger = load_ledger()

    current = {}
    for f in sorted(STAGING.iterdir()):
        if not f.is_file() or f.suffix.lower() not in EXTS:
            continue
        current[f.name] = f

    removed, added = [], []

    # Files that used to exist in OneDrive but don't anymore -> remove from site
    for name in list(ledger.keys()):
        if name not in current:
            old_path = REPO / ledger[name]["path"]
            if old_path.exists():
                run(["git", "-C", str(REPO), "rm", "-q", str(old_path)])
            del ledger[name]
            removed.append(name)
            log(f"Fjernet (ikke længere i OneDrive): {name}")

    # New files in OneDrive that aren't tracked yet -> add to site
    for name, f in current.items():
        if name in ledger:
            continue
        mtime = datetime.fromtimestamp(f.stat().st_mtime)
        day_dir = REPO / "images" / f"{mtime.year:04d}" / f"{mtime.month:02d}" / f"{mtime.day:02d}"
        day_dir.mkdir(parents=True, exist_ok=True)
        dest = day_dir / f.name
        if dest.exists():
            dest = day_dir / f"{f.stem}-onedrive{f.suffix}"
        shutil.copy2(f, dest)
        ledger[name] = {"path": str(dest.relative_to(REPO))}
        added.append(name)
        log(f"Importeret: {name} -> {dest.relative_to(REPO)}")

    if not removed and not added:
        log("Ingen ændringer.")
        return

    LEDGER.write_text(json.dumps(ledger, indent=2, sort_keys=True) + "\n")

    if not IS_CI:
        run(["git", "-C", str(REPO), "pull", "--rebase", "-q"])
    run(["git", "-C", str(REPO), "add", "-A"])
    msg = f"OneDrive sync: +{len(added)} -{len(removed)}"
    run(["git", "-C", str(REPO), "commit", "-q", "-m", msg])
    run(["git", "-C", str(REPO), "push"])
    log(f"Pushet ({msg}). Deploy sker automatisk.")


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as e:
        log(f"FEJL: {e.cmd} -> {e.stderr}")
        sys.exit(1)
