# Guide de Configuration - Système Archives

## 📋 Vue d'ensemble

Ce guide vous accompagne dans la configuration complète du système d'archives premium pour l'application BF1.

---

## 🎯 Prérequis

- ✅ MongoDB en cours d'exécution
- ✅ Backend FastAPI configuré
- ✅ Application mobile React Native configurée
- ✅ Python 3.8+ installé
- ✅ Node.js et npm installés

---

## 🚀 Étape 1: Démarrer le Backend

### Windows

```bash
cd Backend-BF1
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Linux/Mac

```bash
cd Backend-BF1
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Vérification**: Ouvrez http://localhost:8000/docs pour voir la documentation Swagger

---

## 🗄️ Étape 2: Créer des Archives de Test

### Méthode 1: Script Python (Recommandé)

```bash
cd Backend-BF1
python scripts/create_test_archives.py
```

Ce script créera automatiquement 5 archives de test avec différentes catégories :
- 📰 Politique
- 📚 Éducation
- 🏥 Santé
- 💻 Technologie (gratuite)
- 🎨 Culture

### Méthode 2: Via l'API (Manuel)

```bash
curl -X POST "http://localhost:8000/api/v1/archives" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Mon Archive Test",
    "guest_name": "Jean Dupont",
    "guest_role": "Expert",
    "description": "Description de l'archive",
    "duration_minutes": 45,
    "is_premium": true,
    "price": 4.99,
    "category": "Test",
    "tags": ["test"],
    "archived_date": "2024-02-09T10:00:00Z",
    "image": "https://via.placeholder.com/800x450",
    "thumbnail": "https://via.placeholder.com/400x225",
    "video_url": "https://example.com/video.mp4"
  }'
```

---

## 🧪 Étape 3: Tester l'API

### Test Automatique

```bash
cd Backend-BF1
python scripts/test_archives_api.py
```

### Tests Manuels

#### 1. Récupérer toutes les archives

```bash
curl http://localhost:8000/api/v1/archives
```

#### 2. Récupérer les catégories

```bash
curl http://localhost:8000/api/v1/archives/categories/list
```

#### 3. Filtrer par catégorie

```bash
curl "http://localhost:8000/api/v1/archives?category=Politique&limit=10"
```

---

## 📱 Étape 4: Démarrer l'Application Mobile

### Android

```bash
cd Bf1App
npm run android
```

### iOS

```bash
cd Bf1App
npm run ios
```

---

## 🔧 Étape 5: Configuration de l'API Mobile

Vérifiez que le fichier `Bf1App/src/config/api.js` pointe vers le bon serveur :

```javascript
const IS_PRODUCTION = false; // false pour développement local

const API_BASE_URL = IS_PRODUCTION 
  ? 'https://votre-api-production.com/api/v1'
  : 'http://10.0.2.2:8000/api/v1'; // Pour émulateur Android
  // : 'http://localhost:8000/api/v1'; // Pour iOS ou navigateur
```

---

## 🎨 Étape 6: Navigation dans l'Application

### Accéder aux Archives

1. **Depuis l'écran d'accueil** :
   - Faites défiler jusqu'à la section "Archives"
   - Cliquez sur "Voir plus" ou "Découvrir"

2. **Depuis l'écran Interviews** :
   - Allez dans l'onglet "Interviews"
   - Faites défiler jusqu'en bas
   - Section "Archives" avec badge Premium

3. **Navigation directe** :
   - L'écran `ArchiveScreen` est accessible via le stack de navigation

---

## 🔐 Gestion des Accès Premium

### Vérifier le Statut Premium d'un Utilisateur

```javascript
// Dans l'application mobile
import { useAuth } from '../contexts/authContext';

const { user } = useAuth();
const isPremium = user?.is_premium || false;
```

### Tester avec un Utilisateur Premium

1. Créez un utilisateur de test
2. Mettez à jour son statut premium dans MongoDB :

```javascript
db.users.updateOne(
  { email: "test@example.com" },
  { $set: { is_premium: true, premium_expires_at: new Date("2025-12-31") } }
)
```

---

## 📊 Vérification du Système

### Checklist Backend ✅

- [ ] Backend démarré sur port 8000
- [ ] Documentation Swagger accessible
- [ ] Modèle Archive enregistré dans Beanie
- [ ] Router archives inclus dans l'API
- [ ] Archives de test créées
- [ ] Endpoints testés et fonctionnels

### Checklist Mobile ✅

- [ ] Application mobile démarrée
- [ ] Service archiveService configuré
- [ ] Écran ArchiveScreen créé
- [ ] Navigation configurée
- [ ] Section Archives visible dans HomeScreen
- [ ] Section Archives visible dans InterviewsScreen
- [ ] Gestion premium fonctionnelle

---

## 🐛 Dépannage

### Problème: "Archive non trouvée"

**Solution**: Vérifiez que les archives sont bien créées dans MongoDB
```bash
python scripts/create_test_archives.py
```

### Problème: "401 Unauthorized"

**Solution**: Vérifiez que l'utilisateur est connecté et que le token est valide

### Problème: "403 Forbidden - Premium requis"

**Solution**: L'utilisateur n'a pas d'abonnement premium
- Testez avec une archive gratuite (is_premium: false)
- Ou activez le premium pour l'utilisateur de test

### Problème: API non accessible depuis le mobile

**Solution**: Vérifiez l'URL dans `api.js`
- Android émulateur: `http://10.0.2.2:8000/api/v1`
- iOS simulateur: `http://localhost:8000/api/v1`
- Appareil physique: `http://VOTRE_IP_LOCAL:8000/api/v1`

---

## 📈 Monitoring et Statistiques

### Vérifier les Archives dans MongoDB

```javascript
// Connexion MongoDB
use bf1_database

// Compter les archives
db.archives.countDocuments()

// Voir toutes les archives
db.archives.find().pretty()

// Archives premium
db.archives.find({ is_premium: true }).count()

// Archives par catégorie
db.archives.aggregate([
  { $group: { _id: "$category", count: { $sum: 1 } } }
])
```

---

## 🔄 Mise à Jour et Maintenance

### Ajouter une Nouvelle Archive

Via l'API admin ou directement dans MongoDB

### Modifier une Archive

```bash
curl -X PATCH "http://localhost:8000/api/v1/archives/{archive_id}" \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"price": 3.99, "is_active": true}'
```

### Supprimer une Archive

```bash
curl -X DELETE "http://localhost:8000/api/v1/archives/{archive_id}" \
  -H "Authorization: Bearer ADMIN_TOKEN"
```

---

## 📚 Ressources Supplémentaires

- **Documentation API**: [ARCHIVES_API.md](./ARCHIVES_API.md)
- **Swagger UI**: http://localhost:8000/docs
- **Code Backend**: `Backend-BF1/app/api/archives.py`
- **Code Mobile**: `Bf1App/src/screens/ArchiveScreen.js`

---

## ✅ Validation Finale

Exécutez ce script pour valider l'installation complète :

```bash
cd Backend-BF1
scripts\setup_archives.bat
```

Ou manuellement :
1. ✅ Backend démarré
2. ✅ Archives créées
3. ✅ Tests API passés
4. ✅ Application mobile lancée
5. ✅ Navigation vers Archives fonctionnelle
6. ✅ Gestion premium testée

---

## 🎉 Félicitations !

Votre système d'archives premium est maintenant complètement opérationnel !

Pour toute question ou problème, consultez la documentation ou contactez l'équipe de développement.
