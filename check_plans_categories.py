"""
Script pour vérifier et afficher les catégories des plans d'abonnement.
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

async def check_plans():
    # Connexion MongoDB
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client.get_database()
    
    # Initialiser Beanie avec le modèle
    await init_beanie(database=db, document_models=[SubscriptionPlan])
    
    print("🔍 Vérification des plans d'abonnement...")
    print("=" * 60)
    
    # Récupérer tous les plans
    plans = await SubscriptionPlan.find().to_list()
    
    if not plans:
        print("❌ Aucun plan trouvé dans la base de données!")
        return
    
    print(f"✅ {len(plans)} plan(s) trouvé(s)\n")
    
    for plan in plans:
        print(f"📋 Plan: {plan.name}")
        print(f"   - Code: {plan.code}")
        print(f"   - ID: {plan.id}")
        print(f"   - Catégorie: {plan.category if plan.category else '❌ NULL/VIDE'}")
        print(f"   - Durée: {plan.duration_months} mois")
        print(f"   - Prix: {plan.price_cents} centimes ({plan.price_cents/100} {plan.currency})")
        print(f"   - Actif: {'✅' if plan.is_active else '❌'}")
        print("-" * 60)
    
    # Compter les plans sans catégorie
    plans_without_category = [p for p in plans if not p.category]
    if plans_without_category:
        print(f"\n⚠️ {len(plans_without_category)} plan(s) sans catégorie:")
        for p in plans_without_category:
            print(f"   - {p.name} (code: {p.code}, ID: {p.id})")
    else:
        print("\n✅ Tous les plans ont une catégorie définie!")

if __name__ == "__main__":
    asyncio.run(check_plans())
