#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_site.py – v1.2 (07 juin 2025)
Indexe tous les PDF de /Public/Books sur pCloud
et écrit docs/books/books_data.json.
Aucun appel n’est fait si le fichier a < 1 h.
"""

import os, sys, time, json, requests, pathlib

# ————————————————————————— CONFIG
API_TOKEN      = os.environ.get("PCLOUD_TOKEN")
if not API_TOKEN:
    raise EnvironmentError("PCLOUD_TOKEN environment variable is required")
PCL_API_BASE   = "https://api.pcloud.com/"
ROOT_FOLDER_ID = "26585008409"          # ID de …/Public/Books
OUTPUT_JSON    = pathlib.Path("docs/books/books_data.json")
CACHE_TTL      = 3600                  # re-sync > 1 h

# ————————————————————————— pCloud helpers
def list_folder(fid: str, offset: int = 0, limit: int = 1000):
    params = {
        "access_token": API_TOKEN,
        "folderid": fid,
        "offset": offset,
        "limit": limit,
    }
    r = requests.get(f"{PCL_API_BASE}listfolder", params=params)
    d = r.json()
    if "metadata" not in d:
        raise RuntimeError(f"❌ Erreur listfolder : {d}")
    return d["metadata"].get("contents", [])

def get_link(fileid: str):
    d = requests.get(
        f"{PCL_API_BASE}getfilelink",
        params={"access_token": API_TOKEN, "fileid": fileid},
    ).json()
    host = d["hosts"][0]
    if not host.startswith("http"):
        host = "https://" + host
    return host + d["path"]

# ————————————————————————— recursion
def scan(fid, parent=None):
    res = []
    offset = 0
    while True:
        entries = list_folder(fid, offset=offset)
        if not entries:
            break
        offset += len(entries)
        for e in entries:
            if e.get("isfolder"):
                res += scan(e["folderid"], e["name"])
            elif e["name"].lower().endswith(".pdf"):
                res.append({
                    "title":   e["name"],
                    "folder":  parent,
                    "url":     get_link(e["fileid"]),
                    "created": e.get("created")
                })
    return res

# ————————————————————————— main
def main():
    if OUTPUT_JSON.exists() and time.time() - OUTPUT_JSON.stat().st_mtime < CACHE_TTL:
        print(f"⏩ Livres   SKIPPÉ (cache < {CACHE_TTL}s)")
        return

    print(f"→ Sync pCloud Livres (folderid={ROOT_FOLDER_ID})…")
    books = scan(ROOT_FOLDER_ID)
    OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_JSON.write_text(
        json.dumps(books, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )
    print(f"✅ {len(books)} livres indexés → {OUTPUT_JSON}")

if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(exc, file=sys.stderr)
        sys.exit(1)