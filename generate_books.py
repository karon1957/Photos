#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generate_books.py
Lit docs/books/books_data.json et génère :
  - docs/books/index.md
  - un répertoire docs/books/‹slug›/index.md pour chaque livre
"""

import json
import re
import shutil
import unicodedata
from pathlib import Path

IN_JSON = Path("docs/books/books_data.json")
OUT_DIR = Path("docs/books")

def slugify(text: str) -> str:
    """Convertit `text` en slug utilisable pour nom de dossier/fichier."""
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^\w\s-]", "", text.lower())
    slug = re.sub(r"[\s_]+", "-", slug).strip("-")
    return slug

def main():
    if not IN_JSON.exists():
        raise FileNotFoundError(f"{IN_JSON} introuvable. Lancez d’abord pcloud_books_sync.py")
    books = json.load(IN_JSON.open(encoding="utf-8"))

    # Crée le dossier de sortie s'il n'existe pas
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Nettoyer l'ancien contenu (sauf index.md et le JSON source)
    for item in OUT_DIR.iterdir():
        if item.name in {"index.md", IN_JSON.name}:
            continue
        if item.is_dir():
            shutil.rmtree(item)
        else:
            item.unlink()

    # 2. Générer docs/books/index.md
    index_lines = [
        "---",
        "title: Livres",
        "---",
        "",
        "# 📚 Livres",
        ""
    ]
    for entry in books:
        base_title = Path(entry["title"]).stem
        slug = slugify(base_title)
        index_lines.append(f"- [{base_title}](./{slug}/)")
    (OUT_DIR / "index.md").write_text("\n".join(index_lines), encoding="utf-8")

    # 3. Générer une page par livre
    for entry in books:
        base_title = Path(entry["title"]).stem
        slug = slugify(base_title)
        page_dir = OUT_DIR / slug
        page_dir.mkdir(exist_ok=True)

        content = [
            "---",
            f"title: {base_title}",
            "---",
            "",
            # Intégration du viewer PDF
            f'<iframe src="/javascripts/pdfjs/web/viewer.mjs?file={entry["url"]}"',
            '        width="100%" height="800px"></iframe>'
        ]
        (page_dir / "index.md").write_text("\n".join(content), encoding="utf-8")

    print(f"✅ {len(books)} pages de livres générées dans → {OUT_DIR}")

if __name__ == "__main__":
    main()
