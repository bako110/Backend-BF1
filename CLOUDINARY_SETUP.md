# Configuration Cloudinary pour BF1 Backend

## 📋 Informations de configuration

Vos credentials Cloudinary sont déjà configurés :

```env
CLOUDINARY_CLOUD_NAME=dgw62ulgb
CLOUDINARY_API_KEY=564629531797987
CLOUDINARY_API_SECRET=bwIGyXjIG8aQC0U6oV6ycHNhR90
```

## 🚀 Utilisation

### 1. Upload d'une image via API

```bash
# Upload d'un fichier image
curl -X POST "http://localhost:8000/api/v1/upload/image" \
  -F "file=@/path/to/image.jpg" \
  -F "folder=bf1/news" \
  -F "public_id=mon-image"

# Réponse
{
  "success": true,
  "message": "Image uploadée avec succès",
  "data": {
    "url": "https://res.cloudinary.com/dgw62ulgb/image/upload/v1234567890/bf1/news/mon-image.jpg",
    "public_id": "bf1/news/mon-image",
    "width": 1920,
    "height": 1080,
    "format": "jpg"
  }
}
```

### 2. Upload depuis une URL

```bash
curl -X POST "http://localhost:8000/api/v1/upload/from-url" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com/image.jpg",
    "folder": "bf1/programs",
    "public_id": "program-123"
  }'
```

### 3. Upload d'une vidéo

```bash
curl -X POST "http://localhost:8000/api/v1/upload/video" \
  -F "file=@/path/to/video.mp4" \
  -F "folder=bf1/videos"
```

### 4. Supprimer une image

```bash
curl -X DELETE "http://localhost:8000/api/v1/upload/bf1/news/mon-image"
```

## 💻 Utilisation dans le code Python

### Upload d'une image

```python
from app.services.cloudinary_service import cloudinary_service

# Upload depuis un fichier local
result = cloudinary_service.upload_image(
    file_path="/path/to/image.jpg",
    folder="bf1/news",
    public_id="breaking-news-123"
)

print(f"URL de l'image: {result['url']}")
```

### Upload depuis une URL

```python
result = cloudinary_service.upload_from_url(
    url="https://example.com/image.jpg",
    folder="bf1/programs"
)
```

### Supprimer une image

```python
success = cloudinary_service.delete_image("bf1/news/mon-image")
```

## 📁 Structure des dossiers Cloudinary

Organisation recommandée :

```
bf1/
├── news/           # Images d'actualités
├── programs/       # Images de programmes
├── shows/          # Images d'émissions
├── movies/         # Images de films
├── interviews/     # Images d'interviews
├── archives/       # Images d'archives
└── videos/         # Vidéos
```

## 🔧 Intégration dans les routes existantes

### Exemple : Modifier une route pour utiliser Cloudinary

```python
from fastapi import APIRouter, UploadFile, File
from app.utils.file_upload import file_upload_handler

@router.post("/news")
async def create_news(
    title: str,
    description: str,
    image: UploadFile = File(...)
):
    # Upload l'image vers Cloudinary
    image_data = await file_upload_handler.upload_image_to_cloudinary(
        file=image,
        folder="bf1/news"
    )
    
    # Créer l'actualité avec l'URL Cloudinary
    news = {
        "title": title,
        "description": description,
        "image_url": image_data['url'],
        "image_public_id": image_data['public_id']
    }
    
    # Sauvegarder dans la base de données
    # ...
    
    return news
```

## ✅ Avantages de Cloudinary

1. **Stockage cloud** - Plus besoin de stocker les fichiers localement
2. **URLs permanentes** - Les images restent accessibles même après redéploiement
3. **Optimisation automatique** - Compression et format adaptatif
4. **CDN intégré** - Chargement rapide partout dans le monde
5. **Transformations** - Redimensionnement, recadrage, etc.

## 🔗 Transformations d'images

Vous pouvez transformer les images à la volée :

```python
from app.services.cloudinary_service import cloudinary_service

# Obtenir une version redimensionnée
url = cloudinary_service.get_image_url(
    public_id="bf1/news/mon-image",
    transformation={
        "width": 800,
        "height": 600,
        "crop": "fill",
        "quality": "auto"
    }
)
```

## 📊 Limites du plan gratuit

- **Stockage** : 25 GB
- **Bande passante** : 25 GB/mois
- **Transformations** : 25 000/mois

## 🆘 Support

En cas de problème :
1. Vérifiez que les credentials sont corrects dans `.env`
2. Vérifiez que `cloudinary` est installé : `pip install cloudinary`
3. Consultez les logs pour les erreurs détaillées
