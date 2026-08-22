#!/usr/bin/env python3
"""Kopierer sorterede tegninger fra staging til images/AAAA/MM/DD, med bevaret dato."""
import shutil
from pathlib import Path
from datetime import datetime

STAGING = Path("/home/andlo/staging-sonia-onedrive")
DEST_ROOT = Path("/home/andlo/Work/sonia-tegninger/images")
SOURCES = ["filmrulle", "uploads", "pictures-root"]
EXTS = {".png", ".jpg", ".jpeg", ".webp", ".gif"}

copied = 0
skipped = 0
for src_name in SOURCES:
    src_dir = STAGING / src_name
    if not src_dir.exists():
        continue
    for f in sorted(src_dir.iterdir()):
        if not f.is_file() or f.suffix.lower() not in EXTS:
            continue
        mtime = datetime.fromtimestamp(f.stat().st_mtime)
        day_dir = DEST_ROOT / f"{mtime.year:04d}" / f"{mtime.month:02d}" / f"{mtime.day:02d}"
        day_dir.mkdir(parents=True, exist_ok=True)
        dest = day_dir / f.name
        if dest.exists():
            dest = day_dir / f"{f.stem} ({src_name}){f.suffix}"
        shutil.copy2(f, dest)  # copy2 preserves mtime
        copied += 1

print(f"Kopieret: {copied} filer, sprunget over: {skipped}")
