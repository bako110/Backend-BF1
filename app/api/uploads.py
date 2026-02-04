from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile
from app.utils.auth import get_admin_user
import os
from pathlib import Path
from uuid import uuid4

router = APIRouter()

_ALLOWED_IMAGE_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}


@router.post("/image")
async def upload_image(
    request: Request,
    file: UploadFile = File(...),
    current_user=Depends(get_admin_user),
):
    if file.content_type not in _ALLOWED_IMAGE_CONTENT_TYPES:
        raise HTTPException(status_code=400, detail="Invalid image type")

    static_dir = Path(__file__).resolve().parents[2] / "static"
    upload_dir = static_dir / "uploads"
    os.makedirs(upload_dir, exist_ok=True)

    ext = Path(file.filename or "").suffix.lower()
    if not ext:
        ext = ".jpg" if file.content_type == "image/jpeg" else ".png"

    filename = f"{uuid4().hex}{ext}"
    target_path = upload_dir / filename

    contents = await file.read()
    with open(target_path, "wb") as f:
        f.write(contents)

    relative_url = f"/static/uploads/{filename}"
    base_url = str(request.base_url).rstrip("/")
    return {"url": f"{base_url}{relative_url}"}
