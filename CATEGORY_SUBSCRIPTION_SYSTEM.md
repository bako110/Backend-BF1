# Système de Catégories d'Abonnement

## Vue d'ensemble

Le système d'abonnement a été modernisé pour utiliser une hiérarchie de catégories au lieu d'un simple statut boolean "premium". Cela permet un contrôle d'accès granulaire au contenu.

## Hiérarchie des Catégories

```
Gratuit (None) < Basic < Standard < Premium
```

### Règles d'accès :
- **Gratuit** : Accès uniquement au contenu gratuit (required_subscription_category = null)
- **Basic** : Accès au contenu Basic + Gratuit
- **Standard** : Accès au contenu Standard + Basic + Gratuit  
- **Premium** : Accès à tout le contenu (Premium + Standard + Basic + Gratuit)

## Modifications Backend

### 1. Modèles

#### User (app/models/user.py)
```python
class User:
    is_premium: bool = False  # Conservé pour compatibilité
    subscription_category: Optional[str] = None  # Nouvelle: "basic", "standard", "premium"
```

#### Subscription (app/models/subscription.py)
```python
class Subscription:
    user_id: str
    plan_id: Optional[str]
    category: Optional[str]  # Nouvelle: stocke la catégorie du plan
    is_active: bool
    end_date: Optional[datetime]
```

#### Archive/Movie/Series (app/models/)
```python
class Content:
    required_subscription_category: Optional[str] = None  # null, "basic", "standard", "premium"
    is_premium: bool = False  # Conservé pour compatibilité
```

### 2. Utilitaires (app/utils/subscription_utils.py)

#### can_access_content(user_category, required_category) -> bool
Vérifie si un utilisateur avec une catégorie donnée peut accéder à un contenu.

**Exemples:**
```python
can_access_content('premium', 'basic')    # True (premium peut tout)
can_access_content('basic', 'premium')    # False (basic ne peut pas premium)
can_access_content('standard', 'basic')   # True (standard peut basic)
can_access_content(None, 'basic')         # False (gratuit ne peut pas basic)
can_access_content('basic', None)         # True (tout le monde peut gratuit)
```

#### get_highest_active_category(categories: list) -> str
Retourne la catégorie la plus élevée parmi une liste.

### 3. Services (app/services/subscription_service.py)

#### get_user_subscription_category(user_id) -> Optional[str]
Récupère la catégorie d'abonnement active de l'utilisateur.
Si plusieurs abonnements actifs, retourne la catégorie la plus élevée.

#### sync_user_premium_status(user_id) -> bool
Synchronise `is_premium` ET `subscription_category` de l'utilisateur.
Appelé automatiquement lors de:
- Création d'un abonnement
- Annulation d'un abonnement
- Expiration d'un abonnement (CRON horaire)

#### create_subscription(data) -> Subscription
Crée un abonnement et:
1. Récupère la catégorie du plan
2. Stocke la catégorie dans l'abonnement
3. Synchronise l'utilisateur

### 4. API (app/api/archives.py)

#### GET /archives/{archive_id}/check-access
Endpoint mis à jour pour vérifier l'accès selon la hiérarchie.

**Réponse:**
```json
{
  "has_access": true,
  "required_category": "basic",
  "required_category_display": "Basic",
  "user_category": "premium",
  "user_category_display": "Premium",
  "has_subscription_access": true,
  "has_purchased": false,
  "is_premium": false,
  "price": 0
}
```

## Migration

### Script: update_subscription_categories.py

Exécuter pour mettre à jour les abonnements existants:
```bash
python update_subscription_categories.py
```

**Actions:**
1. Récupère tous les abonnements
2. Pour chaque abonnement, récupère la catégorie de son plan
3. Met à jour le champ `category` de l'abonnement
4. Synchronise tous les utilisateurs avec leurs catégories actives

## Utilisation Admin

### Création de Contenu

Lors de la création d'une archive/film/série dans l'admin:
1. Sélectionner `required_subscription_category`:
   - **Gratuit** : Accessible à tous
   - **Basic** : Nécessite abonnement Basic minimum
   - **Standard** : Nécessite abonnement Standard minimum
   - **Premium** : Nécessite abonnement Premium

### Plans d'Abonnement

Les plans d'abonnement ont déjà le champ `category` défini:
```json
{
  "name": "Premium",
  "category": "premium",
  "duration_months": 1,
  "price_cents": 15000
}
```

## Utilisation Mobile

### Badges d'Abonnement

Les écrans mobiles affichent des badges de couleur pour indiquer la catégorie requise:
- 🟢 **Gratuit** : `#4CAF50` (vert)
- 🔵 **Basic** : `#2196F3` (bleu)
- 🟣 **Standard** : `#9C27B0` (violet)
- 🟠 **Premium** : `#FF6F00` (orange foncé)

### Vérification d'Accès

Lors du clic sur un contenu, l'app vérifie:
```javascript
const response = await api.get(`/archives/${id}/check-access`);
if (response.data.has_access) {
  // Ouvrir le lecteur
} else {
  // Afficher message avec catégorie requise
  Alert.alert(
    'Abonnement requis',
    `Ce contenu nécessite un abonnement ${response.data.required_category_display}`
  );
}
```

## Tests

### Scénarios à Tester

1. **Utilisateur Gratuit**
   - ✅ Peut accéder au contenu gratuit
   - ❌ Ne peut pas accéder au contenu Basic/Standard/Premium

2. **Utilisateur Basic**
   - ✅ Peut accéder au contenu gratuit et Basic
   - ❌ Ne peut pas accéder au contenu Standard/Premium

3. **Utilisateur Standard**
   - ✅ Peut accéder au contenu gratuit, Basic et Standard
   - ❌ Ne peut pas accéder au contenu Premium

4. **Utilisateur Premium**
   - ✅ Peut accéder à TOUT le contenu

5. **Expiration d'Abonnement**
   - Utilisateur passe de Premium à Gratuit
   - Perd l'accès au contenu payant

### Création de Données de Test

```python
# Créer des plans via l'admin
# Basic: 2500 XOF/mois
# Standard: 5000 XOF/mois  
# Premium: 15000 XOF/mois

# Créer du contenu avec différentes catégories
# Archive 1: required_subscription_category = null (Gratuit)
# Archive 2: required_subscription_category = "basic"
# Archive 3: required_subscription_category = "standard"
# Archive 4: required_subscription_category = "premium"

# Créer des utilisateurs de test avec différents abonnements
# User 1: Pas d'abonnement (gratuit)
# User 2: Abonnement Basic
# User 3: Abonnement Standard
# User 4: Abonnement Premium
```

## Compatibilité

Le champ `is_premium` est conservé pour la compatibilité:
- Tout utilisateur avec une catégorie (basic/standard/premium) a `is_premium = True`
- Utilisateurs sans abonnement ont `is_premium = False`

Cela évite de casser les vérifications existantes dans l'app mobile qui utilisent encore `is_premium`.

## CRON Automatique

Le système exécute automatiquement toutes les heures:
```python
deactivate_expired_subscriptions()
```

Ce job:
1. Désactive les abonnements expirés
2. Synchronise les utilisateurs affectés
3. Met à jour `is_premium` et `subscription_category`

## Dépannage

### Utilisateur ne voit pas le contenu attendu

1. Vérifier l'abonnement actif:
```python
await get_user_subscription_category(user_id)
```

2. Synchroniser manuellement:
```python
await sync_user_premium_status(user_id)
```

3. Vérifier la catégorie du contenu dans l'admin

### Badge ne s'affiche pas sur mobile

1. Vérifier que l'API retourne `required_subscription_category`
2. Vérifier que `getSubscriptionBadge()` existe dans l'écran
3. Vérifier les logs réseau pour voir la réponse API

## Avantages du Nouveau Système

1. **Flexibilité** : Plusieurs niveaux d'abonnement au lieu de tout-ou-rien
2. **Évolutivité** : Facile d'ajouter de nouveaux niveaux (VIP, Enterprise, etc.)
3. **Monétisation** : Encourage les upgrades (Basic → Standard → Premium)
4. **Clarté** : Les badges montrent visuellement ce qui nécessite quel niveau
5. **Granularité** : Contrôle fin sur quel contenu nécessite quel niveau
