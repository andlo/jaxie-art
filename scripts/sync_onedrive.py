#!/usr/bin/env python3
"""
Henter nye tegninger fra Sonias OneDrive-mappe Pictures/Jaxie-drawings,
lægger dem ind i images/AAAA/MM/DD (med dato bevaret), og pusher til GitHub
hvis der var noget nyt. Kører idempotent: en fil bliver aldrig importeret
to gange, selv hvis den senere fjernes fra galleriet igen.
Kører både lokalt og i GitHub Actions (bruger $GITHUB_WORKSPACE hvis sat).
"""
import os
import subprocess
import shutil
import sys
import tempfile
from pathlib import Path
from datetime import datetime

REPO = Path(os.environ.get("GITHUB_WORKSPACE", "/home/andlo/Work/jaxie-drawings"))
IS_CI = "GITHUB_WORKSPACE" in os.environ
STAGING = Path(tempfile.mkdtemp()) if IS_CI else Path("/home/andlo/staging-jaxie-drawings")
STAGING.mkdir(exist_ok=True)
LEDGER = REPO / ".onedrive-sync-ledger.txt"
EXTS = {".png", ".jpg", ".jpeg", ".webp", ".gif"}
REMOTE = "sonia-onedrive:Pictures/Jaxie-drawings"


def log(msg):
    print(f"[{datetime.now().isoformat(timespec='seconds')}] {msg}", flush=True)

def run(cmd, **kw):
    return subprocess.run(cmd, check=True, capture_output=True, text=True, **kw)


def main():
    log("Henter fra OneDrive...")
    run(["rclone", "copy", REMOTE, str(STAGING), "--transfers", "8"])

    ledger = set()
    if LEDGER.exists():
        ledger = set(LEDGER.read_text().splitlines())

    new_files = []
    for f in sorted(STAGING.iterdir()):
        if not f.is_file() or f.suffix.lower() not in EXTS:
            continue
        if f.name in ledger:
            continue
        mtime = datetime.fromtimestamp(f.stat().st_mtime)
        day_dir = REPO / "images" / f"{mtime.year:04d}" / f"{mtime.month:02d}" / f"{mtime.day:02d}"
        day_dir.mkdir(parents=True, exist_ok=True)
        dest = day_dir / f.name
        if dest.exists():
            dest = day_dir / f"{f.stem}-onedrive{f.suffix}"
        shutil.copy2(f, dest)
        ledger.add(f.name)
        new_files.append(f.name)
        log(f"Importeret: {f.name} -> {dest.relative_to(REPO)}")

    if not new_files:
        log("Ingen nye tegninger.")
        return

    LEDGER.write_text("\n".join(sorted(ledger)) + "\n")

    if not IS_CI:
        run(["git", "-C", str(REPO), "pull", "--rebase", "-q"])
    run(["git", "-C", str(REPO), "add", "-A"])
    run(["git", "-C", str(REPO), "commit", "-q", "-m",
         f"Auto-import {len(new_files)} drawing(s) from OneDrive"])
    run(["git", "-C", str(REPO), "push"])
    log(f"Pushet {len(new_files)} nye tegning(er). Deploy sker automatisk.")


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as e:
        log(f"FEJL: {e.cmd} -> {e.stderr}")
        sys.exit(1)
