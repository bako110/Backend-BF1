"""
API pour l'upload de fichiers vers Cloudinary
"""

from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import Optional
from app.utils.file_upload import file_upload_handler

router = APIRouter()

@router.post("/image")
async def upload_image(
    file: UploadFile = File(...),
    folder: Optional[str] = "bf1",
    public_id: Optional[str] = None
):
    """
    Upload une image vers Cloudinary
    
    Args:
        file: Fichier image à uploader
        folder: Dossier Cloudinary (défaut: bf1)
        public_id: ID public personnalisé (optionnel)
    
    Returns:
        URL de l'image et métadonnées
    """
    try:
        # Vérifier le type de fichier
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="Le fichier doit être une image")
        
        print(f"📤 Upload image: {file.filename}")
        
        # Upload vers Cloudinary
        result = await file_upload_handler.upload_image_to_cloudinary(
            file=file,
            folder=folder,
            public_id=public_id
        )
        
        return {
            "success": True,
            "message": "Image uploadée avec succès",
            "data": result
        }
        
    except Exception as e:
        print(f"❌ Erreur upload image: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/video")
async def upload_video(
    file: UploadFile = File(...),
    folder: Optional[str] = "bf1/videos",
    public_id: Optional[str] = None
):
    """
    Upload une vidéo vers Cloudinary
    
    Args:
        file: Fichier vidéo à uploader
        folder: Dossier Cloudinary (défaut: bf1/videos)
        public_id: ID public personnalisé (optionnel)
    
    Returns:
        URL de la vidéo et métadonnées
    """
    try:
        # Vérifier le type de fichier
        if not file.content_type.startswith('video/'):
            raise HTTPException(status_code=400, detail="Le fichier doit être une vidéo")
        
        print(f"📤 Upload vidéo: {file.filename}")
        
        # Upload vers Cloudinary
        result = await file_upload_handler.upload_video_to_cloudinary(
            file=file,
            folder=folder,
            public_id=public_id
        )
        
        return {
            "success": True,
            "message": "Vidéo uploadée avec succès",
            "data": result
        }
        
    except Exception as e:
        print(f"❌ Erreur upload vidéo: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/from-url")
async def upload_from_url(
    url: str,
    folder: Optional[str] = "bf1",
    public_id: Optional[str] = None
):
    """
    Upload une image depuis une URL vers Cloudinary
    
    Args:
        url: URL de l'image
        folder: Dossier Cloudinary (défaut: bf1)
        public_id: ID public personnalisé (optionnel)
    
    Returns:
        URL de l'image et métadonnées
    """
    try:
        print(f"📤 Upload depuis URL: {url}")
        
        # Upload vers Cloudinary
        result = file_upload_handler.upload_from_url(
            url=url,
            folder=folder,
            public_id=public_id
        )
        
        return {
            "success": True,
            "message": "Image uploadée depuis URL avec succès",
            "data": result
        }
        
    except Exception as e:
        print(f"❌ Erreur upload depuis URL: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{public_id:path}")
async def delete_image(public_id: str):
    """
    Supprimer une image de Cloudinary
    
    Args:
        public_id: ID public de l'image à supprimer
    
    Returns:
        Confirmation de suppression
    """
    try:
        print(f"🗑️ Suppression image: {public_id}")
        
        success = file_upload_handler.delete_image(public_id)
        
        if success:
            return {
                "success": True,
                "message": "Image supprimée avec succès"
            }
        else:
            raise HTTPException(status_code=404, detail="Image non trouvée")
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Erreur suppression image: {e}")
        raise HTTPException(status_code=500, detail=str(e))
