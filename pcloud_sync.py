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
API_TOKEN      = "bMQrZNRzgW7NvywfZXyvbVkZQKSy7UVfRYHYeoDoMIDyv0tCjTLX"
PCL_API_BASE   = "https://api.pcloud.com"
ROOT_FOLDER_ID = "26585006317"               # folderid de /Public/Photos
OUTPUT_JSON    = "photo_metadata_all.json"   # on écrase directement ce fichier

# Compteur global pour le suivi de progression
count = 0

# ————————————————
# FONCTIONS pCloud
# ————————————————
def list_folder(folderid):
    """Liste le contenu du dossier pCloud."""
    r = requests.get(
        f"{PCL_API_BASE}/listfolder",
        params={"access_token": API_TOKEN, "folderid": folderid}
    )
    data = r.json()
    if "metadata" not in data:
        raise RuntimeError(f"❌ Erreur pCloud API (listfolder) : {data}")
    return data["metadata"]["contents"]

def get_download_link(fileid):
    """Récupère l’URL publique pour télécharger un fichier."""
    r = requests.get(
        f"{PCL_API_BASE}/getfilelink",
        params={"access_token": API_TOKEN, "fileid": fileid}
    )
    data = r.json()
    if "hosts" not in data:
        raise RuntimeError(f"❌ Erreur pCloud API (getfilelink) : {data}")
    return data["hosts"][0] + data["path"]

# ————————————————
# PARCOURS RÉCUSRIF
# ————————————————
def traverse(folderid, parent_folder=None):
    """
    Récursive : 
      - si c’est un dossier, on redescend dedans
      - si c’est un fichier, on construit son entrée
    """
    global count
    items = []
    for entry in list_folder(folderid):
        count += 1
        if count % 50 == 0:
            print(f"> Scanné {count} éléments…")
        if entry.get("isfolder"):
            items.extend(traverse(entry["folderid"], entry["name"]))
        else:
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
