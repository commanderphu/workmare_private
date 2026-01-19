# Components

## Overview

Workmate Private besteht aus 12 Kern-Komponenten, die modular aufgebaut sind und über definierte Schnittstellen miteinander kommunizieren. Jede Komponente hat eine klar definierte Verantwortung.
```
┌─────────────────────────────────────────────────────────────┐
│                    FRONTEND (Flutter)                        │
└────────────────────────┬────────────────────────────────────┘
                         │ REST API
┌────────────────────────▼────────────────────────────────────┐
│                    API GATEWAY (FastAPI)                     │
└─────────┬──────────────────────────────────────────┬────────┘
          │                                           │
    ┌─────▼─────┐                               ┌────▼────┐
    │ Document  │                               │  Auth   │
    │ Processor │                               │ Service │
    └─────┬─────┘                               └─────────┘
          │
    ┌─────▼─────┐     ┌──────────┐     ┌──────────────┐
    │   Task    │────▶│ Reminder │────▶│Notification  │
    │  Engine   │     │  Engine  │     │  Channels    │
    └─────┬─────┘     └──────────┘     └──────────────┘
          │
    ┌─────▼─────┐     ┌──────────┐     ┌──────────────┐
    │    SLA    │     │ Calendar │     │ Integration  │
    │  Monitor  │     │   Sync   │     │   Manager    │
    └───────────┘     └──────────┘     └──────────────┘
          │
    ┌─────▼─────┐     ┌──────────┐     ┌──────────────┐
    │   File    │     │Background│     │   Search &   │
    │  Storage  │     │   Jobs   │     │    Filter    │
    └───────────┘     └──────────┘     └──────────────┘
          │
    ┌─────▼─────┐
    │ Analytics │
    │& Insights │
    └───────────┘
```

---

## 1. Document Processor

### Verantwortung
Verarbeitet hochgeladene Dokumente durch eine vollständige Pipeline: Upload → OCR/Vision → KI-Analyse → Metadaten-Extraktion → Automatische Task-Erstellung.

### Features
- **Multi-Input Support:**
  - Foto von Smartphone-Kamera
  - Scanner-Upload (PDF/Image)
  - Email-Anhänge (Auto-Import)
  
- **OCR & Vision:**
  - Claude Vision API (primär)
  - Tesseract OCR (Fallback)
  - Multi-Language Support (DE, EN)
  
- **KI-Analyse:**
  - Dokumenten-Typ Erkennung (Rechnung, Mahnung, Vertrag, etc.)
  - Entitäten-Extraktion:
    - Beträge (€, $, etc.)
    - Daten (Fristen, Lieferdaten)
    - Empfänger/Absender
    - Rechnungsnummern
    - Vertragslaufzeiten
  
- **Auto-Task Creation:**
  - Erstellt Tasks basierend auf Dokumenten-Typ
  - Setzt Deadlines automatisch
  - Berechnet initiale Priorität

### Schnittstellen

**Input:**
```python
POST /api/v1/documents/upload
Content-Type: multipart/form-data

{
  "file": <binary>,
  "source": "camera|scanner|email",
  "metadata": {
    "user_id": "uuid",
    "timestamp": "ISO8601"
  }
}
```

**Output:**
```python
{
  "document_id": "uuid",
  "type": "invoice|reminder|contract|receipt|other",
  "extracted_data": {
    "amount": 89.99,
    "currency": "EUR",
    "due_date": "2026-01-25",
    "sender": "Telekom Deutschland GmbH",
    "invoice_number": "12345678"
  },
  "created_tasks": ["task_uuid_1", "task_uuid_2"],
  "confidence_score": 0.95
}
```

### Technische Details

**Processing Pipeline:**
```python
class DocumentProcessor:
    async def process(self, file: UploadFile) -> ProcessedDocument:
        # 1. File Upload & Validation
        doc = await self.storage.save(file)
        
        # 2. OCR/Vision
        text = await self.vision_service.extract_text(doc)
        
        # 3. AI Analysis
        analysis = await self.ai_service.analyze_document(text)
        
        # 4. Task Creation
        tasks = await self.task_engine.create_from_document(analysis)
        
        # 5. Save Metadata
        await self.db.save_document_metadata(doc, analysis)
        
        return ProcessedDocument(doc, analysis, tasks)
```

**Dependencies:**
- File Storage Service
- AI Engine (Claude/Ollama)
- Task Engine
- Database

---

## 2. Task Engine

### Verantwortung
Verwaltet alle Tasks im System: Erstellung, Updates, Dependencies, Recurring Tasks, Sub-Tasks und Status-Management.

### Features

- **CRUD Operations:**
  - Create, Read, Update, Delete Tasks
  - Bulk Operations
  
- **Task Properties:**
  - Title, Description
  - Due Date, Priority (Low/Medium/High/Critical)
  - Status (Open, In Progress, Done, Cancelled)
  - Tags & Categories
  
- **Advanced Features:**
  - **Dependencies:** Task B startet erst wenn Task A erledigt
  - **Recurring Tasks:** Täglich, Wöchlich, Monatlich, Jährlich
  - **Sub-Tasks:** Große Tasks in kleine Schritte aufteilen
  - **Templates:** Standard-Tasks für wiederkehrende Szenarien

### Schnittstellen

**Create Task:**
```python
POST /api/v1/tasks
{
  "title": "Telekom Rechnung bezahlen",
  "description": "Rechnung vom 10.01.2026, 89.99€",
  "due_date": "2026-01-25T23:59:59Z",
  "priority": "medium",
  "document_id": "doc_uuid",
  "tags": ["rechnung", "telekom"],
  "dependencies": ["task_uuid_check_account"],
  "recurrence": null,
  "parent_task_id": null
}
```

**Response:**
```python
{
  "task_id": "uuid",
  "created_at": "ISO8601",
  "next_reminder": "2026-01-18T09:00:00Z"
}
```

### Technische Details

**Task Model:**
```python
class Task:
    id: UUID
    user_id: UUID
    title: str
    description: Optional[str]
    due_date: datetime
    priority: Priority  # Enum: Low, Medium, High, Critical
    status: Status  # Enum: Open, InProgress, Done, Cancelled
    document_id: Optional[UUID]
    tags: List[str]
    dependencies: List[UUID]  # Parent tasks that must be done first
    recurrence_rule: Optional[RecurrenceRule]
    parent_task_id: Optional[UUID]  # For sub-tasks
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime]
```

**Dependency Resolution:**
```python
async def can_start_task(task_id: UUID) -> bool:
    task = await db.get_task(task_id)
    if not task.dependencies:
        return True
    
    for dep_id in task.dependencies:
        dep = await db.get_task(dep_id)
        if dep.status != Status.Done:
            return False
    return True
```

**Dependencies:**
- Database
- Reminder Engine (für Scheduling)
- Calendar Sync (für Events)

---

## 3. Reminder Engine

### Verantwortung
Erstellt und verwaltet Reminders mit dynamischer Eskalation. Je näher die Deadline, desto häufiger und dringender die Erinnerungen.

### Features

- **Multi-Stage Reminders:**
  - 7 Tage vorher: Info-Reminder (einmalig)
  - 2 Tage vorher: Warnung (täglich)
  - 1 Tag vorher: Dringend (mehrmals täglich)
  - Überfällig: Kritisch (stündlich)
  
- **Dynamic Escalation:**
  - Priorität steigt automatisch mit Zeit
  - Frequenz erhöht sich
  - Notification-Channels eskalieren (Push → Email → SMS → Smart Home)
  
- **Smart Scheduling:**
  - Keine Reminders nachts (22:00-07:00)
  - Berücksichtigt User-Timezone
  - Optional: User-definierte Quiet Hours

### Schnittstellen

**Create Reminder:**
```python
POST /api/v1/reminders
{
  "task_id": "uuid",
  "stages": [
    {"days_before": 7, "severity": "info"},
    {"days_before": 2, "severity": "warning"},
    {"days_before": 1, "severity": "urgent"}
  ],
  "channels": ["push", "email"]
}
```

**Reminder Schedule:**
```python
{
  "reminder_id": "uuid",
  "next_trigger": "2026-01-18T09:00:00Z",
  "stage": "warning",
  "channels": ["push", "email"]
}
```

### Technische Details

**Escalation Logic:**
```python
class ReminderEngine:
    def calculate_schedule(self, task: Task) -> List[ReminderEvent]:
        now = datetime.now()
        due = task.due_date
        delta = (due - now).days
        
        events = []
        
        if delta >= 7:
            events.append(ReminderEvent(
                trigger_at=due - timedelta(days=7),
                severity="info",
                channels=["push"]
            ))
        
        if delta >= 2:
            # Daily reminders 2 days before
            for i in range(2):
                events.append(ReminderEvent(
                    trigger_at=due - timedelta(days=2-i),
                    severity="warning",
                    channels=["push", "email"]
                ))
        
        if delta >= 1:
            # Multiple reminders on last day
            for hour in [9, 13, 17, 20]:
                events.append(ReminderEvent(
                    trigger_at=due.replace(hour=hour, minute=0),
                    severity="urgent",
                    channels=["push", "email", "sms"]
                ))
        
        if delta < 0:
            # Overdue - hourly reminders
            events.append(ReminderEvent(
                trigger_at=now + timedelta(hours=1),
                severity="critical",
                channels=["push", "email", "sms", "smart_home"]
            ))
        
        return events
```

**Dependencies:**
- Task Engine
- Notification Channels
- Background Job Processor (für Scheduling)

---

## 4. Notification Channels

### Verantwortung
Versendet Benachrichtigungen über verschiedene Kanäle: Push, Email, SMS, Smart Home und Messaging-Apps.

### Features

**Channels:**
- 📱 **Push Notifications** (Flutter Local Notifications)
- 📧 **Email** (SMTP)
- 💬 **SMS** (Twilio / optional)
- 🏠 **Smart Home** (Home Assistant, MQTT)
- 💬 **Messaging Apps:**
  - Telegram
  - WhatsApp (via API)
  - Discord
  - Signal

**Channel Selection:**
- User kann Channels pro Task konfigurieren
- Default: Push + Email
- Kritische Tasks: Alle Channels
- Quiet Hours: Nur kritische über SMS/Smart Home

### Schnittstellen

**Send Notification:**
```python
POST /api/v1/notifications/send
{
  "user_id": "uuid",
  "task_id": "uuid",
  "message": {
    "title": "Rechnung fällig!",
    "body": "Telekom Rechnung (89.99€) fällig in 2 Tagen",
    "action_url": "/tasks/uuid"
  },
  "channels": ["push", "email", "telegram"],
  "severity": "warning"
}
```

### Technische Details

**Channel Implementations:**
```python
class NotificationService:
    def __init__(self):
        self.channels = {
            "push": PushNotificationChannel(),
            "email": EmailChannel(),
            "sms": SMSChannel(),
            "telegram": TelegramChannel(),
            "smart_home": SmartHomeChannel()
        }
    
    async def send(self, notification: Notification):
        tasks = []
        for channel_name in notification.channels:
            channel = self.channels[channel_name]
            tasks.append(channel.send(notification))
        
        await asyncio.gather(*tasks, return_exceptions=True)
```

**Push Notifications (Flutter):**
```dart
// Client-Side
final FlutterLocalNotificationsPlugin notifications = 
    FlutterLocalNotificationsPlugin();

await notifications.show(
  0,
  'Rechnung fällig!',
  'Telekom Rechnung (89.99€) fällig in 2 Tagen',
  NotificationDetails(...)
);
```

**Email (Python):**
```python
import smtplib
from email.mime.text import MIMEText

async def send_email(to: str, subject: str, body: str):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = settings.EMAIL_FROM
    msg['To'] = to
    
    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
        server.starttls()
        server.login(settings.SMTP_USER, settings.SMTP_PASS)
        server.send_message(msg)
```

**Telegram:**
```python
from telegram import Bot

bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
await bot.send_message(
    chat_id=user.telegram_chat_id,
    text="🔔 Rechnung fällig!\n\nTelekom: 89.99€ in 2 Tagen"
)
```

**Smart Home (Home Assistant):**
```python
import aiohttp

async def trigger_home_assistant(entity_id: str, action: str):
    url = f"{settings.HA_URL}/api/services/light/{action}"
    headers = {"Authorization": f"Bearer {settings.HA_TOKEN}"}
    data = {"entity_id": entity_id}
    
    async with aiohttp.ClientSession() as session:
        await session.post(url, json=data, headers=headers)

# Example: Flash lights red
await trigger_home_assistant("light.office", "turn_on")
await asyncio.sleep(1)
await trigger_home_assistant("light.office", "turn_off")
```

**Dependencies:**
- Reminder Engine
- User Settings (Channel Preferences)
- External APIs (Twilio, Telegram, etc.)

---

## 5. SLA Monitor

### Verantwortung
Überwacht Fristen und berechnet dynamische Prioritäten basierend auf Zeit, Wichtigkeit und Betrag.

### Features

- **Priority Scoring:**
  - Zeit bis Deadline (je näher, desto höher)
  - Dokumenten-Typ (Mahnung > Rechnung > Info)
  - Betrag (höher = wichtiger)
  - User-Override möglich
  
- **Status Tracking:**
  - OK: > 7 Tage
  - Warning: 2-7 Tage
  - Urgent: < 2 Tage
  - Critical: < 24h oder überfällig

### Priority Algorithm
```python
class SLAMonitor:
    def calculate_priority(self, task: Task) -> Priority:
        now = datetime.now()
        delta = (task.due_date - now).total_seconds()
        days_left = delta / 86400  # seconds to days
        
        # Base score from time
        if days_left < 0:
            time_score = 100  # Overdue
        elif days_left < 1:
            time_score = 80
        elif days_left < 2:
            time_score = 60
        elif days_left < 7:
            time_score = 40
        else:
            time_score = 20
        
        # Type multiplier
        type_multiplier = {
            "reminder": 1.5,  # Mahnung
            "invoice": 1.2,
            "contract": 1.3,
            "receipt": 1.0,
            "other": 1.0
        }.get(task.document_type, 1.0)
        
        # Amount factor (if available)
        amount_factor = 1.0
        if task.amount:
            if task.amount > 500:
                amount_factor = 1.3
            elif task.amount > 100:
                amount_factor = 1.1
        
        # Final score
        score = time_score * type_multiplier * amount_factor
        
        # Map to priority
        if score >= 80:
            return Priority.CRITICAL
        elif score >= 60:
            return Priority.HIGH
        elif score >= 40:
            return Priority.MEDIUM
        else:
            return Priority.LOW
```

### Schnittstellen
```python
GET /api/v1/tasks/critical
Response: [
  {
    "task_id": "uuid",
    "title": "Telekom Rechnung",
    "priority": "critical",
    "sla_status": "overdue",
    "days_overdue": 2
  }
]
```

**Dependencies:**
- Task Engine
- Reminder Engine (triggers escalation)

---

## 6. Calendar Sync Service

### Verantwortung
Two-Way Synchronisation zwischen Workmate und externen Kalendern mit Konflikt-Erkennung.

### Features

- **Supported Protocols:**
  - CalDAV (Nextcloud, Apple Calendar, etc.)
  - Google Calendar API
  - Microsoft Graph API (Outlook)
  
- **Sync Modes:**
  - **One-Time:** Manual Sync on-demand
  - **Periodic:** Auto-Sync every X minutes
  - **Real-Time:** Webhooks (Google/Outlook)
  
- **Conflict Resolution:**
  - User-Entscheidung bei Konflikten
  - Last-Write-Wins (optional)
  - Manual Merge

### Technische Details

**Sync Logic:**
```python
class CalendarSyncService:
    async def sync(self, user_id: UUID):
        local_events = await self.db.get_calendar_events(user_id)
        remote_events = await self.calendar_api.get_events(user_id)
        
        # Detect changes
        conflicts = []
        to_push = []
        to_pull = []
        
        for event in local_events:
            remote = remote_events.get(event.external_id)
            if not remote:
                to_push.append(event)  # New local event
            elif event.updated_at > remote.updated_at:
                if remote.updated_at > event.last_synced:
                    conflicts.append((event, remote))  # Conflict!
                else:
                    to_push.append(event)  # Local change
            elif remote.updated_at > event.last_synced:
                to_pull.append(remote)  # Remote change
        
        # Apply changes
        await self.push_events(to_push)
        await self.pull_events(to_pull)
        
        # Handle conflicts
        if conflicts:
            await self.notify_conflicts(user_id, conflicts)
```

**CalDAV Integration:**
```python
import caldav

client = caldav.DAVClient(
    url=user.caldav_url,
    username=user.caldav_user,
    password=user.caldav_pass
)
calendar = client.principal().calendars()[0]

# Add event
event = calendar.save_event(
    dtstart=task.due_date,
    summary=task.title,
    description=task.description
)
```

**Dependencies:**
- Task Engine
- External Calendar APIs
- Background Job Processor (für Periodic Sync)

---

## 7. Integration Manager

### Verantwortung
Verwaltet externe Integrationen als Plugins mit UI zur Aktivierung/Deaktivierung.

### Features

- **Plugin Architecture:**
  - Jede Integration ist ein Plugin
  - Enable/Disable in Settings
  - Config per Integration
  
- **Available Integrations:**
  - Paperless-ngx (Document Management)
  - Home Assistant (Smart Home)
  - MQTT (IoT Devices)
  - Email (IMAP/SMTP)
  - Tracking APIs (DHL, DPD, Hermes)
  - Banking APIs (FinAPI - optional)

### Plugin Interface
```python
class IntegrationPlugin:
    name: str
    description: str
    config_schema: dict  # JSON Schema for config
    
    async def initialize(self, config: dict) -> bool:
        """Initialize plugin with user config"""
        pass
    
    async def sync(self, user_id: UUID):
        """Sync data with external service"""
        pass
    
    async def test_connection(self) -> bool:
        """Test if credentials work"""
        pass
```

**Example: Paperless-ngx Plugin:**
```python
class PaperlessPlugin(IntegrationPlugin):
    name = "Paperless-ngx"
    description = "Sync documents with Paperless-ngx"
    config_schema = {
        "url": {"type": "string", "format": "uri"},
        "api_token": {"type": "string"}
    }
    
    async def sync(self, user_id: UUID):
        # Fetch documents from Paperless
        docs = await self.paperless_api.get_documents()
        
        # Import to Workmate
        for doc in docs:
            await document_processor.process_external(doc)
```

### Schnittstellen

**List Integrations:**
```python
GET /api/v1/integrations
Response: [
  {
    "id": "paperless",
    "name": "Paperless-ngx",
    "enabled": true,
    "config": {
      "url": "https://paperless.local",
      "last_sync": "2026-01-19T10:00:00Z"
    }
  }
]
```

**Enable Integration:**
```python
POST /api/v1/integrations/paperless/enable
{
  "url": "https://paperless.local",
  "api_token": "xxx"
}
```

**Dependencies:**
- External APIs
- Background Job Processor (für Auto-Sync)

---

## 8. Auth Service

### Verantwortung
Vollständiges Authentication & Authorization System mit Session-Management und Device-Tracking.

### Features

- **Authentication Methods:**
  - Username/Password + JWT
  - OAuth2 (Google, GitHub, Microsoft)
  - 2FA (TOTP)
  
- **Session Management:**
  - Multiple Sessions per User
  - Device Tracking (Browser, OS, Location)
  - Session Revoke (einzeln oder alle)
  
- **Security:**
  - Password Hashing (bcrypt)
  - Rate Limiting (Login-Attempts)
  - Suspicious Activity Detection

### Technische Details

**Registration:**
```python
POST /api/v1/auth/register
{
  "username": "joshua",
  "email": "joshua@example.com",
  "password": "SecurePass123!"
}

Response:
{
  "user_id": "uuid",
  "access_token": "jwt...",
  "refresh_token": "jwt..."
}
```

**Login with Device Tracking:**
```python
POST /api/v1/auth/login
{
  "username": "joshua",
  "password": "SecurePass123!",
  "device_info": {
    "type": "android",
    "name": "Samsung Galaxy S23",
    "os": "Android 14",
    "ip": "192.168.1.100"
  }
}

Response:
{
  "access_token": "jwt...",
  "refresh_token": "jwt...",
  "session_id": "uuid",
  "requires_2fa": false
}
```

**2FA Flow:**
```python
# Enable 2FA
POST /api/v1/auth/2fa/enable
Response:
{
  "secret": "BASE32SECRET",
  "qr_code": "data:image/png;base64,..."
}

# Verify 2FA Code
POST /api/v1/auth/2fa/verify
{
  "code": "123456"
}
```

**Session Management:**
```python
GET /api/v1/auth/sessions
Response: [
  {
    "session_id": "uuid",
    "device": "Samsung Galaxy S23",
    "os": "Android 14",
    "location": "Koblenz, DE",
    "last_active": "2026-01-19T10:30:00Z",
    "current": true
  }
]

DELETE /api/v1/auth/sessions/{session_id}
```

**Dependencies:**
- Database
- Redis (für Session Storage)
- Email Service (für Verification)

---

## 9. File Storage Service

### Verantwortung
Speichert Dokumente strukturiert in User-Ordnern mit Kategorien.

### Features

- **Structure:**
```
  /uploads/
    /{user_id}/
      /invoices/
      /contracts/
      /receipts/
      /other/
```
  
- **File Operations:**
  - Upload, Download, Delete
  - Metadata Tracking
  - File Type Validation
  - Size Limits
  
- **Storage Backends:**
  - Local Filesystem (Self-Hosted)
  - S3 / MinIO (Cloud)

### Technische Details
```python
class FileStorageService:
    def __init__(self, backend: StorageBackend):
        self.backend = backend
    
    async def save(
        self,
        file: UploadFile,
        user_id: UUID,
        category: str
    ) -> StoredFile:
        # Generate path
        file_id = uuid4()
        ext = Path(file.filename).suffix
        path = f"{user_id}/{category}/{file_id}{ext}"
        
        # Save file
        await self.backend.save(path, file.file)
        
        # Save metadata
        stored_file = StoredFile(
            id=file_id,
            user_id=user_id,
            path=path,
            filename=file.filename,
            size=file.size,
            mime_type=file.content_type,
            category=category,
            created_at=datetime.now()
        )
        await db.save(stored_file)
        
        return stored_file
```

**Local Backend:**
```python
class LocalStorageBackend:
    def __init__(self, base_path: Path):
        self.base_path = base_path
    
    async def save(self, path: str, file: BinaryIO):
        full_path = self.base_path / path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        async with aiofiles.open(full_path, 'wb') as f:
            await f.write(await file.read())
```

**S3 Backend:**
```python
class S3StorageBackend:
    def __init__(self, bucket: str):
        self.s3 = boto3.client('s3')
        self.bucket = bucket
    
    async def save(self, path: str, file: BinaryIO):
        self.s3.upload_fileobj(file, self.bucket, path)
```

**Dependencies:**
- Database (für Metadata)
- boto3 (für S3)

---

## 10. Background Job Processor

### Verantwortung
Verarbeitet asynchrone Tasks mit Retry-Logic und Queue-Management.

### Features

- **Job Types:**
  - Document Processing
  - Reminder Checks
  - Calendar Sync
  - Email Sending
  - Cleanup Jobs
  
- **Retry Logic:**
  - Exponential Backoff
  - Max Retries konfigurierbar
  - Dead Letter Queue für failed jobs
  
- **Scheduling:**
  - One-Time Jobs
  - Recurring Jobs (Cron-like)
  - Delayed Jobs

### Technische Details

**Celery Setup:**
```python
from celery import Celery

app = Celery(
    'workmate',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/1'
)

app.conf.update(
    task_serializer='json',
    result_serializer='json',
    accept_content=['json'],
    timezone='Europe/Berlin',
    enable_utc=True,
)
```

**Task Definition:**
```python
@app.task(bind=True, max_retries=3)
async def process_document(self, document_id: str):
    try:
        doc = await db.get_document(document_id)
        result = await document_processor.process(doc)
        return result
    except Exception as exc:
        # Retry with exponential backoff
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))
```

**Periodic Tasks:**
```python
from celery.schedules import crontab

app.conf.beat_schedule = {
    'check-reminders': {
        'task': 'workmate.tasks.check_reminders',
        'schedule': crontab(minute='*/5'),  # Every 5 minutes
    },
    'sync-calendars': {
        'task': 'workmate.tasks.sync_calendars',
        'schedule': crontab(minute='*/15'),  # Every 15 minutes
    },
    'cleanup-temp-files': {
        'task': 'workmate.tasks.cleanup',
        'schedule': crontab(hour=3, minute=0),  # Daily at 3 AM
    },
}
```

**Dependencies:**
- Redis (Message Broker)
- All other components (als Worker)

---

## 11. Search & Filter Engine

### Verantwortung
Ermöglicht Volltextsuche in Dokumenten/Tasks mit Fuzzy-Matching und Smart Filters.

### Features

- **Search Modes:**
  - Simple: Titel/Beschreibung
  - Full-Text: Dokumenten-Content
  - Fuzzy: Tippfehler-tolerant
  
- **Filters:**
  - Status (Open, Done, etc.)
  - Priority
  - Date Ranges
  - Tags/Categories
  - Amount Ranges
  
- **Smart Filters:**
  - "Überfällige Rechnungen >50€"
  - "Offene Tasks diese Woche"
  - "Verträge mit Kündigungsfrist <3 Monate"

### Technische Details

**PostgreSQL Full-Text Search:**
```python
from sqlalchemy import func

# Create search vector
Task.__table__.append_column(
    Column('search_vector', TSVectorType('title', 'description'))
)

# Search
query = (
    session.query(Task)
    .filter(Task.search_vector.match('telekom rechnung'))
    .order_by(Task.created_at.desc())
)
```

**Fuzzy Search (Levenshtein Distance):**
```python
from fuzzywuzzy import fuzz

def fuzzy_search(query: str, items: List[str], threshold: int = 80):
    results = []
    for item in items:
        score = fuzz.ratio(query.lower(), item.lower())
        if score >= threshold:
            results.append((item, score))
    return sorted(results, key=lambda x: x[1], reverse=True)
```

**Smart Filters:**
```python
class SmartFilter:
    @staticmethod
    def overdue_high_amount(amount_threshold: float = 50.0):
        now = datetime.now()
        return (
            Task.due_date < now,
            Task.status != Status.Done,
            Task.amount > amount_threshold
        )
    
    @staticmethod
    def upcoming_this_week():
        now = datetime.now()
        week_end = now + timedelta(days=7)
        return (
            Task.due_date >= now,
            Task.due_date <= week_end,
            Task.status == Status.Open
        )
```

**Dependencies:**
- Database (PostgreSQL Full-Text)
- Optional: Elasticsearch (für sehr große Datenmengen)

---

## 12. Analytics & Insights

### Verantwortung
Zeigt dem User Basic Stats zur Motivation und Fortschritts-Tracking.

### Features

- **Stats:**
  - Anzahl Tasks (Total, Done, Open)
  - Anzahl Dokumente (nach Typ)
  - Tasks diese Woche/Monat erledigt
  - Durchschnittliche Erledigungs-Zeit
  
- **Visualizations:**
  - Task Completion Chart (7/30 Tage)
  - Document Types Pie Chart
  - Priority Distribution
  
- **Achievements (Gamification):**
  - "10 Tasks erledigt! 🎉"
  - "Keine überfälligen Tasks diese Woche! ⭐"
  - "Streak: 5 Tage in Folge Tasks erledigt! 🔥"

### Schnittstellen
```python
GET /api/v1/analytics/summary
Response:
{
  "tasks": {
    "total": 150,
    "done": 120,
    "open": 25,
    "overdue": 5
  },
  "documents": {
    "total": 89,
    "by_type": {
      "invoice": 45,
      "contract": 12,
      "receipt": 32
    }
  },
  "this_week": {
    "completed": 7,
    "avg_time": "2.3 days"
  },
  "achievements": [
    {
      "title": "Task Master",
      "description": "10 Tasks erledigt!",
      "unlocked_at": "2026-01-15"
    }
  ]
}
```

### Technische Details
```python
class AnalyticsService:
    async def get_summary(self, user_id: UUID) -> AnalyticsSummary:
        tasks = await db.query(Task).filter(Task.user_id == user_id).all()
        
        total = len(tasks)
        done = len([t for t in tasks if t.status == Status.Done])
        open_tasks = len([t for t in tasks if t.status == Status.Open])
        overdue = len([
            t for t in tasks 
            if t.due_date < datetime.now() and t.status != Status.Done
        ])
        
        # Calculate average completion time
        completed = [t for t in tasks if t.completed_at]
        avg_time = mean([
            (t.completed_at - t.created_at).days 
            for t in completed
        ]) if completed else 0
        
        return AnalyticsSummary(
            total=total,
            done=done,
            open=open_tasks,
            overdue=overdue,
            avg_completion_days=avg_time
        )
```

**Dependencies:**
- Database
- Task Engine

---

## Component Dependencies Graph
```
Document Processor
    → File Storage
    → AI Engine
    → Task Engine

Task Engine
    → Reminder Engine
    → Calendar Sync
    → Database

Reminder Engine
    → Notification Channels
    → SLA Monitor
    → Background Jobs

Notification Channels
    → External APIs (Telegram, etc.)
    → Smart Home (Home Assistant)

Calendar Sync
    → External APIs (Google, Outlook)
    → Background Jobs

Integration Manager
    → External APIs (Paperless, etc.)
    → Background Jobs

Auth Service
    → Database
    → Redis
    → Email Service

Background Jobs (Celery)
    → Redis
    → All Components

Search & Filter
    → Database

Analytics
    → Database
    → Task Engine
```

---

## Zusammenfassung

Jede Komponente ist:
- **Modular:** Kann isoliert entwickelt werden
- **Testbar:** Klare Schnittstellen
- **Erweiterbar:** Neue Features können hinzugefügt werden
- **Austauschbar:** Implementierungen können gewechselt werden (z.B. Storage Backend)

Das Design folgt dem **Separation of Concerns** Prinzip und ermöglicht parallele Entwicklung und einfaches Testing.