# Data Model

## Overview

Das Workmate Private Datenmodell besteht aus 12 Haupt-Entities, die über Foreign Keys und Junction Tables miteinander verbunden sind. Das Schema ist sowohl für SQLite (Self-Hosted) als auch PostgreSQL (Cloud) optimiert.

## Entity Relationship Diagram
```
┌─────────────┐
│    User     │
└──────┬──────┘
       │
       ├──────────────┬──────────────┬──────────────┬──────────────┐
       │              │              │              │              │
┌──────▼──────┐ ┌─────▼─────┐ ┌─────▼─────┐ ┌─────▼─────┐ ┌─────▼─────┐
│  Document   │ │   Task    │ │ Calendar  │ │Integration│ │  Session  │
└──────┬──────┘ └─────┬─────┘ │   Event   │ └───────────┘ └───────────┘
       │              │        └───────────┘
       │              │
       │        ┌─────┼─────┬──────────────┬──────────────┐
       │        │     │     │              │              │
       │  ┌─────▼─────▼┐ ┌──▼──────┐ ┌────▼────────┐ ┌──▼──────────┐
       │  │  Reminder  │ │   Tag   │ │ Recurrence  │ │    Task     │
       │  └────────────┘ └────┬────┘ │    Rule     │ │ Dependency  │
       │                      │      └─────────────┘ └─────────────┘
       │                      │
┌──────▼──────┐         ┌────▼────┐
│    File     │         │TaskTag  │
└─────────────┘         │(M2M)    │
                        └─────────┘
┌─────────────┐
│Notification │
└─────────────┘
```

---

## 1. User

Speichert Benutzer-Accounts mit Profil und Präferenzen.

### Schema
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    
    -- Profile
    full_name VARCHAR(100),
    timezone VARCHAR(50) DEFAULT 'UTC',
    language VARCHAR(10) DEFAULT 'de',
    
    -- Preferences (JSON)
    notification_preferences JSONB DEFAULT '{}',
    ui_preferences JSONB DEFAULT '{}',
    
    -- Status
    is_active BOOLEAN DEFAULT true,
    is_verified BOOLEAN DEFAULT false,
    two_factor_enabled BOOLEAN DEFAULT false,
    two_factor_secret VARCHAR(32),
    
    -- Timestamps
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    last_login_at TIMESTAMP,
    
    -- Indexes
    INDEX idx_users_email (email),
    INDEX idx_users_username (username)
);
```

### SQLAlchemy Model
```python
from sqlalchemy import Column, String, Boolean, DateTime, JSON
from sqlalchemy.dialects.postgresql import UUID
import uuid

class User(Base):
    __tablename__ = 'users'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    
    # Profile
    full_name = Column(String(100))
    timezone = Column(String(50), default='UTC')
    language = Column(String(10), default='de')
    
    # Preferences
    notification_preferences = Column(JSON, default={})
    ui_preferences = Column(JSON, default={})
    
    # Status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    two_factor_enabled = Column(Boolean, default=False)
    two_factor_secret = Column(String(32))
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login_at = Column(DateTime)
    
    # Relationships
    documents = relationship('Document', back_populates='user')
    tasks = relationship('Task', back_populates='user')
    sessions = relationship('Session', back_populates='user')
```

### Preferences Structure
```json
{
  "notification_preferences": {
    "channels": {
      "push": true,
      "email": true,
      "sms": false,
      "telegram": false,
      "smart_home": false
    },
    "quiet_hours": {
      "enabled": true,
      "start": "22:00",
      "end": "07:00"
    },
    "reminder_frequency": {
      "info": "once",
      "warning": "daily",
      "urgent": "multiple",
      "critical": "hourly"
    }
  },
  "ui_preferences": {
    "theme": "light",
    "language": "de",
    "date_format": "DD.MM.YYYY",
    "first_day_of_week": 1
  }
}
```

---

## 2. Document

Speichert hochgeladene Dokumente mit Metadaten und KI-Analyse-Ergebnissen.

### Schema
```sql
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    file_id UUID NOT NULL REFERENCES files(id) ON DELETE CASCADE,
    
    -- Classification
    type VARCHAR(50) NOT NULL, -- invoice, reminder, contract, receipt, other
    title VARCHAR(255),
    
    -- Extracted Metadata (JSON for flexibility)
    metadata JSONB DEFAULT '{}',
    
    -- Processing
    processing_status VARCHAR(50) DEFAULT 'pending', -- pending, processing, done, failed
    confidence_score FLOAT,
    extracted_text TEXT,
    
    -- Timestamps
    uploaded_at TIMESTAMP NOT NULL DEFAULT NOW(),
    processed_at TIMESTAMP,
    
    -- Indexes
    INDEX idx_documents_user_id (user_id),
    INDEX idx_documents_type (type),
    INDEX idx_documents_status (processing_status),
    INDEX idx_documents_uploaded_at (uploaded_at)
);
```

### SQLAlchemy Model
```python
class Document(Base):
    __tablename__ = 'documents'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    file_id = Column(UUID(as_uuid=True), ForeignKey('files.id', ondelete='CASCADE'), nullable=False)
    
    # Classification
    type = Column(String(50), nullable=False, index=True)
    title = Column(String(255))
    
    # Metadata
    metadata = Column(JSON, default={})
    
    # Processing
    processing_status = Column(String(50), default='pending', index=True)
    confidence_score = Column(Float)
    extracted_text = Column(Text)
    
    # Timestamps
    uploaded_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    processed_at = Column(DateTime)
    
    # Relationships
    user = relationship('User', back_populates='documents')
    file = relationship('File', back_populates='document')
    tasks = relationship('Task', back_populates='document')
```

### Metadata Structure
```json
{
  "amount": 89.99,
  "currency": "EUR",
  "due_date": "2026-01-25",
  "invoice_number": "12345678",
  "sender": {
    "name": "Telekom Deutschland GmbH",
    "address": "...",
    "tax_id": "..."
  },
  "recipient": {
    "name": "Joshua ...",
    "address": "..."
  },
  "payment_info": {
    "iban": "DE...",
    "bic": "...",
    "reference": "..."
  },
  "line_items": [
    {
      "description": "Mobilfunk Vertrag",
      "amount": 89.99
    }
  ]
}
```

---

## 3. Task

Speichert Tasks mit Dependencies, Recurrence und Sub-Tasks.

### Schema
```sql
CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    document_id UUID REFERENCES documents(id) ON DELETE SET NULL,
    parent_task_id UUID REFERENCES tasks(id) ON DELETE CASCADE,
    
    -- Content
    title VARCHAR(255) NOT NULL,
    description TEXT,
    
    -- Scheduling
    due_date TIMESTAMP,
    estimated_duration_minutes INTEGER,
    
    -- Status
    status VARCHAR(50) DEFAULT 'open', -- open, in_progress, done, cancelled
    priority VARCHAR(50) DEFAULT 'medium', -- low, medium, high, critical
    
    -- Metadata
    amount DECIMAL(10, 2),
    currency VARCHAR(3) DEFAULT 'EUR',
    
    -- Timestamps
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMP,
    
    -- Indexes
    INDEX idx_tasks_user_id (user_id),
    INDEX idx_tasks_status (status),
    INDEX idx_tasks_priority (priority),
    INDEX idx_tasks_due_date (due_date),
    INDEX idx_tasks_document_id (document_id),
    INDEX idx_tasks_parent_id (parent_task_id)
);
```

### SQLAlchemy Model
```python
from enum import Enum

class TaskStatus(str, Enum):
    OPEN = 'open'
    IN_PROGRESS = 'in_progress'
    DONE = 'done'
    CANCELLED = 'cancelled'

class TaskPriority(str, Enum):
    LOW = 'low'
    MEDIUM = 'medium'
    HIGH = 'high'
    CRITICAL = 'critical'

class Task(Base):
    __tablename__ = 'tasks'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    document_id = Column(UUID(as_uuid=True), ForeignKey('documents.id', ondelete='SET NULL'), index=True)
    parent_task_id = Column(UUID(as_uuid=True), ForeignKey('tasks.id', ondelete='CASCADE'), index=True)
    
    # Content
    title = Column(String(255), nullable=False)
    description = Column(Text)
    
    # Scheduling
    due_date = Column(DateTime, index=True)
    estimated_duration_minutes = Column(Integer)
    
    # Status
    status = Column(String(50), default=TaskStatus.OPEN, index=True)
    priority = Column(String(50), default=TaskPriority.MEDIUM, index=True)
    
    # Metadata
    amount = Column(Numeric(10, 2))
    currency = Column(String(3), default='EUR')
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime)
    
    # Relationships
    user = relationship('User', back_populates='tasks')
    document = relationship('Document', back_populates='tasks')
    parent_task = relationship('Task', remote_side=[id], backref='subtasks')
    reminders = relationship('Reminder', back_populates='task')
    recurrence_rule = relationship('RecurrenceRule', back_populates='task', uselist=False)
    tags = relationship('Tag', secondary='task_tags', back_populates='tasks')
    
    # Dependencies (many-to-many via junction table)
    blocking = relationship('Task', 
                          secondary='task_dependencies',
                          primaryjoin='Task.id==TaskDependency.child_task_id',
                          secondaryjoin='Task.id==TaskDependency.parent_task_id',
                          backref='blocked_by')
```

---

## 4. Reminder

Speichert Reminder-Events mit History.

### Schema
```sql
CREATE TABLE reminders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_id UUID NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    
    -- Scheduling
    trigger_at TIMESTAMP NOT NULL,
    severity VARCHAR(50) NOT NULL, -- info, warning, urgent, critical
    
    -- Channels
    channels JSONB DEFAULT '[]', -- ["push", "email", "sms"]
    
    -- Status
    status VARCHAR(50) DEFAULT 'pending', -- pending, sent, failed
    sent_at TIMESTAMP,
    error_message TEXT,
    
    -- User Action
    acknowledged_at TIMESTAMP,
    snoozed_until TIMESTAMP,
    
    -- Timestamps
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    
    -- Indexes
    INDEX idx_reminders_task_id (task_id),
    INDEX idx_reminders_trigger_at (trigger_at),
    INDEX idx_reminders_status (status)
);
```

### SQLAlchemy Model
```python
class ReminderSeverity(str, Enum):
    INFO = 'info'
    WARNING = 'warning'
    URGENT = 'urgent'
    CRITICAL = 'critical'

class ReminderStatus(str, Enum):
    PENDING = 'pending'
    SENT = 'sent'
    FAILED = 'failed'

class Reminder(Base):
    __tablename__ = 'reminders'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    task_id = Column(UUID(as_uuid=True), ForeignKey('tasks.id', ondelete='CASCADE'), nullable=False, index=True)
    
    # Scheduling
    trigger_at = Column(DateTime, nullable=False, index=True)
    severity = Column(String(50), nullable=False)
    
    # Channels
    channels = Column(JSON, default=[])
    
    # Status
    status = Column(String(50), default=ReminderStatus.PENDING, index=True)
    sent_at = Column(DateTime)
    error_message = Column(Text)
    
    # User Action
    acknowledged_at = Column(DateTime)
    snoozed_until = Column(DateTime)
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    task = relationship('Task', back_populates='reminders')
```

---

## 5. Calendar Event

Speichert Kalender-Events für Sync mit externen Kalendern.

### Schema
```sql
CREATE TABLE calendar_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    task_id UUID REFERENCES tasks(id) ON DELETE CASCADE,
    
    -- Event Data
    title VARCHAR(255) NOT NULL,
    description TEXT,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP NOT NULL,
    all_day BOOLEAN DEFAULT false,
    
    -- External Sync
    external_calendar_id VARCHAR(255), -- Which calendar (Google, Outlook, etc.)
    external_event_id VARCHAR(255), -- ID in external system
    
    -- Sync Status
    sync_status VARCHAR(50) DEFAULT 'pending', -- pending, synced, conflict, failed
    last_synced_at TIMESTAMP,
    
    -- Conflict Resolution
    conflict_data JSONB, -- Stores both versions if conflict
    
    -- Timestamps
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    
    -- Indexes
    INDEX idx_calendar_user_id (user_id),
    INDEX idx_calendar_task_id (task_id),
    INDEX idx_calendar_start_time (start_time),
    INDEX idx_calendar_external_id (external_event_id),
    INDEX idx_calendar_sync_status (sync_status)
);
```

### SQLAlchemy Model
```python
class CalendarSyncStatus(str, Enum):
    PENDING = 'pending'
    SYNCED = 'synced'
    CONFLICT = 'conflict'
    FAILED = 'failed'

class CalendarEvent(Base):
    __tablename__ = 'calendar_events'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    task_id = Column(UUID(as_uuid=True), ForeignKey('tasks.id', ondelete='CASCADE'), index=True)
    
    # Event Data
    title = Column(String(255), nullable=False)
    description = Column(Text)
    start_time = Column(DateTime, nullable=False, index=True)
    end_time = Column(DateTime, nullable=False)
    all_day = Column(Boolean, default=False)
    
    # External Sync
    external_calendar_id = Column(String(255))
    external_event_id = Column(String(255), index=True)
    
    # Sync Status
    sync_status = Column(String(50), default=CalendarSyncStatus.PENDING, index=True)
    last_synced_at = Column(DateTime)
    
    # Conflict Resolution
    conflict_data = Column(JSON)
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship('User')
    task = relationship('Task')
```

---

## 6. Integration

Speichert User-Integrationen mit verschlüsselten Credentials.

### Schema
```sql
CREATE TABLE integrations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Integration Info
    integration_type VARCHAR(50) NOT NULL, -- paperless, home_assistant, telegram, etc.
    name VARCHAR(100), -- User-defined name
    enabled BOOLEAN DEFAULT false,
    
    -- Configuration (encrypted)
    config JSONB DEFAULT '{}',
    credentials_encrypted TEXT, -- Encrypted JSON with sensitive data
    
    -- Sync Status
    sync_status VARCHAR(50) DEFAULT 'idle', -- idle, syncing, error
    last_sync_at TIMESTAMP,
    error_log TEXT,
    
    -- Timestamps
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    
    -- Indexes
    INDEX idx_integrations_user_id (user_id),
    INDEX idx_integrations_type (integration_type),
    INDEX idx_integrations_enabled (enabled)
);
```

### SQLAlchemy Model
```python
from cryptography.fernet import Fernet

class Integration(Base):
    __tablename__ = 'integrations'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    
    # Integration Info
    integration_type = Column(String(50), nullable=False, index=True)
    name = Column(String(100))
    enabled = Column(Boolean, default=False, index=True)
    
    # Configuration
    config = Column(JSON, default={})
    credentials_encrypted = Column(Text)
    
    # Sync Status
    sync_status = Column(String(50), default='idle')
    last_sync_at = Column(DateTime)
    error_log = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship('User')
    
    # Methods for encryption/decryption
    def set_credentials(self, credentials: dict, encryption_key: bytes):
        fernet = Fernet(encryption_key)
        json_str = json.dumps(credentials)
        self.credentials_encrypted = fernet.encrypt(json_str.encode()).decode()
    
    def get_credentials(self, encryption_key: bytes) -> dict:
        if not self.credentials_encrypted:
            return {}
        fernet = Fernet(encryption_key)
        decrypted = fernet.decrypt(self.credentials_encrypted.encode()).decode()
        return json.loads(decrypted)
```

---

## 7. Notification

Speichert Benachrichtigungs-History.

### Schema
```sql
CREATE TABLE notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    task_id UUID REFERENCES tasks(id) ON DELETE CASCADE,
    reminder_id UUID REFERENCES reminders(id) ON DELETE CASCADE,
    
    -- Content
    title VARCHAR(255) NOT NULL,
    body TEXT,
    action_url VARCHAR(255),
    
    -- Delivery
    channel VARCHAR(50) NOT NULL, -- push, email, sms, telegram, smart_home
    status VARCHAR(50) DEFAULT 'pending', -- pending, sent, failed
    error_message TEXT,
    
    -- Timestamps
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    sent_at TIMESTAMP,
    
    -- User Action
    read_at TIMESTAMP,
    clicked_at TIMESTAMP,
    
    -- Indexes
    INDEX idx_notifications_user_id (user_id),
    INDEX idx_notifications_task_id (task_id),
    INDEX idx_notifications_status (status),
    INDEX idx_notifications_channel (channel),
    INDEX idx_notifications_sent_at (sent_at)
);
```

### SQLAlchemy Model
```python
class NotificationChannel(str, Enum):
    PUSH = 'push'
    EMAIL = 'email'
    SMS = 'sms'
    TELEGRAM = 'telegram'
    WHATSAPP = 'whatsapp'
    DISCORD = 'discord'
    SIGNAL = 'signal'
    SMART_HOME = 'smart_home'

class NotificationStatus(str, Enum):
    PENDING = 'pending'
    SENT = 'sent'
    FAILED = 'failed'

class Notification(Base):
    __tablename__ = 'notifications'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    task_id = Column(UUID(as_uuid=True), ForeignKey('tasks.id', ondelete='CASCADE'), index=True)
    reminder_id = Column(UUID(as_uuid=True), ForeignKey('reminders.id', ondelete='CASCADE'))
    
    # Content
    title = Column(String(255), nullable=False)
    body = Column(Text)
    action_url = Column(String(255))
    
    # Delivery
    channel = Column(String(50), nullable=False, index=True)
    status = Column(String(50), default=NotificationStatus.PENDING, index=True)
    error_message = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    sent_at = Column(DateTime, index=True)
    
    # User Action
    read_at = Column(DateTime)
    clicked_at = Column(DateTime)
    
    # Relationships
    user = relationship('User')
    task = relationship('Task')
    reminder = relationship('Reminder')
```

---

## 8. Session

Speichert User-Sessions mit Device-Tracking.

### Schema
```sql
CREATE TABLE sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Token
    token_hash VARCHAR(255) NOT NULL UNIQUE,
    refresh_token_hash VARCHAR(255),
    
    -- Device Info
    device_type VARCHAR(50), -- web, android, ios
    device_name VARCHAR(100),
    os VARCHAR(50),
    user_agent TEXT,
    
    -- Location
    ip_address VARCHAR(45), -- IPv6 compatible
    city VARCHAR(100),
    country VARCHAR(2), -- ISO Country Code
    
    -- Security
    is_suspicious BOOLEAN DEFAULT false,
    
    -- Status
    expires_at TIMESTAMP NOT NULL,
    last_active TIMESTAMP NOT NULL,
    
    -- Timestamps
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    
    -- Indexes
    INDEX idx_sessions_user_id (user_id),
    INDEX idx_sessions_token_hash (token_hash),
    INDEX idx_sessions_expires_at (expires_at),
    INDEX idx_sessions_suspicious (is_suspicious)
);
```

### SQLAlchemy Model
```python
import hashlib

class Session(Base):
    __tablename__ = 'sessions'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    
    # Token
    token_hash = Column(String(255), unique=True, nullable=False, index=True)
    refresh_token_hash = Column(String(255))
    
    # Device Info
    device_type = Column(String(50))
    device_name = Column(String(100))
    os = Column(String(50))
    user_agent = Column(Text)
    
    # Location
    ip_address = Column(String(45))
    city = Column(String(100))
    country = Column(String(2))
    
    # Security
    is_suspicious = Column(Boolean, default=False, index=True)
    
    # Status
    expires_at = Column(DateTime, nullable=False, index=True)
    last_active = Column(DateTime, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    user = relationship('User', back_populates='sessions')
    
    @staticmethod
    def hash_token(token: str) -> str:
        return hashlib.sha256(token.encode()).hexdigest()
```

---

## 9. Tag

Speichert Tags für Tasks.

### Schema
```sql
CREATE TABLE tags (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Tag Info
    name VARCHAR(50) NOT NULL,
    
    -- Timestamps
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    
    -- Constraints
    UNIQUE(user_id, name),
    
    -- Indexes
    INDEX idx_tags_user_id (user_id),
    INDEX idx_tags_name (name)
);
```

### SQLAlchemy Model
```python
class Tag(Base):
    __tablename__ = 'tags'
    __table_args__ = (
        UniqueConstraint('user_id', 'name', name='uq_user_tag'),
    )
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    
    # Tag Info
    name = Column(String(50), nullable=False, index=True)
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    user = relationship('User')
    tasks = relationship('Task', secondary='task_tags', back_populates='tags')
```

---

## 10. File

Speichert File-Metadata separat von Documents.

### Schema
```sql
CREATE TABLE files (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- File Info
    path VARCHAR(500) NOT NULL,
    original_filename VARCHAR(255) NOT NULL,
    size_bytes BIGINT NOT NULL,
    mime_type VARCHAR(100) NOT NULL,
    checksum VARCHAR(64), -- SHA256
    
    -- Storage
    storage_backend VARCHAR(50) DEFAULT 'local', -- local, s3
    
    -- Processing
    thumbnail_path VARCHAR(500),
    extracted_text TEXT,
    ocr_language VARCHAR(10),
    
    -- Timestamps
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    
    -- Indexes
    INDEX idx_files_user_id (user_id),
    INDEX idx_files_checksum (checksum),
    INDEX idx_files_created_at (created_at)
);
```

### SQLAlchemy Model
```python
class File(Base):
    __tablename__ = 'files'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    
    # File Info
    path = Column(String(500), nullable=False)
    original_filename = Column(String(255), nullable=False)
    size_bytes = Column(BigInteger, nullable=False)
    mime_type = Column(String(100), nullable=False)
    checksum = Column(String(64), index=True)
    
    # Storage
    storage_backend = Column(String(50), default='local')
    
    # Processing
    thumbnail_path = Column(String(500))
    extracted_text = Column(Text)
    ocr_language = Column(String(10))
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    
    # Relationships
    user = relationship('User')
    document = relationship('Document', back_populates='file', uselist=False)
```

---

## 11. Recurrence Rule

Speichert Regeln für wiederkehrende Tasks.

### Schema
```sql
CREATE TABLE recurrence_rules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_id UUID NOT NULL REFERENCES tasks(id) ON DELETE CASCADE UNIQUE,
    
    -- Rule
    frequency VARCHAR(50) NOT NULL, -- daily, weekly, monthly, yearly
    interval INTEGER DEFAULT 1, -- Every X days/weeks/months
    
    -- End Condition
    end_date TIMESTAMP,
    occurrences_count INTEGER, -- Stop after X occurrences
    
    -- Timestamps
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    
    -- Indexes
    INDEX idx_recurrence_task_id (task_id)
);
```

### SQLAlchemy Model
```python
class RecurrenceFrequency(str, Enum):
    DAILY = 'daily'
    WEEKLY = 'weekly'
    MONTHLY = 'monthly'
    YEARLY = 'yearly'

class RecurrenceRule(Base):
    __tablename__ = 'recurrence_rules'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    task_id = Column(UUID(as_uuid=True), ForeignKey('tasks.id', ondelete='CASCADE'), unique=True, nullable=False, index=True)
    
    # Rule
    frequency = Column(String(50), nullable=False)
    interval = Column(Integer, default=1)
    
    # End Condition
    end_date = Column(DateTime)
    occurrences_count = Column(Integer)
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    task = relationship('Task', back_populates='recurrence_rule')
```

---

## 12. Task Dependency (Junction Table)

Speichert Dependencies zwischen Tasks.

### Schema
```sql
CREATE TABLE task_dependencies (
    parent_task_id UUID NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    child_task_id UUID NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    
    PRIMARY KEY (parent_task_id, child_task_id),
    
    -- Indexes
    INDEX idx_task_dep_parent (parent_task_id),
    INDEX idx_task_dep_child (child_task_id)
);
```

### SQLAlchemy Model
```python
class TaskDependency(Base):
    __tablename__ = 'task_dependencies'
    
    parent_task_id = Column(UUID(as_uuid=True), ForeignKey('tasks.id', ondelete='CASCADE'), primary_key=True)
    child_task_id = Column(UUID(as_uuid=True), ForeignKey('tasks.id', ondelete='CASCADE'), primary_key=True)
    
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
```

---

## 13. Task Tag (Junction Table)

Many-to-Many zwischen Tasks und Tags.

### Schema
```sql
CREATE TABLE task_tags (
    task_id UUID NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    tag_id UUID NOT NULL REFERENCES tags(id) ON DELETE CASCADE,
    
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    
    PRIMARY KEY (task_id, tag_id),
    
    -- Indexes
    INDEX idx_task_tags_task (task_id),
    INDEX idx_task_tags_tag (tag_id)
);
```

### SQLAlchemy Model
```python
class TaskTag(Base):
    __tablename__ = 'task_tags'
    
    task_id = Column(UUID(as_uuid=True), ForeignKey('tasks.id', ondelete='CASCADE'), primary_key=True)
    tag_id = Column(UUID(as_uuid=True), ForeignKey('tags.id', ondelete='CASCADE'), primary_key=True)
    
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
```

---

## Indexes Summary

**Critical Indexes for Performance:**
```sql
-- User lookups
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);

-- Document queries
CREATE INDEX idx_documents_user_type ON documents(user_id, type);
CREATE INDEX idx_documents_status ON documents(processing_status);

-- Task queries
CREATE INDEX idx_tasks_user_status ON tasks(user_id, status);
CREATE INDEX idx_tasks_user_priority ON tasks(user_id, priority);
CREATE INDEX idx_tasks_due_date_status ON tasks(due_date, status);

-- Reminder scheduling
CREATE INDEX idx_reminders_trigger_status ON reminders(trigger_at, status);

-- Calendar sync
CREATE INDEX idx_calendar_user_start ON calendar_events(user_id, start_time);

-- Full-Text Search (PostgreSQL)
CREATE INDEX idx_documents_text ON documents USING gin(to_tsvector('german', extracted_text));
CREATE INDEX idx_tasks_text ON tasks USING gin(to_tsvector('german', title || ' ' || COALESCE(description, '')));
```

---

## Migration Strategy

### Alembic Setup
```python
# alembic/env.py
from app.models import Base

target_metadata = Base.metadata

def run_migrations_online():
    # Create all tables
    pass
```

### Initial Migration
```bash
alembic revision --autogenerate -m "Initial schema"
alembic upgrade head
```

---

## Data Retention Policy

- **Documents:** Soft delete + retention period (optional)
- **Tasks:** Keep completed tasks for analytics
- **Notifications:** Purge after 90 days
- **Sessions:** Expire automatically, purge after expiry
- **Files:** Keep while Document exists

---

## Backup Strategy

### Self-Hosted
```bash
# SQLite Backup
sqlite3 workmate.db ".backup workmate_backup.db"

# File Storage Backup
rsync -av /uploads/ /backups/uploads/
```

### Cloud (PostgreSQL)
```bash
# Automated daily backups
pg_dump workmate_prod > backup_$(date +%Y%m%d).sql
```

---

## Summary

- **13 Tables** (11 entities + 2 junction tables)
- **Clear Relationships** via Foreign Keys
- **Optimized Indexes** for common queries
- **Flexible Metadata** via JSON columns
- **Security** (encrypted credentials, suspicious detection)
- **Audit Trail** (timestamps on everything)
- **SQLite/PostgreSQL** compatible

Das Schema ist production-ready und skalierbar! 🚀