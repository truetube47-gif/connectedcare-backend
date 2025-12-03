import shutil
from pathlib import Path
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from app.utils.security import get_current_active_user
from app.models.user import User

router = APIRouter(prefix="/uploads", tags=["Uploads"])

# Create a directory for chat images if it doesn't exist
UPLOAD_DIR = Path("uploads/chat_images")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

@router.post("/chat-image")
async def upload_chat_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user)
):
    """
    Handles uploading an image for use in chat.
    Saves the file and returns its access URL.
    """
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Only image files are allowed.")

    try:
        # Sanitize filename and create a unique path
        # Note: In a real production app, you'd generate a unique ID (e.g., UUID)
        # for the filename to prevent overwrites and conflicts.
        safe_filename = f"{current_user.id}_{Path(file.filename).name}"
        destination_path = UPLOAD_DIR / safe_filename
        
        with destination_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
    finally:
        file.file.close()

    # The URL that the frontend will use to display the image.
    # Assumes you have a static file serving route setup at "/media".
    media_url = f"/media/chat_images/{safe_filename}"
    
    return {"attachment_url": media_url}
