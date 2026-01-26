"""
File serving endpoints
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path
from ...core.config import settings

router = APIRouter()


@router.get("/{file_path:path}")
async def serve_file(file_path: str):
    """
    Serve uploaded files

    Note: Authentication removed for now to allow Image.network() to work.
    TODO: Implement proper authenticated image loading with headers
    """
    # Build full path
    full_path = Path(settings.UPLOAD_DIR) / file_path

    # Security: Ensure path is within upload directory (prevent path traversal)
    try:
        full_path = full_path.resolve()
        upload_dir = Path(settings.UPLOAD_DIR).resolve()

        # Check if the resolved path is within upload directory
        if not str(full_path).startswith(str(upload_dir)):
            raise HTTPException(status_code=403, detail="Access denied")
    except Exception as e:
        raise HTTPException(status_code=403, detail=f"Invalid path: {str(e)}")

    # Check if file exists
    if not full_path.exists():
        raise HTTPException(status_code=404, detail=f"File not found: {file_path}")

    if not full_path.is_file():
        raise HTTPException(status_code=403, detail="Not a file")

    # Return file
    return FileResponse(
        path=str(full_path),
        filename=full_path.name,
    )
