"""
Script pour tester les endpoints de l'API Archives
"""
import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000/api/v1"
ARCHIVES_URL = f"{BASE_URL}/archives"

# Couleurs pour l'affichage
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"


def print_success(message):
    print(f"{GREEN}✅ {message}{RESET}")


def print_error(message):
    print(f"{RED}❌ {message}{RESET}")


def print_info(message):
    print(f"{BLUE}ℹ️  {message}{RESET}")


def print_warning(message):
    print(f"{YELLOW}⚠️  {message}{RESET}")


def test_get_archives():
    """Test: Récupérer toutes les archives"""
    print_info("Test: GET /archives")
    
    try:
        response = requests.get(ARCHIVES_URL)
        if response.status_code == 200:
            archives = response.json()
            print_success(f"Récupération réussie: {len(archives)} archives trouvées")
            
            if archives:
                print_info(f"Première archive: {archives[0].get('title', 'N/A')}")
                print_info(f"  - Premium: {archives[0].get('is_premium', False)}")
                print_info(f"  - Catégorie: {archives[0].get('category', 'N/A')}")
                print_info(f"  - Vues: {archives[0].get('views', 0)}")
            return True
        else:
            print_error(f"Erreur {response.status_code}: {response.text}")
            return False
    except Exception as e:
        print_error(f"Exception: {str(e)}")
        return False


def test_get_archives_with_filters():
    """Test: Récupérer les archives avec filtres"""
    print_info("Test: GET /archives?category=Politique&limit=5")
    
    try:
        response = requests.get(f"{ARCHIVES_URL}?category=Politique&limit=5")
        if response.status_code == 200:
            archives = response.json()
            print_success(f"Filtrage réussi: {len(archives)} archives trouvées")
            return True
        else:
            print_error(f"Erreur {response.status_code}: {response.text}")
            return False
    except Exception as e:
        print_error(f"Exception: {str(e)}")
        return False


def test_get_categories():
    """Test: Récupérer les catégories"""
    print_info("Test: GET /archives/categories/list")
    
    try:
        response = requests.get(f"{ARCHIVES_URL}/categories/list")
        if response.status_code == 200:
            categories = response.json()
            print_success(f"Catégories récupérées: {', '.join(categories)}")
            return True
        else:
            print_error(f"Erreur {response.status_code}: {response.text}")
            return False
    except Exception as e:
        print_error(f"Exception: {str(e)}")
        return False


def test_get_archive_by_id(archive_id, token=None):
    """Test: Récupérer une archive spécifique"""
    print_info(f"Test: GET /archives/{archive_id}")
    
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    try:
        response = requests.get(f"{ARCHIVES_URL}/{archive_id}", headers=headers)
        if response.status_code == 200:
            archive = response.json()
            print_success(f"Archive récupérée: {archive.get('title', 'N/A')}")
            return True
        elif response.status_code == 401:
            print_warning("Authentification requise")
            return False
        elif response.status_code == 403:
            print_warning("Abonnement premium requis")
            return False
        else:
            print_error(f"Erreur {response.status_code}: {response.text}")
            return False
    except Exception as e:
        print_error(f"Exception: {str(e)}")
        return False


def test_create_archive(token):
    """Test: Créer une archive (admin)"""
    print_info("Test: POST /archives (création)")
    
    archive_data = {
        "title": f"Test Archive {datetime.now().strftime('%Y%m%d%H%M%S')}",
        "guest_name": "Test Guest",
        "guest_role": "Test Role",
        "description": "Archive de test créée automatiquement",
        "duration_minutes": 30,
        "is_premium": True,
        "price": 2.99,
        "category": "Test",
        "tags": ["test", "auto"],
        "archived_date": datetime.utcnow().isoformat(),
        "image": "https://via.placeholder.com/800x450",
        "thumbnail": "https://via.placeholder.com/400x225",
        "video_url": "https://example.com/test.mp4"
    }
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.post(ARCHIVES_URL, json=archive_data, headers=headers)
        if response.status_code == 200:
            archive = response.json()
            print_success(f"Archive créée: {archive.get('title', 'N/A')} (ID: {archive.get('id', 'N/A')})")
            return archive.get('id')
        elif response.status_code == 401:
            print_warning("Authentification admin requise")
            return None
        else:
            print_error(f"Erreur {response.status_code}: {response.text}")
            return None
    except Exception as e:
        print_error(f"Exception: {str(e)}")
        return None


def run_all_tests():
    """Exécuter tous les tests"""
    print("\n" + "="*60)
    print("🧪 TEST DE L'API ARCHIVES")
    print("="*60 + "\n")
    
    results = []
    
    # Test 1: Récupérer toutes les archives
    print("\n" + "-"*60)
    results.append(("GET /archives", test_get_archives()))
    
    # Test 2: Récupérer avec filtres
    print("\n" + "-"*60)
    results.append(("GET /archives (filtres)", test_get_archives_with_filters()))
    
    # Test 3: Récupérer les catégories
    print("\n" + "-"*60)
    results.append(("GET /archives/categories/list", test_get_categories()))
    
    # Test 4: Récupérer une archive spécifique (sans auth)
    print("\n" + "-"*60)
    try:
        response = requests.get(ARCHIVES_URL)
        if response.status_code == 200:
            archives = response.json()
            if archives:
                archive_id = archives[0].get('id')
                results.append(("GET /archives/{id} (sans auth)", test_get_archive_by_id(archive_id)))
    except:
        print_warning("Impossible de tester GET /archives/{id}")
    
    # Résumé
    print("\n" + "="*60)
    print("📊 RÉSUMÉ DES TESTS")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\n{passed}/{total} tests réussis")
    
    if passed == total:
        print_success("Tous les tests sont passés! 🎉")
    else:
        print_warning(f"{total - passed} test(s) échoué(s)")
    
    print("\n" + "="*60 + "\n")


if __name__ == "__main__":
    print_info("Assurez-vous que le backend est démarré sur http://localhost:8000")
    input("Appuyez sur Entrée pour commencer les tests...")
    run_all_tests()
