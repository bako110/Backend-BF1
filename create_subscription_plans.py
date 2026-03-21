"""
Script pour créer les plans d'abonnement avec les bonnes catégories.
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017/bf1db")

from app.models.subscription_plan import SubscriptionPlan

async def create_plans():
    # Connexion MongoDB
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client.get_database()
    
    # Initialiser Beanie avec le modèle
    await init_beanie(database=db, document_models=[SubscriptionPlan])
    
    print("📝 Création des plans d'abonnement avec catégories...")
    print("=" * 60)
    
    # Définir les plans avec leurs catégories
    plans_data = [
        # Plans BASIC (1 500 XOF / mois)
        {
            "code": "basic_1m",
            "name": "Basic 1 Mois",
            "category": "basic",
            "duration_months": 1,
            "price_cents": 150000,  # 1 500 XOF
            "currency": "XOF",
            "is_active": True
        },
        {
            "code": "basic_3m",
            "name": "Basic 3 Mois",
            "category": "basic",
            "duration_months": 3,
            "price_cents": 405000,  # 4 050 XOF (10% réduction)
            "currency": "XOF",
            "is_active": True
        },
        {
            "code": "basic_12m",
            "name": "Basic 1 An",
            "category": "basic",
            "duration_months": 12,
            "price_cents": 1440000,  # 14 400 XOF (20% réduction)
            "currency": "XOF",
            "is_active": True
        },
        
        # Plans STANDARD (3 000 XOF / mois)
        {
            "code": "standard_1m",
            "name": "Standard 1 Mois",
            "category": "standard",
            "duration_months": 1,
            "price_cents": 300000,  # 3 000 XOF
            "currency": "XOF",
            "is_active": True
        },
        {
            "code": "standard_3m",
            "name": "Standard 3 Mois",
            "category": "standard",
            "duration_months": 3,
            "price_cents": 810000,  # 8 100 XOF (10% réduction)
            "currency": "XOF",
            "is_active": True
        },
        {
            "code": "standard_12m",
            "name": "Standard 1 An",
            "category": "standard",
            "duration_months": 12,
            "price_cents": 2880000,  # 28 800 XOF (20% réduction)
            "currency": "XOF",
            "is_active": True
        },
        
        # Plans PREMIUM (5 000 XOF / mois)
        {
            "code": "premium_1m",
            "name": "Premium 1 Mois",
            "category": "premium",
            "duration_months": 1,
            "price_cents": 500000,  # 5 000 XOF
            "currency": "XOF",
            "is_active": True
        },
        {
            "code": "premium_3m",
            "name": "Premium 3 Mois",
            "category": "premium",
            "duration_months": 3,
            "price_cents": 1350000,  # 13 500 XOF (10% réduction)
            "currency": "XOF",
            "is_active": True
        },
        {
            "code": "premium_12m",
            "name": "Premium 1 An",
            "category": "premium",
            "duration_months": 12,
            "price_cents": 4800000,  # 48 000 XOF (20% réduction)
            "currency": "XOF",
            "is_active": True
        }
    ]
    
    created_count = 0
    updated_count = 0
    
    for plan_data in plans_data:
        # Vérifier si le plan existe déjà
        existing_plan = await SubscriptionPlan.find_one(SubscriptionPlan.code == plan_data["code"])
        
        if existing_plan:
            # Mettre à jour la catégorie si elle n'est pas définie
            if not existing_plan.category:
                existing_plan.category = plan_data["category"]
                await existing_plan.save()
                print(f"✅ Plan mis à jour: {plan_data['name']} → category: {plan_data['category']}")
                updated_count += 1
            else:
                print(f"⏭️  Plan existe déjà: {plan_data['name']} (category: {existing_plan.category})")
        else:
            # Créer le nouveau plan
            plan = SubscriptionPlan(**plan_data)
            await plan.insert()
            print(f"✅ Plan créé: {plan_data['name']} (category: {plan_data['category']})")
            created_count += 1
    
    print("\n" + "=" * 60)
    print(f"📊 Résumé:")
    print(f"   - Plans créés: {created_count}")
    print(f"   - Plans mis à jour: {updated_count}")
    print(f"   - Plans existants: {len(plans_data) - created_count - updated_count}")
    
    # Afficher tous les plans
    print("\n" + "=" * 60)
    print("📋 Liste complète des plans:")
    all_plans = await SubscriptionPlan.find().to_list()
    for plan in all_plans:
        print(f"\n   {plan.name}")
        print(f"   - ID: {plan.id}")
        print(f"   - Code: {plan.code}")
        print(f"   - Catégorie: {plan.category}")
        print(f"   - Prix: {plan.price_cents/100} {plan.currency} ({plan.duration_months} mois)")

if __name__ == "__main__":
    asyncio.run(create_plans())
