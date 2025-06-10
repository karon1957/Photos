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
import shutil
 40uism-codex/corriger-un-bug-majeur
import unicodedata
main
from pathlib import Path

IN_JSON = Path("docs/books/books_data.json")
OUT_DIR = Path("docs/books")

def slugify(text: str) -> str:
    """Convert `text` to a safe slug for file/folder names."""
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^\w\s-]", "", text.lower())
    slug = re.sub(r"[\s_]+", "-", slug).strip("-")
    return slug

def main():
    if not IN_JSON.exists():
        raise FileNotFoundError(f"{IN_JSON} introuvable. Lancez d’abord pcloud_books_sync.py")
    books = json.load(open(IN_JSON, encoding="utf-8"))

 40uism-codex/corriger-un-bug-majeur
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # Make sure the output directory exists before trying to iterate over it
    OUT_DIR.mkdir(parents=True, exist_ok=True)
 main
    # Nettoyer l'ancien contenu (fichiers/dossiers de livres)
    for item in OUT_DIR.iterdir():
        if item.name in {"index.md", IN_JSON.name}:
            continue
        if item.is_dir():
            shutil.rmtree(item)
        else:
            item.unlink()

    # 1. Générer index.md
    index = ["---", "title: Livres", "---", "", "# 📚 Livres", ""]
    for b in books:
        base_title = Path(b["title"]).stem
        slug = slugify(base_title)
        index.append(f"- [{base_title}](./{slug}/)")
    with open(OUT_DIR / "index.md", "w", encoding="utf-8") as f:
        f.write("\n".join(index))

    # 2. Générer chaque page
    for b in books:
        base_title = Path(b["title"]).stem
        slug = slugify(base_title)
        page_dir = OUT_DIR / slug
        page_dir.mkdir(exist_ok=True)
        content = [
            "---",
            f"title: {base_title}",
            "---",
            "",
            f'<iframe src="/javascripts/pdfjs/web/viewer.mjs?file={b["url"]}" ',
            '        width="100%" height="800px"></iframe>'
        ]
        with open(page_dir / "index.md", "w", encoding="utf-8") as f:
            f.write("\n".join(content))

    print(f"✅ {len(books)} pages de livres générées dans → {OUT_DIR}")

if __name__ == "__main__":
    main()