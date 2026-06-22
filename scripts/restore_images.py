"""
Migre les images Cloudinary (https://res.cloudinary.com/...) vers le stockage local.
Parcourt toutes les collections MongoDB et remplace les URLs dans les champs image/thumbnail/poster/avatar_url.
"""
import os
import uuid
import requests
from pathlib import Path
from pymongo import MongoClient

MONGO_URL = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
DB_NAME   = os.getenv("MONGODB_DBNAME", "Bf1_db")
BASE_URL  = os.getenv("BASE_URL", "http://161.97.117.46:8090")

BASE_DIR   = Path(__file__).resolve().parents[1]
UPLOAD_DIR = BASE_DIR / "static" / "uploads" / "bf1"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

IMAGE_FIELDS = ["image", "thumbnail", "poster", "avatar_url", "cover", "banner", "photo"]

client = MongoClient(MONGO_URL)
db     = client[DB_NAME]


def download_image(url: str) -> str | None:
    try:
        resp = requests.get(url, timeout=30)
        if resp.status_code != 200:
            print(f"  ✗ HTTP {resp.status_code}: {url}")
            return None
        ct  = resp.headers.get("content-type", "")
        ext = ".png" if "png" in ct else ".webp" if "webp" in ct else ".jpg"
        filename = uuid.uuid4().hex + ext
        (UPLOAD_DIR / filename).write_bytes(resp.content)
        return f"{BASE_URL}/static/uploads/bf1/{filename}"
    except Exception as e:
        print(f"  ✗ Erreur: {e} — {url}")
        return None


def is_cloudinary(url) -> bool:
    return isinstance(url, str) and "cloudinary.com" in url


total_migrated = 0

for col_name in sorted(db.list_collection_names()):
    collection = db[col_name]
    migrated   = 0

    # Construire le filtre : au moins un champ contient une URL cloudinary
    query = {"$or": [{field: {"$regex": "cloudinary\\.com"}} for field in IMAGE_FIELDS]}
    docs  = list(collection.find(query))

    if not docs:
        continue

    print(f"\n[{col_name}] {len(docs)} document(s) à migrer")

    for doc in docs:
        updates = {}
        for field in IMAGE_FIELDS:
            val = doc.get(field)
            if is_cloudinary(val):
                print(f"  → {field}: {val[:60]}...")
                new_url = download_image(val)
                if new_url:
                    updates[field] = new_url
                    print(f"  ✓ {new_url}")

        if updates:
            collection.update_one({"_id": doc["_id"]}, {"$set": updates})
            migrated += 1

    print(f"  ✅ {migrated}/{len(docs)} migré(s)")
    total_migrated += migrated

print(f"\n{'='*50}")
print(f"MIGRATION TERMINÉE — {total_migrated} document(s) mis à jour")
print(f"Images dans : {UPLOAD_DIR}")
