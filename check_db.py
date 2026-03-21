"""
Script pour vérifier l'état des collections MongoDB
Usage: python check_db.py
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os

async def check_collections():
    MONGODB_URI = os.getenv("MONGODB_URI")
    MONGODB_DBNAME = os.getenv("MONGODB_DBNAME", "Bf1_db")
    
    print(f"🔌 Connexion à MongoDB...")
    print(f"📦 Base de données: {MONGODB_DBNAME}\n")
    
    client = AsyncIOMotorClient(MONGODB_URI)
    db = client[MONGODB_DBNAME]
    
    print("=" * 60)
    print("📊 ÉTAT DES COLLECTIONS")
    print("=" * 60)
    
    collections = await db.list_collection_names()
    
    for coll in sorted(collections):
        count = await db[coll].count_documents({})
        status = "✅" if count > 0 else "❌"
        print(f"{status} {coll:30} {count:5} documents")
    
    print("\n" + "=" * 60)
    print("🔍 DÉTAILS: popular_programs")
    print("=" * 60)
    
    programs = await db.popular_programs.find().to_list(length=10)
    if programs:
        print(f"\n✅ {len(programs)} programmes populaires trouvés:\n")
        for prog in programs:
            title = prog.get('title', 'Sans titre')
            schedule = prog.get('schedule', 'N/A')
            episodes = prog.get('episodes', 0)
            rating = prog.get('rating', 0)
            print(f"   📺 {title}")
            print(f"      ⏰ {schedule}")
            print(f"      📹 {episodes} épisodes | ⭐ {rating}/5")
            print()
    else:
        print("\n❌ Collection 'popular_programs' VIDE!")
        print("\n💡 Solution: Exécutez 'python seed.py' pour peupler la base\n")
    
    print("=" * 60)
    print("🔍 DÉTAILS: replays")
    print("=" * 60)
    
    replays = await db.replays.find().to_list(length=10)
    if replays:
        print(f"\n✅ {len(replays)} replays trouvés:\n")
        for replay in replays:
            title = replay.get('title', 'Sans titre')
            duration = replay.get('duration_minutes', 0)
            rating = replay.get('rating', 0)
            print(f"   ▶️  {title}")
            print(f"      ⏱️  {duration} min | ⭐ {rating}/5")
            print()
    else:
        print("\n❌ Collection 'replays' VIDE!")
        print("\n💡 Solution: Exécutez 'python seed.py' pour peupler la base\n")
    
    client.close()
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(check_collections())
