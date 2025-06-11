#!/usr/bin/env python3
"""Add missing Singapur photos to docs/gallery/gallery_data.json."""
import json
from pathlib import Path
from urllib.parse import quote
from datetime import datetime
import os

GALLERY_JSON = Path("docs/gallery/gallery_data.json")
MERGED_JSON = Path("photo_metadata_merged.json")
BASE_URL = "https://filedn.com/lu9cusIvW31SULdQ8WPS6W0/Photos"
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".tiff", ".heic"}


def load_json(path: Path):
    if not path.exists():
        raise FileNotFoundError(path)
    return json.loads(path.read_text("utf-8"))


def normalize_date(created: str) -> str:
    """Convert "Thu, 17 Jun 2010 23:08:12 +0000" -> "2010:06:17"."""
    if not created:
        return ""
    try:
        dt = datetime.strptime(created, "%a, %d %b %Y %H:%M:%S %z")
        return dt.strftime("%Y:%m:%d")
    except Exception:
        return ""


def main():
    gallery = load_json(GALLERY_JSON)
    existing_urls = {p["url"] for p in gallery}
    photos = load_json(MERGED_JSON)
    added = 0

    for p in photos:
        folder = p.get("folder", "")
        if not folder.startswith("Singapur"):
            continue
        title = p.get("title") or ""
        ext = Path(title).suffix.lower()
        if ext not in IMAGE_EXTS:
            continue
        url = f"{BASE_URL}/{quote(folder)}/{quote(title)}"
        if url in existing_urls:
            continue
        entry = {
            "title": os.path.splitext(title)[0],
            "url": url,
            "folder": "Singapur",
            "keywords": [],
            "place": "",
            "date": normalize_date(p.get("created", "")),
        }
        gallery.append(entry)
        existing_urls.add(url)
        added += 1

    GALLERY_JSON.write_text(json.dumps(gallery, indent=2, ensure_ascii=False))
    print(f"Added {added} Singapur photos")


if __name__ == "__main__":
    main()
