#!/usr/bin/env python3
"""
Scanner images/AAAA/MM/DD/*.{png,jpg,jpeg,webp,gif} og bygger manifest.json
til brug for galleri-siden (index.html).
"""
import json
import os
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
IMAGES_DIR = ROOT / "images"
OUT_FILE = ROOT / "manifest.json"
EXTS = {".png", ".jpg", ".jpeg", ".webp", ".gif"}


def iso_week_label(d: date) -> str:
    y, w, _ = d.isocalendar()
    return f"{y}-W{w:02d}"


def iso_week_range(d: date) -> str:
    from datetime import timedelta
    monday = d - timedelta(days=d.weekday())
    sunday = monday + timedelta(days=6)
    if monday.month == sunday.month:
        return f"{monday.strftime('%b %-d')}\u2013{sunday.day}, {sunday.year}"
    return f"{monday.strftime('%b %-d')} \u2013 {sunday.strftime('%b %-d, %Y')}"


def main():
    items = []
    if not IMAGES_DIR.exists():
        print("Ingen images/ mappe fundet — opretter tom manifest.")
    for year_dir in sorted(IMAGES_DIR.glob("[0-9][0-9][0-9][0-9]")):
        for month_dir in sorted(year_dir.glob("[0-9][0-9]")):
            for day_dir in sorted(month_dir.glob("[0-9][0-9]")):
                try:
                    d = date(int(year_dir.name), int(month_dir.name), int(day_dir.name))
                except ValueError:
                    continue
                for f in sorted(day_dir.iterdir()):
                    if f.suffix.lower() not in EXTS:
                        continue
                    rel = f.relative_to(ROOT).as_posix()
                    items.append({
                        "src": rel,
                        "date": d.isoformat(),
                        "year": d.year,
                        "month": f"{d.year}-{d.month:02d}",
                        "monthLabel": d.strftime("%B %Y"),
                        "week": iso_week_label(d),
                        "weekLabel": f"Week {d.isocalendar()[1]} \u2014 {iso_week_range(d)}",
                        "day": d.strftime("%A"),
                        "title": f.stem,
                    })

    items.sort(key=lambda x: (x["date"], x["src"]))
    items.reverse()  # nyeste først

    manifest = {
        "generated": date.today().isoformat(),
        "count": len(items),
        "items": items,
    }
    OUT_FILE.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Skrev {len(items)} billeder til {OUT_FILE}")


if __name__ == "__main__":
    main()
