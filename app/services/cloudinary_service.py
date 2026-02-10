"""
Service Cloudinary pour gérer l'upload des images
"""

import cloudinary
import cloudinary.uploader
import cloudinary.api
import os
from typing import Optional, Dict, Any

class CloudinaryService:
    def __init__(self):
        """Initialiser la configuration Cloudinary"""
        cloudinary.config(
            cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME', 'dgw62ulgb'),
            api_key=os.getenv('CLOUDINARY_API_KEY', '564629531797987'),
            api_secret=os.getenv('CLOUDINARY_API_SECRET', 'bwIGyXjIG8aQC0U6oV6ycHNhR90')
        )
        print("✅ Cloudinary configuré")
    
    def upload_image(self, file_path: str, folder: str = "bf1", public_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Upload une image sur Cloudinary
        
        Args:
            file_path: Chemin du fichier à uploader
            folder: Dossier Cloudinary où stocker l'image
            public_id: ID public personnalisé (optionnel)
        
        Returns:
            Dict contenant l'URL et les métadonnées de l'image
        """
        try:
            print(f"📤 Upload image vers Cloudinary: {file_path}")
            
            upload_options = {
                'folder': folder,
                'resource_type': 'image',
                'overwrite': True,
                'quality': 'auto:good',
                'fetch_format': 'auto'
            }
            
            if public_id:
                upload_options['public_id'] = public_id
            
            result = cloudinary.uploader.upload(file_path, **upload_options)
            
            print(f"✅ Image uploadée: {result['secure_url']}")
            
            return {
                'url': result['secure_url'],
                'public_id': result['public_id'],
                'width': result.get('width'),
                'height': result.get('height'),
                'format': result.get('format'),
                'resource_type': result.get('resource_type')
            }
            
        except Exception as e:
            print(f"❌ Erreur upload Cloudinary: {e}")
            raise e
    
    def upload_from_url(self, url: str, folder: str = "bf1", public_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Upload une image depuis une URL vers Cloudinary
        
        Args:
            url: URL de l'image à uploader
            folder: Dossier Cloudinary où stocker l'image
            public_id: ID public personnalisé (optionnel)
        
        Returns:
            Dict contenant l'URL et les métadonnées de l'image
        """
        try:
            print(f"📤 Upload image depuis URL vers Cloudinary: {url}")
            
            upload_options = {
                'folder': folder,
                'resource_type': 'image',
                'overwrite': True,
                'quality': 'auto:good',
                'fetch_format': 'auto'
            }
            
            if public_id:
                upload_options['public_id'] = public_id
            
            result = cloudinary.uploader.upload(url, **upload_options)
            
            print(f"✅ Image uploadée depuis URL: {result['secure_url']}")
            
            return {
                'url': result['secure_url'],
                'public_id': result['public_id'],
                'width': result.get('width'),
                'height': result.get('height'),
                'format': result.get('format'),
                'resource_type': result.get('resource_type')
            }
            
        except Exception as e:
            print(f"❌ Erreur upload Cloudinary depuis URL: {e}")
            raise e
    
    def delete_image(self, public_id: str) -> bool:
        """
        Supprimer une image de Cloudinary
        
        Args:
            public_id: ID public de l'image à supprimer
        
        Returns:
            True si suppression réussie, False sinon
        """
        try:
            print(f"🗑️ Suppression image Cloudinary: {public_id}")
            result = cloudinary.uploader.destroy(public_id)
            
            if result.get('result') == 'ok':
                print(f"✅ Image supprimée: {public_id}")
                return True
            else:
                print(f"⚠️ Image non trouvée ou déjà supprimée: {public_id}")
                return False
                
        except Exception as e:
            print(f"❌ Erreur suppression Cloudinary: {e}")
            return False
    
    def get_image_url(self, public_id: str, transformation: Optional[Dict] = None) -> str:
        """
        Obtenir l'URL d'une image avec transformations optionnelles
        
        Args:
            public_id: ID public de l'image
            transformation: Dict de transformations Cloudinary (optionnel)
        
        Returns:
            URL de l'image
        """
        try:
            if transformation:
                url = cloudinary.CloudinaryImage(public_id).build_url(**transformation)
            else:
                url = cloudinary.CloudinaryImage(public_id).build_url()
            
            return url
            
        except Exception as e:
            print(f"❌ Erreur génération URL Cloudinary: {e}")
            return ""
    
    def upload_video(self, file_path: str, folder: str = "bf1/videos", public_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Upload une vidéo sur Cloudinary
        
        Args:
            file_path: Chemin du fichier vidéo à uploader
            folder: Dossier Cloudinary où stocker la vidéo
            public_id: ID public personnalisé (optionnel)
        
        Returns:
            Dict contenant l'URL et les métadonnées de la vidéo
        """
        try:
            print(f"📤 Upload vidéo vers Cloudinary: {file_path}")
            
            upload_options = {
                'folder': folder,
                'resource_type': 'video',
                'overwrite': True,
                'quality': 'auto:good'
            }
            
            if public_id:
                upload_options['public_id'] = public_id
            
            result = cloudinary.uploader.upload(file_path, **upload_options)
            
            print(f"✅ Vidéo uploadée: {result['secure_url']}")
            
            return {
                'url': result['secure_url'],
                'public_id': result['public_id'],
                'width': result.get('width'),
                'height': result.get('height'),
                'format': result.get('format'),
                'duration': result.get('duration'),
                'resource_type': result.get('resource_type')
            }
            
        except Exception as e:
            print(f"❌ Erreur upload vidéo Cloudinary: {e}")
            raise e

# Instance globale du service
cloudinary_service = CloudinaryService()
