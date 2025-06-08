#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generate_books.py
Lit docs/books/books_data.json et génère :
  - docs/books/index.md
  - un répertoire docs/books/‹slug›/index.md pour chaque livre
"""

import os
import json
import re
from pathlib import Path

IN_JSON = Path("docs/books/books_data.json")
OUT_DIR = Path("docs/books")

def slugify(text):
    slug = re.sub(r"[^\w\s-]", "", text.lower())
    slug = re.sub(r"[\s_]+", "-", slug).strip("-")
    return slug

def main():
    if not IN_JSON.exists():
        raise FileNotFoundError(f"{IN_JSON} introuvable. Lancez d’abord pcloud_books_sync.py")
    books = json.load(open(IN_JSON, encoding="utf-8"))

    # 1. Générer index.md
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    index = ["---", "title: Livres", "---", "", "# 📚 Livres", ""]
    for b in books:
        slug = slugify(b["title"])
        index.append(f"- [{b['title']}](./{slug}/)")
    with open(OUT_DIR / "index.md", "w", encoding="utf-8") as f:
        f.write("\n".join(index))

    # 2. Générer chaque page
    for b in books:
        slug = slugify(b["title"])
        page_dir = OUT_DIR / slug
        page_dir.mkdir(exist_ok=True)
        content = [
            "---",
            f"title: {b['title']}",
            "---",
            "",
            f'<iframe src="javascripts/pdfjs/web/viewer.mjs?file={b["url"]}" ',
            '        width="100%" height="800px"></iframe>'
        ]
        with open(page_dir / "index.md", "w", encoding="utf-8") as f:
            f.write("\n".join(content))

    print(f"✅ {len(books)} pages de livres générées dans → {OUT_DIR}")

if __name__ == "__main__":
    main()
