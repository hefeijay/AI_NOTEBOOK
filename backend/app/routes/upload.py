import os
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import JSONResponse
from app.models import User
from app.auth import get_current_user

UPLOAD_DIR = os.path.join(os.getcwd(), "data", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

router = APIRouter(prefix="/upload", tags=["upload"])


@router.post("")
async def upload_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    if not file:
        raise HTTPException(status_code=400, detail="No file uploaded")
    file_ext = os.path.splitext(file.filename)[1]
    filename = os.urandom(16).hex() + file_ext
    save_path = os.path.join(UPLOAD_DIR, filename)
    try:
        with open(save_path, "wb") as f:
            content = await file.read()
            f.write(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {e}")

    url = f"/static/uploads/{filename}"
    return JSONResponse({"url": url})

