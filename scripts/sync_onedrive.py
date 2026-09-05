#!/usr/bin/env python3
"""
Mirrors Sonia's OneDrive folder Pictures/Jaxie-drawings into images/AAAA/MM/DD.
The OneDrive folder is the single source of truth:
  - New files there -> imported into the gallery.
  - Files deleted there -> removed from the gallery.
  - Files renamed there -> old name removed, new name imported
    (a rename looks like a delete + an add).
  - A same-named .txt file next to an image (e.g. Drawing.png +
    Drawing.txt) becomes a caption, shown in the gallery. It's kept in
    sync too: added, edited, or removed independently of the image.
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
    # Pull first, before touching the working tree at all — once we start
    # copying files in / running `git rm`, the tree is dirty and a later
    # `pull --rebase` will refuse to run.
    if not IS_CI:
        run(["git", "-C", str(REPO), "pull", "--rebase", "--autostash", "-q"])
    else:
        run(["git", "-C", str(REPO), "pull", "--rebase", "-q"])

    log("Henter fra OneDrive...")
    run(["rclone", "sync", REMOTE, str(STAGING), "--transfers", "8"])

    ledger = load_ledger()

    current = {}       # image filename -> Path
    caption_texts = {}  # image stem -> caption text
    for f in sorted(STAGING.iterdir()):
        if not f.is_file():
            continue
        if f.suffix.lower() in EXTS:
            current[f.name] = f
        elif f.suffix.lower() == ".txt":
            caption_texts[f.stem] = f.read_text(encoding="utf-8").strip()

    removed, added, updated = [], [], []

    # Files that used to exist in OneDrive but don't anymore -> remove from site
    for name in list(ledger.keys()):
        if name not in current:
            entry = ledger[name]
            for key in ("path", "caption_path"):
                p = entry.get(key)
                if p and (REPO / p).exists():
                    run(["git", "-C", str(REPO), "rm", "-q", str(REPO / p)])
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
        entry = {"path": str(dest.relative_to(REPO))}

        caption = caption_texts.get(f.stem)
        if caption:
            cap_dest = dest.with_suffix(".txt")
            cap_dest.write_text(caption, encoding="utf-8")
            entry["caption_path"] = str(cap_dest.relative_to(REPO))
            entry["caption_text"] = caption

        ledger[name] = entry
        added.append(name)
        log(f"Importeret: {name} -> {dest.relative_to(REPO)}")

    # Existing images -> caption may have been added, edited, or removed
    for name, f in current.items():
        if name not in ledger or name in added:
            continue
        entry = ledger[name]
        new_caption = caption_texts.get(f.stem)
        old_caption = entry.get("caption_text")
        if new_caption == old_caption:
            continue

        img_path = REPO / entry["path"]
        cap_dest = img_path.with_suffix(".txt")
        if new_caption:
            cap_dest.write_text(new_caption, encoding="utf-8")
            entry["caption_path"] = str(cap_dest.relative_to(REPO))
            entry["caption_text"] = new_caption
        else:
            if cap_dest.exists():
                run(["git", "-C", str(REPO), "rm", "-q", str(cap_dest)])
            entry.pop("caption_path", None)
            entry.pop("caption_text", None)
        updated.append(name)
        log(f"Billedtekst opdateret: {name}")

    if not removed and not added and not updated:
        log("Ingen ændringer.")
        return

    LEDGER.write_text(json.dumps(ledger, indent=2, sort_keys=True) + "\n")

    run(["git", "-C", str(REPO), "add", "-A"])
    msg = f"OneDrive sync: +{len(added)} -{len(removed)} ~{len(updated)}"
    run(["git", "-C", str(REPO), "commit", "-q", "-m", msg])
    run(["git", "-C", str(REPO), "push"])
    log(f"Pushet ({msg}). Deploy sker automatisk.")


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as e:
        log(f"FEJL: {e.cmd} -> stdout={e.stdout!r} stderr={e.stderr!r}")
        sys.exit(1)
