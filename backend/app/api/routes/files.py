import json
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session
from typing import List

from app.api.deps import get_db, get_current_user, require_tier
from app.models.user import User
from app.models.files import UploadedFile
from app.schemas.files import FileUploadResponse
from app.services import storage, file_parser

router = APIRouter(prefix="/files", tags=["files"])

ALLOWED_BLOODWORK_TYPES = {
    "application/pdf",
    "image/jpeg",
    "image/jpg",
    "image/png",
    "image/webp",
}

MAX_FILE_SIZE_BYTES = 20 * 1024 * 1024  # 20 MB


@router.post(
    "/bloodwork-upload",
    response_model=FileUploadResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_tier("premium_lite"))],
)
async def upload_bloodwork(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Upload a bloodwork PDF or image for record keeping."""
    if file.content_type not in ALLOWED_BLOODWORK_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Unsupported file type '{file.content_type}'. Accepted: PDF, JPEG, PNG, WEBP.",
        )

    stored_path = await storage.save_file(current_user.id, "bloodwork", file)

    record = UploadedFile(
        user_id=current_user.id,
        file_type="bloodwork",
        original_filename=file.filename,
        stored_path=stored_path,
        mime_type=file.content_type,
        parsed_summary=json.dumps({"status": "stored", "note": "OCR/AI extraction coming in a future release."}),
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.post(
    "/genetics-upload",
    response_model=FileUploadResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_tier("vital_pro"))],
)
async def upload_genetics(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Upload a 23andMe raw data text file (.txt).
    Parses known SNP variants and stores a lightweight summary.
    Requires Vital Pro tier.
    """
    if not (file.filename or "").lower().endswith(".txt"):
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Genetics upload must be a .txt file (23andMe raw export format).",
        )

    stored_path = await storage.save_file(current_user.id, "genetics", file)

    # Parse synchronously — file is already on disk
    parsed_summary = file_parser.parse_genetics_file(stored_path)

    record = UploadedFile(
        user_id=current_user.id,
        file_type="genetics",
        original_filename=file.filename,
        stored_path=stored_path,
        mime_type="text/plain",
        parsed_summary=parsed_summary,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.get("/", response_model=List[FileUploadResponse])
def list_files(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return (
        db.query(UploadedFile)
        .filter(UploadedFile.user_id == current_user.id)
        .order_by(UploadedFile.uploaded_at.desc())
        .all()
    )
