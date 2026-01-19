# Tech Stack

## Overview

Workmate Private nutzt moderne, bewährte Technologien mit Fokus auf:
- **Entwicklungsgeschwindigkeit:** Schnell zum MVP
- **Maintainability:** Code der verstanden werden kann
- **Community:** Große Communities für Support
- **Flexibilität:** Self-Hosting UND Cloud möglich

## Frontend

### Flutter 3.x
**Warum Flutter?**
- ✅ **Cross-Platform:** Web, Android, iOS aus einer Codebase
- ✅ **Native Performance:** Kompiliert zu nativem Code
- ✅ **Hot Reload:** Schnelle Entwicklung
- ✅ **Material Design:** Schöne UI out-of-the-box
- ✅ **Growing Ecosystem:** Viele Packages verfügbar

**Dart Language**
- Moderne, typsichere Sprache
- Einfacher zu lernen als Java/Kotlin
- Gute Tooling (Flutter DevTools)

**Key Packages:**
```yaml
dependencies:
  flutter: sdk
  http: ^1.1.0              # HTTP Client
  provider: ^6.1.0          # State Management
  sqflite: ^2.3.0           # Local DB
  camera: ^0.10.0           # Scanner
  flutter_local_notifications: ^17.0.0  # Notifications
  intl: ^0.19.0             # Internationalization
```

## Backend

### Python 3.11+
**Warum Python?**
- ✅ **Bekannter Stack:** Du kennst es von WorkmateOS
- ✅ **KI-Integration:** Perfekt für AI/ML Libraries
- ✅ **Rapid Development:** Schnell produktiv
- ✅ **Große Community:** Viele Libraries

### FastAPI
**Warum FastAPI?**
- ✅ **Modern:** Async/Await Support
- ✅ **Schnell:** Comparable zu Node.js/Go
- ✅ **Type Hints:** Automatic API Docs (Swagger)
- ✅ **Validation:** Pydantic für Request/Response

**Key Libraries:**
```python
fastapi==0.109.0
uvicorn[standard]==0.27.0    # ASGI Server
sqlalchemy==2.0.25           # ORM
alembic==1.13.0              # DB Migrations
pydantic==2.5.0              # Data Validation
celery==5.3.0                # Background Tasks
redis==5.0.0                 # Cache & Message Broker
python-jose[cryptography]    # JWT
passlib[bcrypt]              # Password Hashing
python-multipart             # File Uploads
anthropic                    # Claude API
pytesseract                  # OCR Fallback
caldav                       # Calendar Integration
paho-mqtt                    # MQTT Client
```

## Datenbank

### SQLite (Self-Hosted)
**Warum SQLite?**
- ✅ **Zero Configuration:** Keine Installation nötig
- ✅ **Single File:** Einfach zu backupen
- ✅ **Perfekt für Single-User:** Ausreichende Performance
- ✅ **Cross-Platform:** Läuft überall

### PostgreSQL 14+ (Cloud)
**Warum PostgreSQL?**
- ✅ **Production-Ready:** Battle-tested
- ✅ **Rich Features:** JSON, Full-Text Search, etc.
- ✅ **Skalierbar:** Multi-User, High Load
- ✅ **ACID:** Transaktionssicherheit

**ORM: SQLAlchemy 2.0**
- Abstrahiert DB-Unterschiede
- Migrations via Alembic
- Type-safe Queries

## AI & NLP

### Claude API (Anthropic)
**Warum Claude?**
- ✅ **Dokumenten-Analyse:** Beste Performance für PDFs/Scans
- ✅ **Vision:** Kann Bilder direkt lesen
- ✅ **Context Window:** 200K Tokens = große Dokumente
- ✅ **Structured Outputs:** JSON-Responses
- ✅ **Safety:** Built-in für sensible Daten

**API Client:**
```python
from anthropic import Anthropic

client = Anthropic(api_key="...")
response = client.messages.create(
    model="claude-sonnet-4-20250514",
    messages=[...],
    max_tokens=1000
)
```

### Ollama (Self-Hosted Alternative)
**Warum Ollama?**
- ✅ **Privacy:** Läuft lokal, keine Cloud
- ✅ **Kostenlos:** Keine API-Kosten
- ✅ **Open Models:** LLaMA, Mistral, etc.
- ❌ **Performance:** Langsamer als Cloud
- ❌ **Hardware:** Braucht GPU für gute Performance

**Models:**
- `llama3.1:8b` - Leicht, schnell
- `mistral:7b` - Gut für Dokumenten-Analyse

### Tesseract OCR
**Warum Tesseract?**
- ✅ **Open Source:** Kostenlos
- ✅ **Offline:** Keine Internet nötig
- ✅ **Multi-Language:** Deutsch, Englisch, etc.
- ❌ **Genauigkeit:** Nicht so gut wie Claude Vision

**Integration:**
```python
import pytesseract
from PIL import Image

text = pytesseract.image_to_string(Image.open('scan.jpg'), lang='deu')
```

## Calendar Integration

### CalDAV
**Standard-Protokoll für Kalender**
- ✅ **Universal:** Nextcloud, Apple, etc.
- ✅ **Self-Hosted freundlich**

**Library:** `caldav` (Python)

### Google Calendar API
```python
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

service = build('calendar', 'v3', credentials=creds)
```

### Microsoft Graph API (Outlook)
```python
import requests

headers = {"Authorization": f"Bearer {token}"}
response = requests.get(
    "https://graph.microsoft.com/v1.0/me/calendar/events",
    headers=headers
)
```

## Smart Home Integration

### Home Assistant
**Warum Home Assistant?**
- ✅ **Open Source:** Community-driven
- ✅ **Flexible:** 1000+ Integrations
- ✅ **REST API:** Einfach zu integrieren

**API:**
```python
import requests

url = "http://homeassistant.local:8123/api/services/light/turn_on"
headers = {"Authorization": f"Bearer {token}"}
data = {"entity_id": "light.office"}
requests.post(url, json=data, headers=headers)
```

### MQTT
**Warum MQTT?**
- ✅ **Lightweight:** Perfekt für IoT
- ✅ **Pub/Sub:** Flexible Messaging
- ✅ **Standard:** Viele Geräte unterstützen es

**Library:** `paho-mqtt` (Python)

## File Storage

### Local Filesystem (Self-Hosted)
```python
import os
from pathlib import Path

UPLOAD_DIR = Path("data/uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)
```

### AWS S3 (Cloud)
```python
import boto3

s3 = boto3.client('s3')
s3.upload_file('local.pdf', 'bucket', 'remote.pdf')
```

**Alternative:** MinIO (S3-compatible, self-hosted)

## Background Processing

### Celery
**Warum Celery?**
- ✅ **Asynchronous Tasks:** Nicht-blockierend
- ✅ **Scheduling:** Cron-like Jobs
- ✅ **Distributed:** Kann skalieren

**Message Broker:** Redis
```python
from celery import Celery

app = Celery('workmate', broker='redis://localhost:6379')

@app.task
def process_document(doc_id):
    # Long-running task
    pass
```

## Authentication & Security

### JWT (JSON Web Tokens)
```python
from jose import jwt

token = jwt.encode({"sub": user_id}, SECRET_KEY, algorithm="HS256")
```

### OAuth2
- **Providers:** Google, GitHub, Microsoft
- **Library:** `authlib` oder `python-social-auth`

### 2FA
- **TOTP:** Time-based One-Time Passwords
- **Library:** `pyotp`
```python
import pyotp

totp = pyotp.TOTP('base32secret')
totp.verify('123456')  # Verify user code
```

## Testing

### Backend
```python
pytest==7.4.0              # Test Framework
pytest-asyncio==0.21.0     # Async Testing
pytest-cov==4.1.0          # Coverage
httpx==0.25.0              # HTTP Testing
```

### Frontend
```dart
flutter_test: sdk
mockito: ^5.4.0
```

## Deployment

### Docker
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0"]
```

### Docker Compose (Self-Hosted)
```yaml
version: '3.8'
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data
  
  redis:
    image: redis:7-alpine
  
  celery:
    build: ./backend
    command: celery -A app.celery worker
```

## CI/CD

### GitHub Actions
```yaml
name: Tests
on: [push]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
      - run: pip install -r requirements.txt
      - run: pytest
```

## Monitoring (Optional)

- **Logging:** `loguru` (Python), `logger` (Dart)
- **Metrics:** Prometheus + Grafana
- **Errors:** Sentry
- **Uptime:** UptimeRobot (für Cloud)

## Dependencies Management

### Backend
```bash
pip-tools  # requirements.in → requirements.txt
```

### Frontend
```bash
flutter pub get
flutter pub upgrade
```

## Development Tools

- **IDE:** VS Code mit Flutter + Python Extensions
- **API Testing:** Postman / Thunder Client
- **DB Management:** DBeaver / TablePlus
- **Git:** Standard Workflow mit Branches

## Version Targets

- **Python:** 3.11+
- **Flutter:** 3.16+
- **Dart:** 3.2+
- **PostgreSQL:** 14+
- **Redis:** 7+
- **Node.js:** 18+ (für Build-Tools)

## Decision Log

### Warum Python statt Go/Rust?
- Du kennst Python bereits
- Schnellere Entwicklung
- Bessere AI/ML Ecosystem
- Performance ist für unser Use Case ausreichend

### Warum Flutter statt React Native?
- Bessere Performance
- Konsistentere UI
- Aktive Community
- Web + Mobile aus einer Codebase

### Warum FastAPI statt Django?
- Moderner (Async)
- Weniger Boilerplate
- Perfekt für APIs (kein HTML-Rendering nötig)
- Bessere Developer Experience

### Warum Claude statt GPT?
- Bessere Dokumenten-Analyse in Tests
- 200K Context = große PDFs
- Vision-Fähigkeiten integriert
- Anthropic's Safety-Focus

---

**Dieser Stack ist pragmatisch, modern und erlaubt schnelle Iteration.**