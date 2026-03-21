"""
Script pour supprimer les anciens index et créer les nouveaux avec contraintes unique
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import IndexModel
import os

# Configuration MongoDB
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DATABASE_NAME = "Bf1_db"  # Nom avec majuscule pour correspondre à la base existante

async def fix_user_indexes():
    """Supprime les anciens index et crée les nouveaux avec contraintes unique"""
    
    # Connexion à MongoDB
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client[DATABASE_NAME]
    users_collection = db["users"]
    
    print("🔧 Correction des index de la collection 'users'...")
    
    try:
        # 1. Lister les index existants
        print("\n📋 Index existants:")
        existing_indexes = await users_collection.list_indexes().to_list(None)
        for idx in existing_indexes:
            print(f"  - {idx['name']}: {idx.get('key', {})}")
        
        # 2. Supprimer les anciens index (sauf _id_)
        print("\n🗑️  Suppression des anciens index...")
        for idx in existing_indexes:
            if idx['name'] != '_id_':
                try:
                    await users_collection.drop_index(idx['name'])
                    print(f"  ✅ Supprimé: {idx['name']}")
                except Exception as e:
                    print(f"  ⚠️  Erreur suppression {idx['name']}: {e}")
        
        # 3. Nettoyer les doublons de phone=null
        print("\n🧹 Nettoyage des doublons de phone=null...")
        
        # Compter les utilisateurs avec phone=null
        null_phone_count = await users_collection.count_documents({"phone": None})
        print(f"  📊 Utilisateurs avec phone=null: {null_phone_count}")
        
        if null_phone_count > 1:
            # Garder le premier, supprimer phone des autres
            users_with_null_phone = await users_collection.find({"phone": None}).to_list(None)
            print(f"  🔧 Mise à jour de {len(users_with_null_phone) - 1} documents...")
            
            # Garder le premier, mettre à jour les autres pour enlever le champ phone
            for i, user in enumerate(users_with_null_phone):
                if i > 0:  # Garder le premier
                    await users_collection.update_one(
                        {"_id": user["_id"]},
                        {"$unset": {"phone": ""}}
                    )
            print(f"  ✅ Doublons nettoyés")
        
        # 4. Créer les nouveaux index avec contraintes unique
        print("\n✨ Création des nouveaux index...")
        
        new_indexes = [
            IndexModel([("email", 1)], unique=True, sparse=True, name="email_1_unique"),
            IndexModel([("username", 1)], unique=True, name="username_1_unique"),
            IndexModel([("phone", 1)], unique=True, sparse=True, name="phone_1_unique"),
            IndexModel([("is_premium", 1)], name="is_premium_1"),
            IndexModel([("created_at", 1)], name="created_at_1"),
        ]
        
        result = await users_collection.create_indexes(new_indexes)
        print(f"  ✅ Index créés: {result}")
        
        # 5. Vérifier les nouveaux index
        print("\n📋 Nouveaux index:")
        new_existing_indexes = await users_collection.list_indexes().to_list(None)
        for idx in new_existing_indexes:
            unique_str = " (UNIQUE)" if idx.get('unique') else ""
            sparse_str = " (SPARSE)" if idx.get('sparse') else ""
            print(f"  - {idx['name']}: {idx.get('key', {})}{unique_str}{sparse_str}")
        
        print("\n✅ Correction des index terminée avec succès!")
        
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        raise
    
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(fix_user_indexes())
