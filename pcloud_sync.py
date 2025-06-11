#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pcloud_sync.py
Récupère récursivement toutes les images du dossier Public/Photos de pCloud
et génère photo_metadata_all.json à la racine du projet.
"""

import os
import json
import requests

# ———————————————— CONFIGURATION ————————————————
API_TOKEN = os.environ.get("PCLOUD_TOKEN")
if not API_TOKEN:
    raise EnvironmentError("La variable d’environnement PCLOUD_TOKEN est requise")
PCL_API_BASE = "https://api.pcloud.com"
ROOT_FOLDER_ID = "26585006317"             # ID du dossier /Public/Photos
OUTPUT_JSON = "photo_metadata_all.json"    # on écrase directement ce fichier

# ———————————————— EXTENSIONS D’IMAGES ACCEPTÉES ————————————————
IMAGE_EXTS = {
    ".jpg", ".jpeg", ".png", ".gif",
    ".bmp", ".webp", ".tiff", ".heic",
}

# compteur global pour le suivi de progression
count = 0

def list_folder(folderid, offset=0, limit=1000):
    """Liste le contenu d'un dossier pCloud (avec pagination)."""
    params = {
        "access_token": API_TOKEN,
        "folderid": folderid,
        "offset": offset,
        "limit": limit,
    }
    resp = requests.get(f"{PCL_API_BASE}/listfolder", params=params)
    data = resp.json()
    if "metadata" not in data or "contents" not in data["metadata"]:
        raise RuntimeError(f"❌ Erreur listfolder : {data}")
    return data["metadata"]["contents"]

def get_download_link(fileid):
    """Récupère l'URL publique pour télécharger un fichier."""
    params = {"access_token": API_TOKEN, "fileid": fileid}
    resp = requests.get(f"{PCL_API_BASE}/getfilelink", params=params)
    data = resp.json()
    if data.get("result") != 0 or "hosts" not in data or "path" not in data:
        raise RuntimeError(f"❌ Erreur getfilelink : {data}")
    host = data["hosts"][0]
    if not host.startswith("http"):
        host = "https://" + host
    return host + data["path"]

def traverse(folderid, parent_folder=None):
    """
    Parcourt récursivement le dossier donné et retourne la liste des images.
    Chaque élément est un dict {"title", "folder", "url", "created"}.
    """
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
                items.extend(traverse(entry["folderid"], entry.get("name")))
            else:
                name = entry.get("name", "")
                ext = os.path.splitext(name)[1].lower()
                if ext in IMAGE_EXTS:
                    url = get_download_link(entry["fileid"])
                    items.append({
                        "title":   name,
                        "folder":  parent_folder,
                        "url":     url,
                        "created": entry.get("created")
                    })
    return items

def main():
    print(f"→ Synchronisation pCloud Photos (folderid={ROOT_FOLDER_ID})…")
    photos = traverse(ROOT_FOLDER_ID)
    # Création du dossier si besoin (ici OUTPUT_JSON est à la racine, donc dirname peut être vide)
    directory = os.path.dirname(OUTPUT_JSON)
    if directory:
        os.makedirs(directory, exist_ok=True)
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(photos, f, indent=2, ensure_ascii=False)
    print(f"✅ {len(photos)} images indexées → {OUTPUT_JSON}")

if __name__ == "__main__":
    main()
