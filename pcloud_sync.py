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
# FONCTIONS pCloud
# ————————————————
def list_folder(folderid, offset=0, limit=1000):
    """Liste le contenu complet d'un dossier pCloud (pagination)."""
    params = {
        "access_token": API_TOKEN,
        "folderid": folderid,
        "offset": offset,
        "limit": limit,
    }
    r = requests.get(f"{PCL_API_BASE}/listfolder", params=params)
    data = r.json()
    if "metadata" not in data:
        raise RuntimeError(f"❌ Erreur pCloud API (listfolder) : {data}")
    return data["metadata"].get("contents", [])

def get_download_link(fileid):
    """Récupère l’URL publique pour télécharger un fichier."""
    r = requests.get(
        f"{PCL_API_BASE}/getfilelink",
        params={"access_token": API_TOKEN, "fileid": fileid}
    )
    data = r.json()
    if "hosts" not in data:
        raise RuntimeError(f"❌ Erreur pCloud API (getfilelink) : {data}")
    host = data["hosts"][0]
    if not host.startswith("http"):
        host = "https://" + host
    return host + data["path"]

# ————————————————
# PARCOURS RÉCUSRIF
# ————————————————
IMAGE_EXTS = {
    ".jpg", ".jpeg", ".png", ".gif",
    ".bmp", ".webp", ".tiff", ".heic",
}

def traverse(folderid, parent_folder=None):
    """Parcourt récursivement un dossier pCloud et ne retient que les images."""
    global count
    items = []
    offset = 0
    while True:
        entries = list_folder(folderid, offset=offset)
        if not entries:
            break
        offset += len(entries)
        for entry in entries:
            count += 1
            if count % 50 == 0:
                print(f"> Scanné {count} éléments…")
            if entry.get("isfolder"):
                items.extend(traverse(entry["folderid"], entry["name"]))
            else:
                ext = os.path.splitext(entry["name"])[1].lower()
                if ext in IMAGE_EXTS:
                    url = get_download_link(entry["fileid"])
                    items.append({
                        "title":   entry["name"],
                        "folder":  parent_folder,
                        "url":     url,
                        "created": entry.get("created")
                    })
    return items

# ————————————————
# SCRIPT PRINCIPAL
# ————————————————
def main():
    print(f"> Démarrage du scan pCloud → folderid={ROOT_FOLDER_ID}")
    photos = traverse(ROOT_FOLDER_ID)
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(photos, f, indent=2, ensure_ascii=False)
    print(f"✅ {len(photos)} photos indexées dans → {OUTPUT_JSON}")

if __name__ == "__main__":
    main()
