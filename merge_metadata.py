#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
merge_metadata.py · v1.0 (15 juin 2025)
Lit photo_metadata_all.json et enrichit/filtre/merge les métadonnées selon vos besoins.
"""
import json
import sys
from pathlib import Path

INPUT_JSON  = Path("photo_metadata_all.json")
OUTPUT_JSON = Path("photo_metadata_merged.json")

if not INPUT_JSON.exists():
    print(f"❌ Fichier introuvable : {INPUT_JSON}", file=sys.stderr)
    sys.exit(1)

with open(INPUT_JSON, encoding="utf-8") as f:
    photos = json.load(f)

# Exemple de traitement : suppression des doublons sur (url)
seen = set()
merged = []
for p in photos:
    if p["url"] in seen:
        continue
    seen.add(p["url"])
    merged.append(p)

with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
    json.dump(merged, f, indent=2, ensure_ascii=False)

print(f"✅ Métadonnées fusionnées : {len(merged)} entrées → {OUTPUT_JSON}")
