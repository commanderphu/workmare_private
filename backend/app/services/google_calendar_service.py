"""
Google Calendar API Service

Handles Google Calendar API operations using OAuth2 authentication.
"""

from typing import Dict, List, Optional
from datetime import datetime, timedelta
import logging

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from ..core.config import settings

logger = logging.getLogger(__name__)


class GoogleCalendarService:
    """Service for Google Calendar API operations"""

    SCOPES = ['https://www.googleapis.com/auth/calendar']

    def __init__(self, credentials_dict: Dict):
        """
        Initialize Google Calendar Service with OAuth credentials

        Args:
            credentials_dict: Dictionary containing access_token, refresh_token, etc.
        """
        self.credentials = Credentials(
            token=credentials_dict.get('access_token'),
            refresh_token=credentials_dict.get('refresh_token'),
            token_uri='https://oauth2.googleapis.com/token',
            client_id=settings.GOOGLE_CLIENT_ID,
            client_secret=settings.GOOGLE_CLIENT_SECRET,
            scopes=self.SCOPES
        )
        self.service = None

    def _get_service(self):
        """Get or refresh Google Calendar service"""
        if self.service is None:
            # Refresh token if expired
            if self.credentials.expired and self.credentials.refresh_token:
                self.credentials.refresh(Request())

            self.service = build('calendar', 'v3', credentials=self.credentials)

        return self.service

    def get_updated_credentials(self) -> Dict:
        """
        Get updated credentials (including refreshed access token)

        Returns:
            Dictionary with updated credentials
        """
        return {
            'access_token': self.credentials.token,
            'refresh_token': self.credentials.refresh_token,
            'token_uri': self.credentials.token_uri,
            'scopes': self.credentials.scopes,
        }

    async def list_calendars(self) -> List[Dict]:
        """
        List all calendars accessible by the user

        Returns:
            List of calendar dictionaries with id, name, description
        """
        try:
            service = self._get_service()
            calendar_list = service.calendarList().list().execute()

            calendars = []
            for calendar in calendar_list.get('items', []):
                calendars.append({
                    'id': calendar['id'],
                    'name': calendar['summary'],
                    'description': calendar.get('description', ''),
                    'timezone': calendar.get('timeZone', 'UTC'),
                    'primary': calendar.get('primary', False),
                })

            return calendars

        except HttpError as e:
            logger.error(f"Error listing Google calendars: {e}")
            raise Exception(f"Failed to list calendars: {e}")

    async def get_events(
        self,
        calendar_id: str = 'primary',
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        max_results: int = 250
    ) -> List[Dict]:
        """
        Fetch events from Google Calendar

        Args:
            calendar_id: Calendar ID (default: 'primary')
            start_date: Start date filter
            end_date: End date filter
            max_results: Maximum number of events to return

        Returns:
            List of event dictionaries
        """
        try:
            service = self._get_service()

            # Default to 30 days if no dates provided
            if not start_date:
                start_date = datetime.utcnow()
            if not end_date:
                end_date = start_date + timedelta(days=30)

            # Format for Google Calendar API (RFC3339)
            time_min = start_date.isoformat() + 'Z'
            time_max = end_date.isoformat() + 'Z'

            events_result = service.events().list(
                calendarId=calendar_id,
                timeMin=time_min,
                timeMax=time_max,
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime'
            ).execute()

            events = []
            for event in events_result.get('items', []):
                events.append(self._parse_event(event))

            return events

        except HttpError as e:
            logger.error(f"Error fetching Google Calendar events: {e}")
            raise Exception(f"Failed to fetch events: {e}")

    async def create_event(
        self,
        calendar_id: str,
        title: str,
        start_time: datetime,
        end_time: datetime,
        description: Optional[str] = None,
        location: Optional[str] = None,
        all_day: bool = False
    ) -> Dict:
        """
        Create an event in Google Calendar

        Returns:
            Created event dictionary
        """
        try:
            service = self._get_service()

            event_body = {
                'summary': title,
                'description': description or '',
                'location': location or '',
            }

            if all_day:
                event_body['start'] = {'date': start_time.date().isoformat()}
                event_body['end'] = {'date': end_time.date().isoformat()}
            else:
                event_body['start'] = {
                    'dateTime': start_time.isoformat(),
                    'timeZone': 'UTC',
                }
                event_body['end'] = {
                    'dateTime': end_time.isoformat(),
                    'timeZone': 'UTC',
                }

            created_event = service.events().insert(
                calendarId=calendar_id,
                body=event_body
            ).execute()

            return self._parse_event(created_event)

        except HttpError as e:
            logger.error(f"Error creating Google Calendar event: {e}")
            raise Exception(f"Failed to create event: {e}")

    async def update_event(
        self,
        calendar_id: str,
        event_id: str,
        title: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        description: Optional[str] = None,
        location: Optional[str] = None,
        all_day: Optional[bool] = None
    ) -> Dict:
        """
        Update an existing event in Google Calendar

        Returns:
            Updated event dictionary
        """
        try:
            service = self._get_service()

            # Fetch existing event
            event = service.events().get(
                calendarId=calendar_id,
                eventId=event_id
            ).execute()

            # Update fields
            if title is not None:
                event['summary'] = title
            if description is not None:
                event['description'] = description
            if location is not None:
                event['location'] = location

            if start_time is not None and end_time is not None:
                if all_day:
                    event['start'] = {'date': start_time.date().isoformat()}
                    event['end'] = {'date': end_time.date().isoformat()}
                else:
                    event['start'] = {
                        'dateTime': start_time.isoformat(),
                        'timeZone': 'UTC',
                    }
                    event['end'] = {
                        'dateTime': end_time.isoformat(),
                        'timeZone': 'UTC',
                    }

            updated_event = service.events().update(
                calendarId=calendar_id,
                eventId=event_id,
                body=event
            ).execute()

            return self._parse_event(updated_event)

        except HttpError as e:
            logger.error(f"Error updating Google Calendar event: {e}")
            raise Exception(f"Failed to update event: {e}")

    async def delete_event(self, calendar_id: str, event_id: str):
        """Delete an event from Google Calendar"""
        try:
            service = self._get_service()
            service.events().delete(
                calendarId=calendar_id,
                eventId=event_id
            ).execute()

        except HttpError as e:
            logger.error(f"Error deleting Google Calendar event: {e}")
            raise Exception(f"Failed to delete event: {e}")

    def _parse_event(self, event: Dict) -> Dict:
        """
        Parse Google Calendar event to our format

        Args:
            event: Google Calendar event dictionary

        Returns:
            Parsed event dictionary
        """
        # Handle all-day vs timed events
        start = event.get('start', {})
        end = event.get('end', {})

        if 'date' in start:
            # All-day event
            start_time = datetime.fromisoformat(start['date'])
            end_time = datetime.fromisoformat(end['date'])
            all_day = True
        else:
            # Timed event
            start_time = datetime.fromisoformat(start['dateTime'].replace('Z', '+00:00'))
            end_time = datetime.fromisoformat(end['dateTime'].replace('Z', '+00:00'))
            all_day = False

        # Get last modified time
        updated = event.get('updated')
        last_modified = datetime.fromisoformat(updated.replace('Z', '+00:00')) if updated else datetime.utcnow()

        return {
            'id': event['id'],
            'title': event.get('summary', ''),
            'description': event.get('description', ''),
            'location': event.get('location', ''),
            'start_time': start_time,
            'end_time': end_time,
            'all_day': all_day,
            'last_modified': last_modified,
            'etag': event.get('etag', ''),
        }

    async def test_connection(self) -> Dict:
        """
        Test connection to Google Calendar API

        Returns:
            Dictionary with success status and available calendars
        """
        try:
            calendars = await self.list_calendars()
            return {
                'success': True,
                'calendars': calendars,
                'message': f'Successfully connected. Found {len(calendars)} calendar(s).'
            }
        except Exception as e:
            return {
                'success': False,
                'calendars': [],
                'message': str(e)
            }
