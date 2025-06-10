#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generate_gallery.py  ·  v3.8  (12 juin 2025)

– Lit docs/gallery/gallery_data.json (date au format "YYYY:MM:DD")
– Remplace ":" par "-" → "YYYY-MM-DD"
– Génère docs/gallery/gallery.md avec :
    • front-matter pour masquer la navigation
    • <a … data-date="YYYY-MM-DD">
    • <div class="all-photos"> contenant tous les <a> (non affichés)
    • <div class="gallery-grid"> vide au départ
"""

import json, html
from pathlib import Path

esc = lambda t: html.escape(str(t), quote=True)

IN  = Path("docs/gallery/gallery_data.json")
OUT = Path("docs/gallery/gallery.md")

# 1) Charger le JSON
pics = json.loads(IN.read_text("utf-8"))
OUT.parent.mkdir(parents=True, exist_ok=True)

# 2) Écrire le Markdown
with OUT.open("w", encoding="utf-8") as md:
    md.write("---\n")
    md.write("hide:\n")
    md.write("  - navigation   # masque la barre Material sur cette page\n")
    md.write("---\n\n")
    md.write("# Galerie photo\n\n")
    md.write('<div id="gallery">\n')
    md.write('  <aside id="filters"></aside>\n')
    md.write('  <div class="gallery-grid"></div>\n')
    md.write('  <div class="all-photos" style="display:none">\n')
    for p in pics:
        # Normaliser la date : "YYYY:MM:DD" → "YYYY-MM-DD"
        raw_date = (p.get("date") or "").strip()
        if raw_date and ":" in raw_date:
            dt = raw_date.replace(":", "-")
        else:
            dt = raw_date  # peut être vide ou déjà correct
        # Construire la balise <a>
        md.write(
            f'    <a href="{esc(p["url"])}" '
            f'data-title="{esc(p["title"])}" '
            f'data-folder="{esc(p.get("folder",""))}" '
            f'data-keywords="{",".join(p.get("keywords",[]))}" '
            f'data-place="{esc(p.get("place",""))}" '
            f'data-date="{esc(dt)}"></a>\n'
        )
    md.write("  </div>\n")
    md.write("</div>\n")

print(f"✔ Markdown généré : {OUT} ({len(pics)} photos)")
