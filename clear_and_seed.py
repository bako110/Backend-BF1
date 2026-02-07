"""
Script pour ÉCRASER complètement la base de données et la recréer
⚠️  ATTENTION: Ce script supprime TOUTES les données existantes
Usage: python clear_and_seed.py
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

async def clear_and_recreate_database():
    MONGODB_URI = os.getenv("MONGODB_URI")
    MONGODB_DBNAME = os.getenv("MONGODB_DBNAME", "Bf1_db")
    
    print("=" * 60)
    print("⚠️  NETTOYAGE COMPLET DE LA BASE DE DONNÉES")
    print("=" * 60)
    print(f"📦 Base de données: {MONGODB_DBNAME}")
    print("⚠️  Toutes les données vont être SUPPRIMÉES!")
    print("=" * 60)
    
    # Confirmation
    response = input("\n❓ Êtes-vous sûr de vouloir continuer? (oui/non): ")
    if response.lower() not in ['oui', 'yes', 'o', 'y']:
        print("\n❌ Opération annulée.")
        return
    
    print("\n🔌 Connexion à MongoDB...")
    client = AsyncIOMotorClient(MONGODB_URI)
    db = client[MONGODB_DBNAME]
    
    # Lister toutes les collections
    collections = await db.list_collection_names()
    print(f"\n📊 {len(collections)} collections trouvées:")
    for coll in collections:
        count = await db[coll].count_documents({})
        print(f"   • {coll}: {count} documents")
    
    # Supprimer toutes les collections
    print("\n🗑️  Suppression de toutes les collections...")
    for coll in collections:
        await db[coll].drop()
        print(f"   ✓ {coll} supprimée")
    
    print("\n✅ Base de données complètement nettoyée!")
    
    # Vérification
    remaining = await db.list_collection_names()
    if remaining:
        print(f"\n⚠️  Collections restantes: {remaining}")
    else:
        print("\n✅ Aucune collection restante - Base vide!")
    
    client.close()
    
    print("\n" + "=" * 60)
    print("🌱 PEUPLEMENT DE LA BASE DE DONNÉES")
    print("=" * 60)
    print("\n▶️  Exécution de seed.py...\n")
    
    # Importer et exécuter seed.py
    import sys
    sys.path.insert(0, os.path.dirname(__file__))
    
    # Réinitialiser les modules pour forcer le rechargement
    if 'seed' in sys.modules:
        del sys.modules['seed']
    
    # Importer le module seed
    import importlib.util
    spec = importlib.util.spec_from_file_location("seed", "seed.py")
    seed_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(seed_module)
    
    # Exécuter la fonction main de seed.py
    await seed_module.main()
    
    print("\n" + "=" * 60)
    print("✅ BASE DE DONNÉES RECRÉÉE AVEC SUCCÈS!")
    print("=" * 60)
    print("\n📊 Vérification finale...")
    
    # Vérification finale
    client = AsyncIOMotorClient(MONGODB_URI)
    db = client[MONGODB_DBNAME]
    
    final_collections = await db.list_collection_names()
    print(f"\n✅ {len(final_collections)} collections créées:\n")
    
    for coll in sorted(final_collections):
        count = await db[coll].count_documents({})
        status = "✅" if count > 0 else "⚠️"
        print(f"{status} {coll:30} {count:5} documents")
    
    # Vérifier popular_programs spécifiquement
    print("\n" + "=" * 60)
    print("🔍 VÉRIFICATION: popular_programs")
    print("=" * 60)
    
    programs = await db.popular_programs.find().to_list(length=10)
    if programs:
        print(f"\n✅ {len(programs)} programmes populaires créés:\n")
        for prog in programs:
            print(f"   📺 {prog.get('title', 'Sans titre')}")
            print(f"      ⏰ {prog.get('schedule', 'N/A')}")
            print(f"      📹 {prog.get('episodes', 0)} épisodes | ⭐ {prog.get('rating', 0)}/5\n")
    else:
        print("\n❌ ERREUR: Collection 'popular_programs' toujours vide!")
    
    # Vérifier replays
    print("=" * 60)
    print("🔍 VÉRIFICATION: replays")
    print("=" * 60)
    
    replays = await db.replays.find().to_list(length=10)
    if replays:
        print(f"\n✅ {len(replays)} replays créés:\n")
        for replay in replays:
            print(f"   ▶️  {replay.get('title', 'Sans titre')}")
            print(f"      ⏱️  {replay.get('duration_minutes', 0)} min | ⭐ {replay.get('rating', 0)}/5\n")
    else:
        print("\n❌ ERREUR: Collection 'replays' toujours vide!")
    
    client.close()
    
    print("=" * 60)
    print("🎉 TERMINÉ!")
    print("=" * 60)
    print("\n💡 Prochaines étapes:")
    print("   1. Redémarrez votre serveur backend")
    print("   2. Rechargez votre application")
    print("   3. Les données devraient maintenant s'afficher!\n")

if __name__ == "__main__":
    asyncio.run(clear_and_recreate_database())
