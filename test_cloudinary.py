#!/usr/bin/env python3
"""
Script de test pour vérifier la configuration Cloudinary
"""

import os
import sys
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Ajouter le chemin du projet
sys.path.insert(0, os.path.dirname(__file__))

from app.services.cloudinary_service import cloudinary_service

def test_cloudinary_config():
    """Tester la configuration Cloudinary"""
    print("🔧 Test de la configuration Cloudinary...")
    print(f"Cloud Name: {os.getenv('CLOUDINARY_CLOUD_NAME')}")
    print(f"API Key: {os.getenv('CLOUDINARY_API_KEY')}")
    print(f"API Secret: {'*' * len(os.getenv('CLOUDINARY_API_SECRET', ''))}")
    print()

def test_upload_from_url():
    """Tester l'upload depuis une URL"""
    print("📤 Test d'upload depuis une URL...")
    
    try:
        # URL d'une image de test
        test_url = "https://via.placeholder.com/800x600.png?text=BF1+Test"
        
        result = cloudinary_service.upload_from_url(
            url=test_url,
            folder="bf1/test",
            public_id="test-image"
        )
        
        print("✅ Upload réussi !")
        print(f"URL: {result['url']}")
        print(f"Public ID: {result['public_id']}")
        print(f"Dimensions: {result['width']}x{result['height']}")
        print()
        
        return result['public_id']
        
    except Exception as e:
        print(f"❌ Erreur lors de l'upload: {e}")
        return None

def test_get_image_url(public_id):
    """Tester la génération d'URL avec transformations"""
    print("🖼️ Test de génération d'URL avec transformations...")
    
    try:
        # URL originale
        original_url = cloudinary_service.get_image_url(public_id)
        print(f"URL originale: {original_url}")
        
        # URL avec transformation (redimensionnement)
        transformed_url = cloudinary_service.get_image_url(
            public_id,
            transformation={
                "width": 400,
                "height": 300,
                "crop": "fill",
                "quality": "auto"
            }
        )
        print(f"URL transformée (400x300): {transformed_url}")
        print()
        
    except Exception as e:
        print(f"❌ Erreur lors de la génération d'URL: {e}")

def test_delete_image(public_id):
    """Tester la suppression d'une image"""
    print("🗑️ Test de suppression d'image...")
    
    try:
        success = cloudinary_service.delete_image(public_id)
        
        if success:
            print("✅ Image supprimée avec succès !")
        else:
            print("⚠️ Image non trouvée ou déjà supprimée")
        print()
        
    except Exception as e:
        print(f"❌ Erreur lors de la suppression: {e}")

def main():
    """Fonction principale"""
    print("=" * 60)
    print("🧪 TEST CLOUDINARY - BF1 Backend")
    print("=" * 60)
    print()
    
    # Test 1: Configuration
    test_cloudinary_config()
    
    # Test 2: Upload depuis URL
    public_id = test_upload_from_url()
    
    if public_id:
        # Test 3: Génération d'URL
        test_get_image_url(public_id)
        
        # Test 4: Suppression
        test_delete_image(public_id)
    
    print("=" * 60)
    print("✅ Tests terminés !")
    print("=" * 60)

if __name__ == "__main__":
    main()
