# BF1 API Documentation

## Shows (Émissions)

- **GET /shows** : Liste toutes les émissions
- **GET /shows/category/{category}** : Filtrer par catégorie (ex: info, sport, culture)
- **GET /shows/edition/{edition}** : Filtrer par édition (ex: Journal 13H30, 19H30)
- **GET /shows/host/{host}** : Filtrer par animateur
- **GET /shows/live** : Liste des émissions en direct
- **GET /shows/replay** : Liste des émissions en replay

### Champs du modèle Show
- title : Titre
- description : Description
- host : Animateur
- duration : Durée
- category : Catégorie
- edition : Édition (Journal 13H30, 19H30...)
- start_time / end_time : Horaire
- image_url : Image
- is_live : En direct ?
- is_featured : Mise en avant
- tags : Tags
- replay_url : URL du replay

---

## News (Journaux)

- **GET /news** : Liste tous les journaux
- **GET /news/edition/{edition}** : Filtrer par édition (13H30, 19H30...)
- **GET /news/live** : Liste des journaux en direct

### Champs du modèle News
- title : Titre
- content : Contenu
- image_url : Image
- published_at : Date de publication
- author : Auteur
- edition : Édition (13H30, 19H30...)
- is_live : En direct ?

---

## Utilisation mobile
- Filtrez par catégorie, édition, animateur, live/replay pour retrouver rapidement ce qui passe sur BF1.
- Accédez au live ou au replay directement via les routes dédiées.
- Les endpoints sont conçus pour une intégration claire et rapide sur mobile.

---

## Exemples de requêtes
- **/shows/category/info** : Toutes les émissions d’info
- **/shows/edition/13H30** : Toutes les émissions du journal de 13H30
- **/shows/live** : Toutes les émissions en direct
- **/news/edition/19H30** : Tous les journaux de 19H30
- **/news/live** : Tous les journaux en direct

---

Pour toute personnalisation ou ajout de filtre, demande simplement !
