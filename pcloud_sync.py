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

# ————————————————
# CONFIGURATION
# ————————————————
API_TOKEN      = os.environ.get("PCLOUD_TOKEN")
if not API_TOKEN:
    raise EnvironmentError("La variable d’environnement PCLOUD_TOKEN est requise")
PCL_API_BASE   = "https://api.pcloud.com"
ROOT_FOLDER_ID = "26585006317"             # folderid de /Public/Photos
OUTPUT_JSON    = "photo_metadata_all.json" # on écrase directement ce fichier

# extensions d’images autorisées
IMAGE_EXTS = {
    ".jpg", ".jpeg", ".png", ".gif",
    ".bmp", ".webp", ".tiff", ".heic",
}

# compteur global pour le suivi de progression
count = 0

# ————————————————
# FONCTIONS pCloud
# ————————————————
def list_folder(folderid: str, offset: int = 0, limit: int = 1000):
    """
    Liste le contenu (fichiers + sous-dossiers) d'un dossier pCloud,
    avec pagination.
    """
    params = {
        "access_token": API_TOKEN,
        "folderid":     folderid,
        "offset":       offset,
        "limit":        limit,
    }
    r = requests.get(f"{PCL_API_BASE}/listfolder", params=params)
    d = r.json()
    if "metadata" not in d or "contents" not in d["metadata"]:
        raise RuntimeError(f"❌ Erreur pCloud API (listfolder) : {d}")
    return d["metadata"]["contents"]

def get_download_link(fileid: str) -> str:
    """
    Récupère l’URL publique pour télécharger un fichier pCloud.
    """
    params = {"access_token": API_TOKEN, "fileid": fileid}
    r = requests.get(f"{PCL_API_BASE}/getfilelink", params=params)
    d = r.json()
    if d.get("result", 0) != 0 or "hosts" not in d or "path" not in d:
        raise RuntimeError(f"❌ Erreur pCloud API (getfilelink) : {d}")
    host = d["hosts"][0]
    if not host.startswith("http"):
        host = "https://" + host
    return host + d["path"]

# ————————————————
# PARCOURS RÉCUSRIF
# ————————————————
def traverse(folderid: str, parent_folder: str = None) -> list:
    """
    Parcourt récursivement un dossier pCloud et ne retient que les images
    (extensions définies dans IMAGE_EXTS).  
    Retourne une liste d’objets { title, folder, url, created }.
    """
    global count
    results = []
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
                # sous-dossier : redescendre dedans
                results.extend(traverse(entry["folderid"], entry["name"]))
            else:
                name, ext = entry["name"], os.path.splitext(entry["name"])[1].lower()
                if ext in IMAGE_EXTS:
                    url = get_download_link(entry["fileid"])
                    results.append({
                        "title":   name,
                        "folder":  parent_folder,
                        "url":     url,
                        "created": entry.get("created")
                    })

    return results

# ————————————————
# SCRIPT PRINCIPAL
# ————————————————
def main():
    print(f"→ Démarrage du scan pCloud → folderid={ROOT_FOLDER_ID}")
    photos = traverse(ROOT_FOLDER_ID)

    # Écrire le JSON en écrasant l'ancien
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(photos, f, indent=2, ensure_ascii=False)

    print(f"✅ {len(photos)} photos indexées dans → {OUTPUT_JSON}")

if __name__ == "__main__":
    main()
