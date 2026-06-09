"""
Utilitaire pour gérer l'upload de fichiers — stockage local sur le VPS.
"""

import os
import uuid
import aiofiles
import asyncio
from fastapi import UploadFile, Request
from typing import Optional, Dict, Any
from app.services.local_storage_service import local_storage

CHUNK_SIZE = 1024 * 256  # 256 KB


class FileUploadHandler:
    def __init__(self):
        self.temp_dir = os.getenv("TEMP_UPLOAD_DIR", "/tmp/bf1_uploads")
        os.makedirs(self.temp_dir, exist_ok=True)

    async def _save_temp(self, file: UploadFile) -> str:
        ext = os.path.splitext(file.filename or "file")[1]
        temp_path = os.path.join(self.temp_dir, f"{uuid.uuid4()}{ext}")
        async with aiofiles.open(temp_path, "wb") as buf:
            while chunk := await file.read(CHUNK_SIZE):
                await buf.write(chunk)
        return temp_path

    async def _delete_temp(self, path: str):
        try:
            await asyncio.to_thread(os.remove, path)
        except OSError:
            pass

    async def upload_image(
        self,
        file: UploadFile,
        folder: str = "bf1",
        public_id: Optional[str] = None,
        request: Optional[Request] = None,
    ) -> Dict[str, Any]:
        temp_path = None
        try:
            temp_path = await self._save_temp(file)
            result = await asyncio.to_thread(
                local_storage.upload_image,
                file_path=temp_path,
                folder=folder,
                public_id=public_id,
                request=request,
            )
            return result
        finally:
            if temp_path:
                await self._delete_temp(temp_path)

    # Alias conservé pour compatibilité avec les appels existants
    async def upload_image_to_cloudinary(
        self,
        file: UploadFile,
        folder: str = "bf1",
        public_id: Optional[str] = None,
        request: Optional[Request] = None,
    ) -> Dict[str, Any]:
        return await self.upload_image(file, folder, public_id, request)

    async def upload_video(
        self,
        file: UploadFile,
        folder: str = "bf1/videos",
        public_id: Optional[str] = None,
        request: Optional[Request] = None,
    ) -> Dict[str, Any]:
        temp_path = None
        try:
            temp_path = await self._save_temp(file)
            result = await asyncio.to_thread(
                local_storage.upload_video,
                file_path=temp_path,
                folder=folder,
                public_id=public_id,
                request=request,
            )
            return result
        finally:
            if temp_path:
                await self._delete_temp(temp_path)

    async def upload_video_to_cloudinary(
        self,
        file: UploadFile,
        folder: str = "bf1/videos",
        public_id: Optional[str] = None,
        request: Optional[Request] = None,
    ) -> Dict[str, Any]:
        return await self.upload_video(file, folder, public_id, request)

    def delete_image(self, public_id: str) -> bool:
        return local_storage.delete_file(public_id)


file_upload_handler = FileUploadHandler()
