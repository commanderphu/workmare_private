"""
Calendar and Integration management endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
import uuid

from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials

from ...db.session import get_db
from ...schemas import (
    CalendarEventCreate,
    CalendarEventUpdate,
    CalendarEventResponse,
    IntegrationCreate,
    IntegrationUpdate,
    IntegrationResponse,
    SyncRequest,
    SyncResponse,
)
from ...models import User, CalendarEvent, Integration
from ...models.calendar_event import CalendarSyncStatus
from ...models.integration import IntegrationType, SyncDirection
from ..dependencies import get_current_user
from ...services.caldav_service import CalDAVService
from ...services.google_calendar_service import GoogleCalendarService
from ...services.calendar_sync_service import CalendarSyncService
from ...services.task_event_mapping_service import TaskEventMappingService
from ...core.config import settings

router = APIRouter(prefix="/calendar", tags=["Calendar"])


# ===== Calendar Events Endpoints =====

@router.get("/events/", response_model=List[CalendarEventResponse])
def get_calendar_events(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    sync_status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all calendar events for current user

    Filters:
    - start_date: Only events starting after this date
    - end_date: Only events ending before this date
    - sync_status: Filter by sync status (pending, synced, failed, conflict)
    """
    query = db.query(CalendarEvent).filter(CalendarEvent.user_id == current_user.id)

    # Apply filters
    if start_date:
        query = query.filter(CalendarEvent.start_time >= start_date)
    if end_date:
        query = query.filter(CalendarEvent.end_time <= end_date)
    if sync_status:
        query = query.filter(CalendarEvent.sync_status == sync_status)

    # Order by start time
    query = query.order_by(CalendarEvent.start_time)

    events = query.offset(skip).limit(limit).all()
    return events


@router.post("/events/", response_model=CalendarEventResponse, status_code=status.HTTP_201_CREATED)
def create_calendar_event(
    event_data: CalendarEventCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new calendar event
    """
    # Validate dates
    if event_data.end_time <= event_data.start_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="End time must be after start time"
        )

    # Validate task_id if provided
    if event_data.task_id:
        from ...models import Task
        task = db.query(Task).filter(
            Task.id == event_data.task_id,
            Task.user_id == current_user.id
        ).first()
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )

    # Validate integration if provided
    if event_data.external_calendar_id:
        integration = db.query(Integration).filter(
            Integration.id == event_data.external_calendar_id,
            Integration.user_id == current_user.id
        ).first()
        if not integration:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Calendar integration not found"
            )

    new_event = CalendarEvent(
        user_id=current_user.id,
        task_id=str(event_data.task_id) if event_data.task_id else None,
        title=event_data.title,
        description=event_data.description,
        start_time=event_data.start_time,
        end_time=event_data.end_time,
        all_day=event_data.all_day,
        location=event_data.location,
        external_calendar_id=str(event_data.external_calendar_id) if event_data.external_calendar_id else None,
    )

    db.add(new_event)
    db.commit()
    db.refresh(new_event)

    # TODO: Trigger sync to external calendar if external_calendar_id is set

    return new_event


@router.get("/events/{event_id}", response_model=CalendarEventResponse)
def get_calendar_event(
    event_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific calendar event
    """
    event = db.query(CalendarEvent).filter(
        CalendarEvent.id == str(event_id),
        CalendarEvent.user_id == current_user.id
    ).first()

    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Calendar event not found"
        )

    return event


@router.patch("/events/{event_id}", response_model=CalendarEventResponse)
def update_calendar_event(
    event_id: uuid.UUID,
    event_data: CalendarEventUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update a calendar event
    """
    event = db.query(CalendarEvent).filter(
        CalendarEvent.id == str(event_id),
        CalendarEvent.user_id == current_user.id
    ).first()

    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Calendar event not found"
        )

    # Validate dates if both are being updated
    update_data = event_data.model_dump(exclude_unset=True)
    start = update_data.get('start_time', event.start_time)
    end = update_data.get('end_time', event.end_time)

    if end <= start:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="End time must be after start time"
        )

    # Update fields
    for field, value in update_data.items():
        if field == 'task_id' and value:
            setattr(event, field, str(value))
        else:
            setattr(event, field, value)

    # Mark as pending sync if it was previously synced
    if event.sync_status == CalendarSyncStatus.SYNCED:
        event.sync_status = CalendarSyncStatus.PENDING

    db.commit()
    db.refresh(event)

    # TODO: Trigger sync to external calendar

    return event


@router.delete("/events/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_calendar_event(
    event_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a calendar event
    """
    event = db.query(CalendarEvent).filter(
        CalendarEvent.id == str(event_id),
        CalendarEvent.user_id == current_user.id
    ).first()

    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Calendar event not found"
        )

    # TODO: Delete from external calendar if synced

    db.delete(event)
    db.commit()

    return None


# ===== Integration Endpoints =====

@router.get("/integrations/", response_model=List[IntegrationResponse])
def get_integrations(
    enabled_only: bool = False,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all calendar integrations for current user
    """
    query = db.query(Integration).filter(Integration.user_id == current_user.id)

    if enabled_only:
        query = query.filter(Integration.enabled == True)

    integrations = query.all()

    # Remove sensitive credentials from response
    for integration in integrations:
        if hasattr(integration, 'credentials'):
            integration.credentials = None

    return integrations


@router.post("/integrations/", response_model=IntegrationResponse, status_code=status.HTTP_201_CREATED)
def create_integration(
    integration_data: IntegrationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new calendar integration

    For CalDAV:
    - config: {"url": "https://...", "calendar_name": "..."}
    - credentials: {"username": "...", "password": "..."}
    """
    # TODO: Validate credentials by testing connection
    # For now, just create the integration

    new_integration = Integration(
        user_id=current_user.id,
        name=integration_data.name,
        integration_type=IntegrationType(integration_data.integration_type),
        enabled=integration_data.enabled,
        config=integration_data.config,
        credentials=integration_data.credentials,
        sync_direction=SyncDirection(integration_data.sync_direction),
        auto_sync=integration_data.auto_sync,
        sync_interval_minutes=integration_data.sync_interval_minutes,
    )

    db.add(new_integration)
    db.commit()
    db.refresh(new_integration)

    # Remove credentials from response
    new_integration.credentials = None

    return new_integration


@router.get("/integrations/{integration_id}", response_model=IntegrationResponse)
def get_integration(
    integration_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific integration
    """
    integration = db.query(Integration).filter(
        Integration.id == str(integration_id),
        Integration.user_id == current_user.id
    ).first()

    if not integration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Integration not found"
        )

    # Remove credentials from response
    integration.credentials = None

    return integration


@router.patch("/integrations/{integration_id}", response_model=IntegrationResponse)
def update_integration(
    integration_id: uuid.UUID,
    integration_data: IntegrationUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update an integration
    """
    integration = db.query(Integration).filter(
        Integration.id == str(integration_id),
        Integration.user_id == current_user.id
    ).first()

    if not integration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Integration not found"
        )

    # Update fields
    update_data = integration_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if field == 'sync_direction' and value:
            setattr(integration, field, SyncDirection(value))
        else:
            setattr(integration, field, value)

    db.commit()
    db.refresh(integration)

    # Remove credentials from response
    integration.credentials = None

    return integration


@router.delete("/integrations/{integration_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_integration(
    integration_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete an integration

    This will also set external_calendar_id to NULL for all related events
    """
    integration = db.query(Integration).filter(
        Integration.id == str(integration_id),
        Integration.user_id == current_user.id
    ).first()

    if not integration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Integration not found"
        )

    db.delete(integration)
    db.commit()

    return None


@router.post("/integrations/{integration_id}/test", response_model=dict)
async def test_integration(
    integration_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Test connection to calendar integration
    """
    integration = db.query(Integration).filter(
        Integration.id == str(integration_id),
        Integration.user_id == current_user.id
    ).first()

    if not integration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Integration not found"
        )

    try:
        if integration.integration_type == IntegrationType.CALDAV:
            # Test CalDAV connection
            if not integration.credentials:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Missing credentials"
                )

            caldav_service = CalDAVService(
                url=integration.config.get('url'),
                username=integration.credentials.get('username'),
                password=integration.credentials.get('password')
            )

            success = await caldav_service.test_connection()

            if success:
                calendars = caldav_service.list_calendars()
                return {
                    "success": True,
                    "message": "Connection successful",
                    "calendars": calendars
                }
            else:
                return {
                    "success": False,
                    "message": "Connection failed"
                }
        elif integration.integration_type == IntegrationType.GOOGLE_CALENDAR:
            # Test Google Calendar connection
            if not integration.credentials:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Missing Google OAuth credentials"
                )

            google_service = GoogleCalendarService(integration.credentials)
            result = await google_service.test_connection()

            # Update credentials in case token was refreshed
            updated_creds = google_service.get_updated_credentials()
            integration.credentials = updated_creds
            db.commit()

            return result

        else:
            # TODO: Implement Outlook Calendar test
            raise HTTPException(
                status_code=status.HTTP_501_NOT_IMPLEMENTED,
                detail=f"Testing for {integration.integration_type.value} not yet implemented"
            )

    except Exception as e:
        return {
            "success": False,
            "message": f"Connection test failed: {str(e)}"
        }


@router.post("/events/{event_id}/resolve-conflict", response_model=CalendarEventResponse)
async def resolve_event_conflict(
    event_id: uuid.UUID,
    resolution: str,  # 'keep_local' or 'keep_remote'
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Resolve a conflict for a calendar event

    Args:
        resolution: Either 'keep_local' (keep local changes) or 'keep_remote' (accept remote changes)
    """
    if resolution not in ['keep_local', 'keep_remote']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Resolution must be either 'keep_local' or 'keep_remote'"
        )

    event = db.query(CalendarEvent).filter(
        CalendarEvent.id == str(event_id),
        CalendarEvent.user_id == current_user.id
    ).first()

    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Calendar event not found"
        )

    if event.sync_status != CalendarSyncStatus.CONFLICT:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Event is not in conflict state"
        )

    # Resolve conflict using sync service
    sync_service = CalendarSyncService(db)
    success = await sync_service.resolve_conflict(str(event_id), resolution, current_user)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to resolve conflict"
        )

    # Refresh and return updated event
    db.refresh(event)
    return event


@router.post("/integrations/{integration_id}/sync", response_model=SyncResponse)
async def sync_integration(
    integration_id: uuid.UUID,
    sync_request: SyncRequest = SyncRequest(),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Manually trigger sync for an integration
    """
    integration = db.query(Integration).filter(
        Integration.id == str(integration_id),
        Integration.user_id == current_user.id
    ).first()

    if not integration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Integration not found"
        )

    if not integration.enabled and not sync_request.force:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Integration is disabled. Use force=true to sync anyway."
        )

    # Perform sync using CalendarSyncService
    sync_service = CalendarSyncService(db)
    result = await sync_service.sync_integration(integration, current_user)

    return SyncResponse(
        success=result.errors == 0,
        events_synced=result.to_dict()["total_synced"],
        conflicts=result.conflicts,
        errors=result.errors,
        message="; ".join(result.error_messages) if result.errors > 0 else "Sync completed successfully"
    )


# ===== Task-Event Mapping Endpoints =====

@router.post("/tasks/sync-all", response_model=dict)
def sync_all_tasks_to_calendar(
    force: bool = False,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Bulk sync all tasks with due_dates to calendar events

    Args:
        force: If true, recreate all events from scratch
    """
    mapping_service = TaskEventMappingService(db)
    stats = mapping_service.bulk_sync_user_tasks(current_user, force=force)

    return {
        "success": stats["errors"] == 0,
        "message": f"Synced {stats['processed']} tasks",
        "stats": stats
    }


@router.post("/tasks/cleanup-completed", response_model=dict)
def cleanup_completed_task_events(
    older_than_days: int = 7,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Remove calendar events for completed tasks older than X days

    Args:
        older_than_days: Remove events for tasks completed more than X days ago (default: 7)
    """
    if older_than_days < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="older_than_days must be at least 1"
        )

    mapping_service = TaskEventMappingService(db)
    deleted_count = mapping_service.remove_completed_task_events(current_user, older_than_days)

    return {
        "success": True,
        "message": f"Removed {deleted_count} completed task events",
        "deleted_count": deleted_count
    }


# ===== Google Calendar OAuth Endpoints =====

@router.get("/oauth/google/authorize")
def google_oauth_authorize(
    current_user: User = Depends(get_current_user),
):
    """
    Initiate Google OAuth2 flow

    Redirects user to Google's OAuth consent screen
    """
    if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Google OAuth not configured. Please set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET in .env"
        )

    # Create OAuth flow
    flow = Flow.from_client_config(
        client_config={
            "web": {
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [settings.GOOGLE_REDIRECT_URI],
            }
        },
        scopes=['https://www.googleapis.com/auth/calendar']
    )
    flow.redirect_uri = settings.GOOGLE_REDIRECT_URI

    # Generate authorization URL
    authorization_url, state = flow.authorization_url(
        access_type='offline',  # Get refresh token
        include_granted_scopes='true',
        prompt='consent',  # Force consent screen to get refresh token
        state=str(current_user.id)  # Pass user ID in state for callback
    )

    return {"authorization_url": authorization_url}


@router.get("/oauth/google/callback")
async def google_oauth_callback(
    request: Request,
    code: str,
    state: str,
    db: Session = Depends(get_db)
):
    """
    Google OAuth2 callback endpoint

    Exchanges authorization code for access/refresh tokens and creates integration
    """
    if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Google OAuth not configured"
        )

    try:
        # Recreate the flow
        flow = Flow.from_client_config(
            client_config={
                "web": {
                    "client_id": settings.GOOGLE_CLIENT_ID,
                    "client_secret": settings.GOOGLE_CLIENT_SECRET,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [settings.GOOGLE_REDIRECT_URI],
                }
            },
            scopes=['https://www.googleapis.com/auth/calendar']
        )
        flow.redirect_uri = settings.GOOGLE_REDIRECT_URI

        # Exchange authorization code for tokens
        flow.fetch_token(code=code)
        credentials = flow.credentials

        # Get user ID from state
        user_id = uuid.UUID(state)
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Store credentials and create integration
        credentials_dict = {
            'access_token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'scopes': credentials.scopes,
        }

        # Initialize Google Calendar service to get calendar list
        google_service = GoogleCalendarService(credentials_dict)
        calendars = await google_service.list_calendars()

        # Find primary calendar
        primary_calendar = next((cal for cal in calendars if cal.get('primary')), calendars[0] if calendars else None)

        if not primary_calendar:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No calendars found in Google account"
            )

        # Create integration
        integration = Integration(
            user_id=user.id,
            name=f"Google Calendar - {primary_calendar['name']}",
            integration_type=IntegrationType.GOOGLE_CALENDAR,
            config={
                'calendar_id': primary_calendar['id'],
                'calendar_name': primary_calendar['name'],
                'timezone': primary_calendar.get('timezone', 'UTC'),
            },
            credentials=credentials_dict,
            enabled=True,
            sync_direction=SyncDirection.BIDIRECTIONAL,
            auto_sync=True,
            sync_interval_minutes=15
        )
        db.add(integration)
        db.commit()
        db.refresh(integration)

        # Return success page or redirect
        return {
            "success": True,
            "message": "Google Calendar connected successfully",
            "integration_id": str(integration.id),
            "calendar_name": primary_calendar['name'],
            "available_calendars": calendars
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"OAuth callback failed: {str(e)}"
        )
