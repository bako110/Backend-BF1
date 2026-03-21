# API Archives - Documentation

## Vue d'ensemble

L'API Archives permet de gérer et d'accéder aux archives d'interviews premium de l'application BF1.

**Base URL**: `/api/v1/archives`

---

## Endpoints

### 1. Récupérer toutes les archives

```http
GET /api/v1/archives
```

**Paramètres de requête**:
- `skip` (int, optionnel): Nombre d'éléments à sauter (pagination) - défaut: 0
- `limit` (int, optionnel): Nombre max d'éléments à retourner - défaut: 50, max: 100
- `category` (string, optionnel): Filtrer par catégorie
- `is_active` (bool, optionnel): Filtrer par statut actif - défaut: true

**Réponse**: `200 OK`
```json
[
  {
    "id": "507f1f77bcf86cd799439011",
    "title": "Interview exclusive avec Jean Dupont",
    "guest_name": "Jean Dupont",
    "guest_role": "Ministre de l'Économie",
    "description": "Une interview approfondie...",
    "duration_minutes": 45,
    "is_premium": true,
    "price": 4.99,
    "category": "Politique",
    "tags": ["économie", "politique"],
    "views": 1250,
    "rating": 4.5,
    "image": "https://...",
    "thumbnail": "https://...",
    "video_url": "https://...",
    "archived_date": "2024-01-15T10:00:00Z",
    "created_at": "2024-01-10T10:00:00Z",
    "is_active": true
  }
]
```

---

### 2. Récupérer une archive spécifique

```http
GET /api/v1/archives/{archive_id}
```

**Authentification**: Requise (Bearer Token)

**Réponse**: `200 OK` ou `403 Forbidden` (si premium requis)

---

### 3. Vérifier l'accès à une archive

```http
GET /api/v1/archives/{archive_id}/check-access
```

**Authentification**: Requise (Bearer Token)

**Réponse**: `200 OK`
```json
{
  "has_access": true,
  "is_premium": true,
  "user_is_premium": true,
  "price": 4.99
}
```

---

### 4. Récupérer les catégories

```http
GET /api/v1/archives/categories/list
```

**Réponse**: `200 OK`
```json
["Politique", "Éducation", "Santé", "Technologie", "Culture"]
```

---

### 5. Noter une archive

```http
POST /api/v1/archives/{archive_id}/rate?rating=4.5
```

**Authentification**: Requise (Bearer Token)

**Paramètres de requête**:
- `rating` (float, requis): Note entre 0 et 5

**Réponse**: `200 OK`
```json
{
  "message": "Note enregistrée",
  "new_rating": 4.5
}
```

---

### 6. Créer une archive (Admin)

```http
POST /api/v1/archives
```

**Authentification**: Requise (Admin uniquement)

**Corps de la requête**:
```json
{
  "title": "Nouvelle interview",
  "guest_name": "Nom de l'invité",
  "guest_role": "Rôle de l'invité",
  "description": "Description détaillée",
  "duration_minutes": 45,
  "is_premium": true,
  "price": 4.99,
  "category": "Politique",
  "tags": ["tag1", "tag2"],
  "archived_date": "2024-02-09T10:00:00Z",
  "image": "https://...",
  "thumbnail": "https://...",
  "video_url": "https://..."
}
```

**Réponse**: `200 OK` (Archive créée)

---

### 7. Mettre à jour une archive (Admin)

```http
PATCH /api/v1/archives/{archive_id}
```

**Authentification**: Requise (Admin uniquement)

**Corps de la requête**: Champs à mettre à jour (tous optionnels)

---

### 8. Supprimer une archive (Admin)

```http
DELETE /api/v1/archives/{archive_id}
```

**Authentification**: Requise (Admin uniquement)

**Réponse**: `200 OK`
```json
{
  "message": "Archive supprimée avec succès"
}
```

---

## Modèle de données

### Archive

| Champ | Type | Description |
|-------|------|-------------|
| id | string | Identifiant unique |
| title | string | Titre de l'archive |
| guest_name | string | Nom de l'invité |
| guest_role | string | Rôle/fonction de l'invité |
| description | string | Description détaillée |
| duration_minutes | int | Durée en minutes |
| is_premium | bool | Contenu premium (payant) |
| price | float | Prix si achat individuel |
| category | string | Catégorie |
| tags | array[string] | Tags |
| views | int | Nombre de vues |
| rating | float | Note (0-5) |
| image | string (URL) | Image principale |
| thumbnail | string (URL) | Miniature |
| video_url | string (URL) | URL de la vidéo |
| archived_date | datetime | Date d'archivage |
| original_publish_date | datetime | Date de publication originale |
| created_at | datetime | Date de création |
| updated_at | datetime | Date de mise à jour |
| is_active | bool | Archive active |

---

## Codes d'erreur

| Code | Description |
|------|-------------|
| 200 | Succès |
| 401 | Non authentifié |
| 403 | Accès refusé (premium requis) |
| 404 | Archive non trouvée |
| 422 | Données invalides |

---

## Exemples d'utilisation

### JavaScript (Fetch)

```javascript
// Récupérer toutes les archives
const response = await fetch('http://localhost:8000/api/v1/archives');
const archives = await response.json();

// Récupérer une archive avec authentification
const response = await fetch(`http://localhost:8000/api/v1/archives/${archiveId}`, {
  headers: {
    'Authorization': `Bearer ${token}`
  }
});
const archive = await response.json();
```

### Python (Requests)

```python
import requests

# Récupérer toutes les archives
response = requests.get('http://localhost:8000/api/v1/archives')
archives = response.json()

# Créer une archive (admin)
headers = {'Authorization': f'Bearer {admin_token}'}
data = {
    'title': 'Nouvelle archive',
    'guest_name': 'Jean Dupont',
    # ... autres champs
}
response = requests.post('http://localhost:8000/api/v1/archives', json=data, headers=headers)
```

---

## Scripts utiles

### Créer des données de test

```bash
cd Backend-BF1
python scripts/create_test_archives.py
```

### Tester l'API

```bash
cd Backend-BF1
python scripts/test_archives_api.py
```

---

## Notes importantes

1. **Authentification**: Les endpoints de lecture nécessitent une authentification utilisateur
2. **Premium**: L'accès aux archives premium nécessite un abonnement actif
3. **Admin**: Les opérations de création/modification/suppression nécessitent des droits admin
4. **Pagination**: Utilisez `skip` et `limit` pour paginer les résultats
5. **Filtrage**: Utilisez `category` pour filtrer par catégorie

---

## Support

Pour toute question ou problème, contactez l'équipe de développement.
