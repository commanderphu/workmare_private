"""
Push notification endpoints
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ...db.session import get_db
from ...models.user import User
from ..dependencies import get_current_active_user

router = APIRouter(prefix="/notifications", tags=["notifications"])


class FCMTokenRequest(BaseModel):
    token: str


@router.post("/fcm-token")
def register_fcm_token(
    payload: FCMTokenRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Register or update the FCM device token for the current user."""
    if not payload.token:
        raise HTTPException(status_code=400, detail="Token darf nicht leer sein")

    current_user.fcm_token = payload.token
    db.commit()
    return {"status": "ok"}


@router.delete("/fcm-token")
def delete_fcm_token(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Remove FCM token (e.g. on logout)."""
    current_user.fcm_token = None
    db.commit()
    return {"status": "ok"}
