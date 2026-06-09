"""
API upload de fichiers — stockage local sur le VPS.
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, Request
from typing import Optional
from app.utils.file_upload import file_upload_handler
from app.services.local_storage_service import local_storage

router = APIRouter()


@router.post("/image")
async def upload_image(
    request: Request,
    file: UploadFile = File(...),
    folder: Optional[str] = "bf1",
    public_id: Optional[str] = None,
):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Le fichier doit être une image")
    try:
        result = await file_upload_handler.upload_image(
            file=file, folder=folder, public_id=public_id, request=request
        )
        return {"success": True, "message": "Image uploadée avec succès", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/video")
async def upload_video(
    request: Request,
    file: UploadFile = File(...),
    folder: Optional[str] = "bf1/videos",
    public_id: Optional[str] = None,
):
    if not file.content_type.startswith("video/"):
        raise HTTPException(status_code=400, detail="Le fichier doit être une vidéo")
    try:
        result = await file_upload_handler.upload_video(
            file=file, folder=folder, public_id=public_id, request=request
        )
        return {"success": True, "message": "Vidéo uploadée avec succès", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{public_id:path}")
async def delete_file(public_id: str):
    success = local_storage.delete_file(public_id)
    if success:
        return {"success": True, "message": "Fichier supprimé avec succès"}
    raise HTTPException(status_code=404, detail="Fichier non trouvé")
