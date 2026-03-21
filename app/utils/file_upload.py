"""
Utilitaire pour gérer l'upload de fichiers avec Cloudinary
"""

import os
import uuid
from fastapi import UploadFile
from typing import Optional, Dict, Any
from app.services.cloudinary_service import cloudinary_service

class FileUploadHandler:
    def __init__(self):
        self.temp_dir = "temp_uploads"
        os.makedirs(self.temp_dir, exist_ok=True)
    
    async def upload_image_to_cloudinary(
        self, 
        file: UploadFile, 
        folder: str = "bf1",
        public_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Upload une image vers Cloudinary
        
        Args:
            file: Fichier uploadé via FastAPI
            folder: Dossier Cloudinary
            public_id: ID public personnalisé (optionnel)
        
        Returns:
            Dict contenant l'URL et les métadonnées
        """
        temp_file_path = None
        
        try:
            # Générer un nom de fichier temporaire unique
            file_extension = os.path.splitext(file.filename)[1]
            temp_filename = f"{uuid.uuid4()}{file_extension}"
            temp_file_path = os.path.join(self.temp_dir, temp_filename)
            
            # Sauvegarder temporairement le fichier
            with open(temp_file_path, "wb") as buffer:
                content = await file.read()
                buffer.write(content)
            
            print(f"📁 Fichier temporaire créé: {temp_file_path}")
            
            # Upload vers Cloudinary
            result = cloudinary_service.upload_image(
                file_path=temp_file_path,
                folder=folder,
                public_id=public_id
            )
            
            return result
            
        except Exception as e:
            print(f"❌ Erreur upload fichier: {e}")
            raise e
            
        finally:
            # Nettoyer le fichier temporaire
            if temp_file_path and os.path.exists(temp_file_path):
                try:
                    os.remove(temp_file_path)
                    print(f"🗑️ Fichier temporaire supprimé: {temp_file_path}")
                except Exception as e:
                    print(f"⚠️ Erreur suppression fichier temporaire: {e}")
    
    async def upload_video_to_cloudinary(
        self, 
        file: UploadFile, 
        folder: str = "bf1/videos",
        public_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Upload une vidéo vers Cloudinary
        
        Args:
            file: Fichier uploadé via FastAPI
            folder: Dossier Cloudinary
            public_id: ID public personnalisé (optionnel)
        
        Returns:
            Dict contenant l'URL et les métadonnées
        """
        temp_file_path = None
        
        try:
            # Générer un nom de fichier temporaire unique
            file_extension = os.path.splitext(file.filename)[1]
            temp_filename = f"{uuid.uuid4()}{file_extension}"
            temp_file_path = os.path.join(self.temp_dir, temp_filename)
            
            # Sauvegarder temporairement le fichier
            with open(temp_file_path, "wb") as buffer:
                content = await file.read()
                buffer.write(content)
            
            print(f"📁 Fichier vidéo temporaire créé: {temp_file_path}")
            
            # Upload vers Cloudinary
            result = cloudinary_service.upload_video(
                file_path=temp_file_path,
                folder=folder,
                public_id=public_id
            )
            
            return result
            
        except Exception as e:
            print(f"❌ Erreur upload vidéo: {e}")
            raise e
            
        finally:
            # Nettoyer le fichier temporaire
            if temp_file_path and os.path.exists(temp_file_path):
                try:
                    os.remove(temp_file_path)
                    print(f"🗑️ Fichier vidéo temporaire supprimé: {temp_file_path}")
                except Exception as e:
                    print(f"⚠️ Erreur suppression fichier temporaire: {e}")
    
    def upload_from_url(
        self, 
        url: str, 
        folder: str = "bf1",
        public_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Upload une image depuis une URL vers Cloudinary
        
        Args:
            url: URL de l'image
            folder: Dossier Cloudinary
            public_id: ID public personnalisé (optionnel)
        
        Returns:
            Dict contenant l'URL et les métadonnées
        """
        try:
            result = cloudinary_service.upload_from_url(
                url=url,
                folder=folder,
                public_id=public_id
            )
            
            return result
            
        except Exception as e:
            print(f"❌ Erreur upload depuis URL: {e}")
            raise e
    
    def delete_image(self, public_id: str) -> bool:
        """
        Supprimer une image de Cloudinary
        
        Args:
            public_id: ID public de l'image
        
        Returns:
            True si suppression réussie
        """
        return cloudinary_service.delete_image(public_id)

# Instance globale
file_upload_handler = FileUploadHandler()
