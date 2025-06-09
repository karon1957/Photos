#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pcloud_sync.py
Récupère récursivement toutes les photos du dossier Public/Photos de pCloud
et génère photo_metadata_all.json à la racine du projet.
"""

import os
import json
import requests

# ————————————————
# CONFIGURATION
# ————————————————
# Remplacez ici par votre token si vous préférez en dur
API_TOKEN      = os.environ.get("PCLOUD_TOKEN")
if not API_TOKEN:
    raise EnvironmentError("PCLOUD_TOKEN environment variable is required")
PCL_API_BASE   = "https://api.pcloud.com"
ROOT_FOLDER_ID = "26585006317"               # folderid de /Public/Photos
OUTPUT_JSON    = "photo_metadata_all.json"   # on écrase directement ce fichier

# Compteur global pour le suivi de progression
count = 0

# ————————————————
# FONCTIONS pCloud (identiques à pcloud_sync)
# ————————————————
def list_folder(folderid, offset=0, limit=1000):
    params = {
        "access_token": API_TOKEN,
        "folderid": folderid,
        "offset": offset,
        "limit": limit,
    }
    resp = requests.get(f"{PCL_API_BASE}listfolder", params=params)
    data = resp.json()
    if data.get("result") != 0:
        raise RuntimeError(f"❌ Erreur listfolder : {data}")
    return data["metadata"].get("contents", [])

def get_download_link(fileid):
    resp = requests.get(
        f"{PCL_API_BASE}getfilelink",
        params={"access_token": API_TOKEN, "fileid": fileid}
    )
    data = resp.json()
    if data.get("result") != 0:
        raise RuntimeError(f"❌ Erreur getfilelink : {data}")
    host = data["hosts"][0]
    if not host.startswith("http"):
        host = "https://" + host
    return host + data["path"]

# ————————————————
# PARCOURS RÉCUSRIF (PDFs uniquement)
# ————————————————
def traverse(folderid):
    items = []
    offset = 0
    while True:
        entries = list_folder(folderid, offset=offset)
        if not entries:
            break
        offset += len(entries)
        for entry in entries:
            if entry.get("isfolder"):
                items.extend(traverse(entry["folderid"]))
            else:
                name, ext = entry["name"], os.path.splitext(entry["name"])[1].lower()
                if ext != ".pdf":
                    continue  # ignorer tout autre format (.odt, etc.)
                url = get_download_link(entry["fileid"])
                items.append({
                    "title": name,
                    "url":   url
                })
    return items

def main():
    print(f"→ Synchronisation pCloud Livres (folderid={ROOT_FOLDER_ID})…")
    books = traverse(ROOT_FOLDER_ID)
    os.makedirs(os.path.dirname(OUTPUT_JSON), exist_ok=True)
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(books, f, indent=2, ensure_ascii=False)
    print(f"✅ {len(books)} livres indexés dans → {OUTPUT_JSON}")

if __name__ == "__main__":
    main()