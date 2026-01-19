# Calendar Integration

## Overview

Die Kalender-Integration ermöglicht Two-Way Synchronisation zwischen Workmate Private und externen Kalendern. Tasks werden automatisch als Events eingetragen und Änderungen in beide Richtungen synchronisiert.

---

## Supported Calendar Systems

### 1. CalDAV (Universal)

**Kompatible Services:**
- Nextcloud Calendar
- ownCloud Calendar
- Apple Calendar (iCloud)
- Radicale
- Baikal
- SOGo

**Warum CalDAV?**
- ✅ Offener Standard (RFC 4791)
- ✅ Self-Hosting friendly
- ✅ Privacy (keine Cloud-Abhängigkeit)
- ✅ Breite Kompatibilität

**Implementation:**
```python
import caldav
from caldav import DAVClient

class CalDAVIntegration:
    def __init__(self, url: str, username: str, password: str):
        self.client = DAVClient(
            url=url,
            username=username,
            password=password
        )
        self.principal = self.client.principal()
        self.calendars = self.principal.calendars()
    
    async def create_event(
        self,
        calendar_name: str,
        title: str,
        start: datetime,
        end: datetime,
        description: str = None
    ) -> str:
        """Create event in calendar, return external ID"""
        
        calendar = self._get_calendar_by_name(calendar_name)
        
        # Create iCal event
        ical = self._build_ical_event(title, start, end, description)
        
        # Save to calendar
        event = calendar.save_event(ical)
        
        return event.id
    
    def _build_ical_event(
        self,
        title: str,
        start: datetime,
        end: datetime,
        description: str = None
    ) -> str:
        """Build iCal format event"""
        
        return f"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Workmate Private//EN
BEGIN:VEVENT
UID:{uuid.uuid4()}@workmate.private
DTSTAMP:{datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')}
DTSTART:{start.strftime('%Y%m%dT%H%M%S')}
DTEND:{end.strftime('%Y%m%dT%H%M%S')}
SUMMARY:{title}
DESCRIPTION:{description or ''}
END:VEVENT
END:VCALENDAR"""
    
    async def sync_from_calendar(self, calendar_name: str) -> List[CalendarEvent]:
        """Fetch events from calendar"""
        
        calendar = self._get_calendar_by_name(calendar_name)
        
        # Get events from last 30 days to next 365 days
        start = datetime.now() - timedelta(days=30)
        end = datetime.now() + timedelta(days=365)
        
        events = calendar.date_search(start=start, end=end)
        
        parsed_events = []
        for event in events:
            parsed = self._parse_ical_event(event.data)
            parsed_events.append(parsed)
        
        return parsed_events
```

### 2. Google Calendar API

**Setup:**
```python
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

class GoogleCalendarIntegration:
    def __init__(self, credentials: Credentials):
        self.service = build('calendar', 'v3', credentials=credentials)
    
    async def create_event(
        self,
        calendar_id: str,
        title: str,
        start: datetime,
        end: datetime,
        description: str = None
    ) -> str:
        """Create event in Google Calendar"""
        
        event = {
            'summary': title,
            'description': description,
            'start': {
                'dateTime': start.isoformat(),
                'timeZone': 'Europe/Berlin',
            },
            'end': {
                'dateTime': end.isoformat(),
                'timeZone': 'Europe/Berlin',
            },
        }
        
        result = self.service.events().insert(
            calendarId=calendar_id,
            body=event
        ).execute()
        
        return result['id']
    
    async def sync_from_calendar(self, calendar_id: str = 'primary') -> List[dict]:
        """Fetch events from Google Calendar"""
        
        now = datetime.utcnow().isoformat() + 'Z'
        
        events_result = self.service.events().list(
            calendarId=calendar_id,
            timeMin=now,
            maxResults=100,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        return events_result.get('items', [])
    
    async def watch_calendar(self, calendar_id: str, webhook_url: str):
        """Setup push notifications for calendar changes"""
        
        request_body = {
            'id': str(uuid.uuid4()),
            'type': 'web_hook',
            'address': webhook_url
        }
        
        return self.service.events().watch(
            calendarId=calendar_id,
            body=request_body
        ).execute()
```

**OAuth2 Flow:**
```python
from google_auth_oauthlib.flow import Flow

SCOPES = ['https://www.googleapis.com/auth/calendar']

async def google_oauth_init(user_id: UUID) -> str:
    """Initialize OAuth flow, return authorization URL"""
    
    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "redirect_uris": [settings.GOOGLE_REDIRECT_URI],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token"
            }
        },
        scopes=SCOPES,
        redirect_uri=settings.GOOGLE_REDIRECT_URI
    )
    
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        state=str(user_id)
    )
    
    return authorization_url

async def google_oauth_callback(code: str, state: str):
    """Handle OAuth callback"""
    
    user_id = UUID(state)
    
    flow = Flow.from_client_config(...)
    flow.fetch_token(code=code)
    
    credentials = flow.credentials
    
    # Save credentials encrypted
    await integration_service.save_credentials(
        user_id=user_id,
        integration_type="google_calendar",
        credentials={
            "token": credentials.token,
            "refresh_token": credentials.refresh_token,
            "token_uri": credentials.token_uri,
            "client_id": credentials.client_id,
            "client_secret": credentials.client_secret,
            "scopes": credentials.scopes
        }
    )
```

### 3. Microsoft Outlook (Graph API)

**Setup:**
```python
import msal
import requests

class OutlookIntegration:
    def __init__(self, access_token: str):
        self.access_token = access_token
        self.base_url = "https://graph.microsoft.com/v1.0"
    
    async def create_event(
        self,
        calendar_id: str,
        title: str,
        start: datetime,
        end: datetime,
        description: str = None
    ) -> str:
        """Create event in Outlook Calendar"""
        
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        event_data = {
            "subject": title,
            "body": {
                "contentType": "HTML",
                "content": description or ""
            },
            "start": {
                "dateTime": start.isoformat(),
                "timeZone": "Europe/Berlin"
            },
            "end": {
                "dateTime": end.isoformat(),
                "timeZone": "Europe/Berlin"
            }
        }
        
        url = f"{self.base_url}/me/calendars/{calendar_id}/events"
        response = requests.post(url, json=event_data, headers=headers)
        
        return response.json()['id']
    
    async def sync_from_calendar(self, calendar_id: str = None) -> List[dict]:
        """Fetch events from Outlook Calendar"""
        
        headers = {"Authorization": f"Bearer {self.access_token}"}
        
        if calendar_id:
            url = f"{self.base_url}/me/calendars/{calendar_id}/events"
        else:
            url = f"{self.base_url}/me/calendar/events"
        
        params = {
            "$top": 100,
            "$orderby": "start/dateTime"
        }
        
        response = requests.get(url, headers=headers, params=params)
        return response.json().get('value', [])
```

---

## Sync Architecture

### Sync Service
```python
from enum import Enum

class SyncDirection(str, Enum):
    TO_CALENDAR = "to_calendar"
    FROM_CALENDAR = "from_calendar"
    BIDIRECTIONAL = "bidirectional"

class CalendarSyncService:
    def __init__(self, user_id: UUID):
        self.user_id = user_id
        self.integrations = self._load_integrations()
    
    async def sync_all(self):
        """Sync all enabled calendar integrations"""
        
        for integration in self.integrations:
            if not integration.enabled:
                continue
            
            try:
                if integration.sync_direction in [
                    SyncDirection.TO_CALENDAR,
                    SyncDirection.BIDIRECTIONAL
                ]:
                    await self._push_to_calendar(integration)
                
                if integration.sync_direction in [
                    SyncDirection.FROM_CALENDAR,
                    SyncDirection.BIDIRECTIONAL
                ]:
                    await self._pull_from_calendar(integration)
                
                integration.last_sync_at = datetime.now()
                integration.sync_status = "success"
                await db.save(integration)
            
            except Exception as e:
                logger.error(f"Sync failed for {integration.id}: {e}")
                integration.sync_status = "error"
                integration.error_log = str(e)
                await db.save(integration)
```

### Push to Calendar (Workmate → External)
```python
async def _push_to_calendar(self, integration: Integration):
    """Push Workmate tasks/events to external calendar"""
    
    # Get all calendar events that need syncing
    events = await db.query(CalendarEvent).filter(
        CalendarEvent.user_id == self.user_id,
        CalendarEvent.sync_status.in_(['pending', 'conflict']),
        or_(
            CalendarEvent.external_calendar_id == integration.id,
            CalendarEvent.external_calendar_id.is_(None)
        )
    ).all()
    
    calendar_client = self._get_calendar_client(integration)
    
    for event in events:
        try:
            if event.external_event_id:
                # Update existing event
                await calendar_client.update_event(
                    event.external_event_id,
                    title=event.title,
                    start=event.start_time,
                    end=event.end_time,
                    description=event.description
                )
            else:
                # Create new event
                external_id = await calendar_client.create_event(
                    calendar_id=integration.config.get('calendar_id', 'primary'),
                    title=event.title,
                    start=event.start_time,
                    end=event.end_time,
                    description=event.description
                )
                
                event.external_event_id = external_id
                event.external_calendar_id = integration.id
            
            event.sync_status = CalendarSyncStatus.SYNCED
            event.last_synced_at = datetime.now()
            await db.save(event)
        
        except Exception as e:
            logger.error(f"Failed to push event {event.id}: {e}")
            event.sync_status = CalendarSyncStatus.FAILED
            await db.save(event)
```

### Pull from Calendar (External → Workmate)
```python
async def _pull_from_calendar(self, integration: Integration):
    """Pull events from external calendar to Workmate"""
    
    calendar_client = self._get_calendar_client(integration)
    
    # Fetch events from calendar
    external_events = await calendar_client.sync_from_calendar(
        calendar_id=integration.config.get('calendar_id', 'primary')
    )
    
    for ext_event in external_events:
        # Check if event already exists
        existing = await db.query(CalendarEvent).filter(
            CalendarEvent.user_id == self.user_id,
            CalendarEvent.external_event_id == ext_event['id']
        ).first()
        
        if existing:
            # Check for conflicts
            if self._has_conflict(existing, ext_event):
                await self._handle_conflict(existing, ext_event)
            else:
                # Update existing
                existing.title = ext_event['title']
                existing.start_time = ext_event['start']
                existing.end_time = ext_event['end']
                existing.description = ext_event.get('description')
                existing.last_synced_at = datetime.now()
                await db.save(existing)
        
        else:
            # Create new event
            new_event = CalendarEvent(
                user_id=self.user_id,
                title=ext_event['title'],
                start_time=ext_event['start'],
                end_time=ext_event['end'],
                description=ext_event.get('description'),
                external_event_id=ext_event['id'],
                external_calendar_id=integration.id,
                sync_status=CalendarSyncStatus.SYNCED,
                last_synced_at=datetime.now()
            )
            await db.save(new_event)
```

---

## Conflict Resolution

### Conflict Detection
```python
def _has_conflict(
    self,
    local_event: CalendarEvent,
    remote_event: dict
) -> bool:
    """Check if local and remote versions conflict"""
    
    # Both modified since last sync
    local_modified = local_event.updated_at > local_event.last_synced_at
    remote_modified = self._parse_remote_modified_time(remote_event) > local_event.last_synced_at
    
    if not (local_modified and remote_modified):
        return False
    
    # Check if actual data differs
    if (
        local_event.title != remote_event['title'] or
        local_event.start_time != remote_event['start'] or
        local_event.end_time != remote_event['end']
    ):
        return True
    
    return False
```

### Conflict Resolution Strategies
```python
from enum import Enum

class ConflictResolution(str, Enum):
    KEEP_LOCAL = "keep_local"
    KEEP_REMOTE = "keep_remote"
    MANUAL = "manual"

async def _handle_conflict(
    self,
    local_event: CalendarEvent,
    remote_event: dict
):
    """Handle sync conflict"""
    
    # Store both versions
    local_event.conflict_data = {
        "local": {
            "title": local_event.title,
            "start": local_event.start_time.isoformat(),
            "end": local_event.end_time.isoformat(),
            "description": local_event.description,
            "updated_at": local_event.updated_at.isoformat()
        },
        "remote": {
            "title": remote_event['title'],
            "start": remote_event['start'],
            "end": remote_event['end'],
            "description": remote_event.get('description'),
            "updated_at": remote_event.get('updated_at')
        }
    }
    
    local_event.sync_status = CalendarSyncStatus.CONFLICT
    await db.save(local_event)
    
    # Notify user
    await notification_service.send(
        user_id=self.user_id,
        title="Kalender-Konflikt",
        body=f"Event '{local_event.title}' wurde gleichzeitig in Workmate und {integration.name} geändert.",
        action_url=f"/calendar/conflicts/{local_event.id}"
    )

async def resolve_conflict(
    self,
    event_id: UUID,
    resolution: ConflictResolution
):
    """Resolve a conflict based on user choice"""
    
    event = await db.get_calendar_event(event_id)
    
    if resolution == ConflictResolution.KEEP_LOCAL:
        # Push local version to calendar
        await self._push_event_to_calendar(event)
    
    elif resolution == ConflictResolution.KEEP_REMOTE:
        # Update local with remote version
        remote = event.conflict_data['remote']
        event.title = remote['title']
        event.start_time = datetime.fromisoformat(remote['start'])
        event.end_time = datetime.fromisoformat(remote['end'])
        event.description = remote.get('description')
    
    # Clear conflict
    event.sync_status = CalendarSyncStatus.SYNCED
    event.conflict_data = None
    event.last_synced_at = datetime.now()
    await db.save(event)
```

---

## Real-Time Sync (Webhooks)

### Google Calendar Webhooks
```python
@app.post("/webhooks/google-calendar")
async def google_calendar_webhook(
    request: Request,
    x_goog_channel_id: str = Header(...),
    x_goog_resource_state: str = Header(...)
):
    """Handle Google Calendar push notifications"""
    
    if x_goog_resource_state == "sync":
        # Initial sync, ignore
        return {"status": "ok"}
    
    # Parse channel ID to get user
    user_id = await _get_user_from_channel_id(x_goog_channel_id)
    
    # Trigger sync
    await calendar_sync_service.sync_user(user_id)
    
    return {"status": "synced"}
```

### Outlook Subscriptions
```python
@app.post("/webhooks/outlook-calendar")
async def outlook_calendar_webhook(
    request: Request,
    validation_token: str = Query(None)
):
    """Handle Outlook Calendar subscriptions"""
    
    # Validation request
    if validation_token:
        return PlainTextResponse(validation_token)
    
    # Notification
    data = await request.json()
    
    for notification in data.get('value', []):
        user_id = notification['subscriptionId']
        
        # Trigger sync
        await calendar_sync_service.sync_user(user_id)
    
    return {"status": "ok"}
```

---

## Task → Event Mapping

### Automatic Event Creation
```python
class TaskToEventMapper:
    async def create_event_from_task(self, task: Task) -> CalendarEvent:
        """Create calendar event from task"""
        
        # Determine event time
        if task.due_date:
            # All-day event if no specific time
            if task.due_date.hour == 0 and task.due_date.minute == 0:
                start = task.due_date.replace(hour=0, minute=0)
                end = task.due_date.replace(hour=23, minute=59)
                all_day = True
            else:
                # Estimate duration (default 1 hour)
                duration = timedelta(hours=1)
                if task.estimated_duration_minutes:
                    duration = timedelta(minutes=task.estimated_duration_minutes)
                
                start = task.due_date - duration
                end = task.due_date
                all_day = False
        else:
            # No deadline, skip
            return None
        
        # Create event
        event = CalendarEvent(
            user_id=task.user_id,
            task_id=task.id,
            title=task.title,
            description=task.description,
            start_time=start,
            end_time=end,
            all_day=all_day,
            sync_status=CalendarSyncStatus.PENDING
        )
        
        await db.save(event)
        
        # Trigger sync
        await calendar_sync_service.push_event(event.id)
        
        return event
```

---

## UI/UX

### Calendar Selection
```dart
// Flutter UI for calendar selection
class CalendarIntegrationSetup extends StatefulWidget {
  @override
  _CalendarIntegrationSetupState createState() => _CalendarIntegrationSetupState();
}

class _CalendarIntegrationSetupState extends State<CalendarIntegrationSetup> {
  String selectedType = 'caldav';
  
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Kalender verbinden')),
      body: ListView(
        children: [
          ListTile(
            leading: Icon(Icons.cloud),
            title: Text('CalDAV (Nextcloud, Apple, etc.)'),
            trailing: Radio(
              value: 'caldav',
              groupValue: selectedType,
              onChanged: (value) => setState(() => selectedType = value),
            ),
          ),
          ListTile(
            leading: Icon(Icons.g_mobiledata),
            title: Text('Google Calendar'),
            trailing: Radio(
              value: 'google',
              groupValue: selectedType,
              onChanged: (value) => setState(() => selectedType = value),
            ),
          ),
          ListTile(
            leading: Icon(Icons.microsoft),
            title: Text('Microsoft Outlook'),
            trailing: Radio(
              value: 'outlook',
              groupValue: selectedType,
              onChanged: (value) => setState(() => selectedType = value),
            ),
          ),
          Padding(
            padding: EdgeInsets.all(16),
            child: ElevatedButton(
              onPressed: _connectCalendar,
              child: Text('Verbinden'),
            ),
          ),
        ],
      ),
    );
  }
  
  Future<void> _connectCalendar() async {
    if (selectedType == 'caldav') {
      _showCalDAVSetup();
    } else if (selectedType == 'google') {
      await _connectGoogleCalendar();
    } else if (selectedType == 'outlook') {
      await _connectOutlookCalendar();
    }
  }
}
```

---

## Performance Optimization

### Incremental Sync
```python
async def incremental_sync(self, integration: Integration):
    """Only sync events modified since last sync"""
    
    last_sync = integration.last_sync_at or (datetime.now() - timedelta(days=365))
    
    calendar_client = self._get_calendar_client(integration)
    
    # Only fetch events modified since last sync
    if isinstance(calendar_client, GoogleCalendarIntegration):
        events = await calendar_client.sync_from_calendar(
            updated_min=last_sync.isoformat()
        )
    else:
        # CalDAV doesn't support incremental, fall back to full sync
        events = await calendar_client.sync_from_calendar()
```

### Batch Operations
```python
async def batch_push_events(
    self,
    integration: Integration,
    events: List[CalendarEvent]
):
    """Push multiple events in batch"""
    
    calendar_client = self._get_calendar_client(integration)
    
    # Chunk into batches of 50
    chunk_size = 50
    for i in range(0, len(events), chunk_size):
        chunk = events[i:i + chunk_size]
        
        tasks = [
            calendar_client.create_event(
                calendar_id=integration.config.get('calendar_id'),
                title=event.title,
                start=event.start_time,
                end=event.end_time,
                description=event.description
            )
            for event in chunk
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        for event, result in zip(chunk, results):
            if isinstance(result, Exception):
                logger.error(f"Failed to create event {event.id}: {result}")
            else:
                event.external_event_id = result
                event.sync_status = CalendarSyncStatus.SYNCED
                await db.save(event)
```

---

## Testing
```python
@pytest.mark.asyncio
async def test_caldav_integration():
    integration = CalDAVIntegration(
        url="http://localhost:5232",
        username="test",
        password="test"
    )
    
    # Create event
    external_id = await integration.create_event(
        calendar_name="Test Calendar",
        title="Test Event",
        start=datetime.now(),
        end=datetime.now() + timedelta(hours=1)
    )
    
    assert external_id is not None
    
    # Fetch events
    events = await integration.sync_from_calendar("Test Calendar")
    assert len(events) > 0
    assert any(e['title'] == "Test Event" for e in events)
```

---

## Zusammenfassung

**Calendar Integration Features:**
- ✅ CalDAV, Google, Outlook Support
- ✅ Two-Way Sync
- ✅ Conflict Resolution
- ✅ Real-Time Webhooks
- ✅ Task → Event Mapping
- ✅ Incremental Sync
- ✅ Batch Operations

**ADHD-Benefit:**
- Automatische Kalender-Einträge
- Keine manuelle Duplikation
- Zentrale Übersicht
- Flexibel (nutze deinen Lieblings-Kalender)