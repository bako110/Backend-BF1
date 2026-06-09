"""
Utilitaire pour gérer l'upload de fichiers (Cloudinary ou local selon config)
"""

import os
import uuid
import aiofiles
import asyncio
from fastapi import UploadFile
from typing import Optional, Dict, Any
from app.services.cloudinary_service import cloudinary_service

CHUNK_SIZE = 1024 * 256  # 256 KB par chunk


class FileUploadHandler:
    def __init__(self):
        self.temp_dir = os.getenv("TEMP_UPLOAD_DIR", "/tmp/bf1_uploads")
        os.makedirs(self.temp_dir, exist_ok=True)

    async def _save_temp(self, file: UploadFile) -> str:
        """Sauvegarde le fichier uploadé en temp via I/O async (non-bloquant)."""
        ext = os.path.splitext(file.filename or "file")[1]
        temp_path = os.path.join(self.temp_dir, f"{uuid.uuid4()}{ext}")
        async with aiofiles.open(temp_path, "wb") as buf:
            while chunk := await file.read(CHUNK_SIZE):
                await buf.write(chunk)
        return temp_path

    async def _delete_temp(self, path: str):
        """Supprime le fichier temporaire de manière non-bloquante."""
        try:
            await asyncio.to_thread(os.remove, path)
        except OSError:
            pass

    async def upload_image_to_cloudinary(
        self,
        file: UploadFile,
        folder: str = "bf1",
        public_id: Optional[str] = None
    ) -> Dict[str, Any]:
        temp_path = None
        try:
            temp_path = await self._save_temp(file)
            result = await asyncio.to_thread(
                cloudinary_service.upload_image,
                file_path=temp_path,
                folder=folder,
                public_id=public_id,
            )
            return result
        except Exception as e:
            print(f"❌ Erreur upload image: {e}")
            raise
        finally:
            if temp_path:
                await self._delete_temp(temp_path)

    async def upload_video_to_cloudinary(
        self,
        file: UploadFile,
        folder: str = "bf1/videos",
        public_id: Optional[str] = None
    ) -> Dict[str, Any]:
        temp_path = None
        try:
            temp_path = await self._save_temp(file)
            result = await asyncio.to_thread(
                cloudinary_service.upload_video,
                file_path=temp_path,
                folder=folder,
                public_id=public_id,
            )
            return result
        except Exception as e:
            print(f"❌ Erreur upload vidéo: {e}")
            raise
        finally:
            if temp_path:
                await self._delete_temp(temp_path)

    def upload_from_url(
        self,
        url: str,
        folder: str = "bf1",
        public_id: Optional[str] = None
    ) -> Dict[str, Any]:
        try:
            return cloudinary_service.upload_from_url(url=url, folder=folder, public_id=public_id)
        except Exception as e:
            print(f"❌ Erreur upload depuis URL: {e}")
            raise

    def delete_image(self, public_id: str) -> bool:
        return cloudinary_service.delete_image(public_id)


# Instance globale
file_upload_handler = FileUploadHandler()
