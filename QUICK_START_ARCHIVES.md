# 🚀 Démarrage Rapide - Système Archives

## En 5 minutes chrono ! ⏱️

### 1️⃣ Démarrer le Backend (Terminal 1)

```bash
cd Backend-BF1
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

✅ **Vérification**: Ouvrez http://localhost:8000/docs

---

### 2️⃣ Créer les Données de Test (Terminal 2)

```bash
cd Backend-BF1
python scripts/create_test_archives.py
```

✅ **Résultat attendu**: "5 archives de test créées avec succès!"

---

### 3️⃣ Tester l'API (Optionnel)

```bash
python scripts/test_archives_api.py
```

✅ **Résultat attendu**: Tous les tests passent

---

### 4️⃣ Démarrer l'Application Mobile (Terminal 3)

```bash
cd Bf1App
npm run android
```

✅ **Résultat attendu**: Application lancée sur l'émulateur/appareil

---

### 5️⃣ Tester dans l'Application

1. 🏠 **Écran d'accueil** → Faites défiler → Section "Archives" 
2. 🎤 **Onglet Interviews** → Faites défiler → Section "Archives"
3. 📂 Cliquez sur "Découvrir" ou "Voir plus"
4. ✨ Testez l'accès premium

---

## 🎯 Endpoints Principaux

| Endpoint | Description |
|----------|-------------|
| `GET /api/v1/archives` | Liste des archives |
| `GET /api/v1/archives/{id}` | Détail d'une archive |
| `GET /api/v1/archives/categories/list` | Catégories |
| `GET /api/v1/archives/{id}/check-access` | Vérifier l'accès |

---

## 🔧 Configuration Rapide

### Backend
- Port: `8000`
- Base URL: `http://localhost:8000/api/v1`
- Docs: `http://localhost:8000/docs`

### Mobile
- Fichier config: `Bf1App/src/config/api.js`
- Android émulateur: `http://10.0.2.2:8000/api/v1`
- iOS simulateur: `http://localhost:8000/api/v1`

---

## 📊 Données de Test Créées

- ✅ 5 archives (4 premium, 1 gratuite)
- ✅ 5 catégories différentes
- ✅ Images et vidéos placeholder
- ✅ Notes et vues simulées

---

## 🐛 Problème Courant

**"Cannot connect to backend"**

Solution rapide:
1. Vérifiez que le backend tourne sur port 8000
2. Vérifiez l'URL dans `api.js`
3. Pour Android émulateur, utilisez `10.0.2.2` au lieu de `localhost`

---

## 📚 Documentation Complète

- 📖 [Guide Complet](./docs/ARCHIVES_SETUP.md)
- 📖 [Documentation API](./docs/ARCHIVES_API.md)

---

## ✅ Checklist de Validation

- [ ] Backend démarré et accessible
- [ ] 5 archives créées dans MongoDB
- [ ] Tests API passent
- [ ] Application mobile lancée
- [ ] Section Archives visible dans HomeScreen
- [ ] Navigation vers ArchiveScreen fonctionne
- [ ] Badge Premium affiché correctement

---

**C'est tout ! Votre système d'archives est opérationnel ! 🎉**
