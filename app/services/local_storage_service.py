"""
Service de stockage local — remplace Cloudinary.
Les fichiers sont sauvegardés dans static/uploads/{folder}/ et servis via /static.
"""

import os
import uuid
import shutil
from pathlib import Path
from typing import Optional, Dict, Any
from fastapi import Request

BASE_DIR = Path(__file__).resolve().parents[2]
UPLOAD_ROOT = BASE_DIR / "static" / "uploads"


def _make_url(request: Optional[Request], rel_path: str) -> str:
    """Construit l'URL publique du fichier."""
    base = os.getenv("BASE_URL", "").rstrip("/")
    if not base and request:
        base = str(request.base_url).rstrip("/")
    return f"{base}/static/uploads/{rel_path}"


class LocalStorageService:

    def _dest_dir(self, folder: str) -> Path:
        dest = UPLOAD_ROOT / folder
        dest.mkdir(parents=True, exist_ok=True)
        return dest

    def upload_image(
        self,
        file_path: str,
        folder: str = "bf1",
        public_id: Optional[str] = None,
        request: Optional[Request] = None,
    ) -> Dict[str, Any]:
        ext = Path(file_path).suffix.lower() or ".jpg"
        filename = f"{public_id or uuid.uuid4().hex}{ext}"
        dest = self._dest_dir(folder) / filename
        shutil.copy2(file_path, dest)
        rel = f"{folder}/{filename}"
        url = _make_url(request, rel)
        return {"url": url, "public_id": rel, "path": str(dest)}

    def upload_video(
        self,
        file_path: str,
        folder: str = "bf1/videos",
        public_id: Optional[str] = None,
        request: Optional[Request] = None,
    ) -> Dict[str, Any]:
        ext = Path(file_path).suffix.lower() or ".mp4"
        filename = f"{public_id or uuid.uuid4().hex}{ext}"
        dest = self._dest_dir(folder) / filename
        shutil.copy2(file_path, dest)
        rel = f"{folder}/{filename}"
        url = _make_url(request, rel)
        return {"url": url, "public_id": rel, "path": str(dest)}

    def delete_file(self, public_id: str) -> bool:
        target = UPLOAD_ROOT / public_id
        if target.exists():
            target.unlink()
            return True
        return False

    def get_image_url(self, public_id: str, request: Optional[Request] = None) -> str:
        return _make_url(request, public_id)


local_storage = LocalStorageService()
