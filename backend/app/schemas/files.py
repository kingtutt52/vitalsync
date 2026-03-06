from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class FileUploadResponse(BaseModel):
    id: str
    user_id: str
    file_type: str
    original_filename: str
    mime_type: Optional[str]
    parsed_summary: Optional[str]
    uploaded_at: datetime

    model_config = {"from_attributes": True}
