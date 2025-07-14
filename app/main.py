import os
from uuid import uuid4
from fastapi import FastAPI, Depends, UploadFile, File, HTTPException, status, Response
from fastapi.responses import FileResponse
from fastapi.security import OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import aiofiles
import logging

AVATAR_DIR = './avatars'
ALLOWED_MIME_TYPES = {"image/jpeg", "image/png"}
MAX_AVATAR_SIZE = 2 * 1024 * 1024  # 2MB

if not os.path.exists(AVATAR_DIR):
    os.makedirs(AVATAR_DIR)

# Set up logging
logging.basicConfig(
    format='%(asctime)s %(levelname)s %(message)s',
    level=logging.INFO
)
logger = logging.getLogger("avatar")

app = FastAPI(
    title="User Profile Avatar Management API",
    description="API for securely uploading and retrieving user avatars with authentication, validation, and structured logging.",
    version="1.0.0"
)

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

# Simulated user 'database'
USERS = {
    "u1": {"id": "u1", "username": "alice", "avatar_filename": None},
    "u2": {"id": "u2", "username": "bob", "avatar_filename": None}
}

# Pydantic models
class User(BaseModel):
    id: str
    username: str
    avatar_filename: Optional[str] = None

class AvatarUploadResponse(BaseModel):
    message: str
    avatar_url: str
    user_id: str

class ErrorResponse(BaseModel):
    detail: str

# Dependency to get current authenticated user
def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    # Placeholder authentication logic. In real app, verify & decode JWT or token!
    # For this assessment, the token is the user id (e.g., "u1").
    user = USERS.get(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid authentication token.")
    return User(**user)

# Dependency to get any user by user_id
def get_user_by_id(user_id: str) -> User:
    user = USERS.get(user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail=f"User not found."
        )
    return User(**user)

# POST endpoint to upload current user's avatar
@app.post(
    "/users/me/avatar",
    response_model=AvatarUploadResponse,
    status_code=201,
    responses={
        400: {"model": ErrorResponse, "description": "Validation failed"},
        413: {"model": ErrorResponse, "description": "Avatar too large"},
        401: {"model": ErrorResponse, "description": "Not authenticated"}
    },
    tags=["Avatar"]
)
async def upload_avatar(
    file: UploadFile = File(..., description="Avatar image (PNG or JPEG, max 2MB)"),
    current_user: User = Depends(get_current_user)
):
    logger.info(f"[UPLOAD_ATTEMPT] User: {current_user.id}, Filename: {file.filename}")
    if file.content_type not in ALLOWED_MIME_TYPES:
        logger.warning(f"[UPLOAD_FAILED] User: {current_user.id}, Reason: Invalid MIME type ({file.content_type})")
        raise HTTPException(
            status_code=400, detail="Only PNG and JPEG images are allowed."
        )

    contents = await file.read()
    if len(contents) > MAX_AVATAR_SIZE:
        logger.warning(f"[UPLOAD_FAILED] User: {current_user.id}, Filename: {file.filename}, Reason: File too large ({len(contents)} bytes)")
        raise HTTPException(status_code=413, detail="Avatar image is too large.")
    ext = os.path.splitext(file.filename)[1].lower()
    safe_ext = ext if ext in [".png", ".jpg", ".jpeg"] else (".jpg" if file.content_type=="image/jpeg" else ".png")
    filename = f"{current_user.id}_{uuid4().hex}{safe_ext}"
    file_path = os.path.join(AVATAR_DIR, filename)

    # Remove old avatar file if exists
    old_filename = USERS[current_user.id]["avatar_filename"]
    if old_filename:
        old_path = os.path.join(AVATAR_DIR, old_filename)
        try:
            os.remove(old_path)
        except Exception:
            pass
    # Save new file
    async with aiofiles.open(file_path, "wb") as f:
        await f.write(contents)
    USERS[current_user.id]["avatar_filename"] = filename
    logger.info(f"[UPLOAD_SUCCESS] User: {current_user.id}, Saved as: {filename}")
    return AvatarUploadResponse(
        message="Avatar uploaded successfully.",
        avatar_url=f"/users/{current_user.id}/avatar",
        user_id=current_user.id
    )

# GET endpoint to retrieve any user's avatar
@app.get(
    "/users/{user_id}/avatar",
    responses={
        200: {
            "content": {"image/png": {}, "image/jpeg": {}},
            "description": "Avatar image"
        },
        404: {"model": ErrorResponse, "description": "Avatar not found"}
    },
    tags=["Avatar"]
)
async def get_user_avatar(user_id: str, response: Response):
    user = get_user_by_id(user_id)
    filename = user.avatar_filename
    if not filename:
        raise HTTPException(status_code=404, detail="User has no avatar.")
    file_path = os.path.join(AVATAR_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Avatar file not found.")
    # Guess correct content type
    mimetype = "image/png" if filename.endswith(".png") else "image/jpeg"
    response.headers["Content-Disposition"] = f"inline; filename={filename}"
    return FileResponse(
        path=file_path,
        media_type=mimetype,
        filename=filename,
    )
