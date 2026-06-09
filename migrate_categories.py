"""
Nettoie les champs 'category' de toutes les collections contenu :
- strip des espaces/tabs/newlines
- remplacement des espaces insécables \xa0 par espace normal
- normalisation unicode NFC
"""
import asyncio
import unicodedata
import os
from motor.motor_asyncio import AsyncIOMotorClient


def clean(value: str) -> str:
    if not isinstance(value, str):
        return value
    value = value.replace('\xa0', ' ').replace('\u200b', '')
    value = unicodedata.normalize('NFC', value)
    return value.strip()


COLLECTIONS = ['magazine', 'jtandmag', 'divertissement', 'reportage', 'tele_realite']


async def migrate():
    MONGODB_URI = os.getenv("MONGODB_URI")
    MONGODB_DBNAME = os.getenv("MONGODB_DBNAME", "Bf1_db")

    client = AsyncIOMotorClient(MONGODB_URI)
    db = client[MONGODB_DBNAME]

    for coll_name in COLLECTIONS:
        coll = db[coll_name]
        docs = await coll.find({"category": {"$exists": True}}).to_list(length=None)
        updated = 0
        for doc in docs:
            original = doc.get('category', '')
            cleaned = clean(original)
            if cleaned != original:
                await coll.update_one({"_id": doc["_id"]}, {"$set": {"category": cleaned}})
                updated += 1
                print(f"  [{coll_name}] {repr(original)} -> {repr(cleaned)}")
        print(f"[{coll_name}] {updated}/{len(docs)} documents mis a jour")

    client.close()
    print("Migration terminee.")


if __name__ == "__main__":
    asyncio.run(migrate())
