# 🌱 Script de Peuplement de la Base de Données BF1 TV

## Description

Ce script peuple automatiquement la base de données MongoDB avec des données de test pour l'application BF1 TV.

## Données Créées

### 👥 Utilisateurs (3)
1. **Admin**
   - Email: `admin@bf1tv.com`
   - Password: `admin123`
   - Rôle: Administrateur
   - Premium: Oui

2. **User1**
   - Email: `user1@bf1tv.com`
   - Password: `user123`
   - Rôle: Utilisateur
   - Premium: Non

3. **Premium User**
   - Email: `premium@bf1tv.com`
   - Password: `premium123`
   - Rôle: Utilisateur
   - Premium: Oui

### 📺 Émissions (5)
- Journal Télévisé 19h30 (EN DIRECT)
- Journal Télévisé 13h30 (Replay)
- Sport en Direct (EN DIRECT)
- Culture & Vous (Programmée)
- Divertissement du Soir (Programmée)

### 🎬 Films (5)
- Le Dernier Voyage (Gratuit)
- Amour à Paris (Premium)
- Mission Impossible: Retour (Premium)
- Comédie Familiale (Gratuit)
- Documentaire Nature (Gratuit)

### 📰 Actualités (5)
- Nouvelle loi sur l'environnement (EN DIRECT)
- Victoire historique en Coupe du Monde
- Exposition d'art contemporain au Louvre
- Nouvelle technologie révolutionnaire
- Sommet international sur le climat (EN DIRECT)

## 🚀 Utilisation

### Prérequis
- MongoDB en cours d'exécution
- Variables d'environnement configurées dans `.env`

### Exécution

```bash
# Depuis le dossier Backend
python seed.py
```

### Résultat Attendu

```
============================================================
🌱 SCRIPT DE PEUPLEMENT BF1 TV
============================================================
🔌 Connexion à MongoDB: mongodb://localhost:27017
📦 Base de données: bf1tv

✅ Connexion à la base de données établie

🌱 Début du peuplement de la base de données BF1 TV...

👥 Création des utilisateurs...
✅ Utilisateur créé: admin
✅ Utilisateur créé: user1
✅ Utilisateur créé: premium_user
✅ 3 utilisateurs créés/vérifiés

📺 Création des émissions...
✅ Émission créée: Journal Télévisé 19h30
✅ Émission créée: Journal Télévisé 13h30
✅ Émission créée: Sport en Direct
✅ Émission créée: Culture & Vous
✅ Émission créée: Divertissement du Soir
✅ 5 émissions créées/vérifiées

🎬 Création des films...
✅ Film créé: Le Dernier Voyage
✅ Film créé: Amour à Paris
✅ Film créé: Mission Impossible: Retour
✅ Film créé: Comédie Familiale
✅ Film créé: Documentaire Nature
✅ 5 films créés/vérifiés

📰 Création des actualités...
✅ Actualité créée: Nouvelle loi sur l'environnement adoptée
✅ Actualité créée: Victoire historique en Coupe du Monde
✅ Actualité créée: Exposition d'art contemporain au Louvre
✅ Actualité créée: Nouvelle technologie révolutionnaire
✅ Actualité créée: Sommet international sur le climat
✅ 5 actualités créées/vérifiées

🎉 Peuplement terminé avec succès!

📊 Résumé:
   - Utilisateurs: 3
   - Émissions: 5
   - Films: 5
   - Actualités: 5
============================================================
```

## ⚠️ Notes Importantes

1. **Exécution Multiple** : Le script peut être exécuté plusieurs fois sans créer de doublons (il vérifie l'existence avant d'insérer)

2. **Images** : Les URLs d'images utilisent Unsplash (placeholders). Remplacez-les par vos vraies images.

3. **Vidéos** : Les URLs de streaming sont des exemples. Configurez vos vrais flux vidéo.

4. **Horaires** : Les émissions en direct utilisent l'heure actuelle. Ajustez selon vos besoins.

## 🔧 Personnalisation

Pour ajouter plus de données, modifiez le fichier `app/utils/seed_data.py` :

```python
# Ajouter plus d'émissions
shows_data.append({
    "title": "Votre Émission",
    "description": "Description",
    # ... autres champs
})
```

## 🧹 Nettoyage

Pour supprimer toutes les données de test :

```bash
# Connexion à MongoDB
mongosh

# Utiliser la base de données
use bf1tv

# Supprimer toutes les collections
db.users.deleteMany({})
db.shows.deleteMany({})
db.movies.deleteMany({})
db.news.deleteMany({})
```

## 📝 Logs

Le script affiche des logs détaillés :
- ✅ Création réussie
- ⚠️  Élément existe déjà
- ❌ Erreur

## 🎯 Utilisation dans l'Application Mobile

Après l'exécution du script, l'application React Native affichera :
- 2 émissions en direct sur l'écran d'accueil
- 5 films dans la section Films
- 5 actualités dans la section News
- Programme de la semaine avec les émissions programmées

Vous pouvez vous connecter avec les comptes de test pour tester les fonctionnalités premium et admin.
