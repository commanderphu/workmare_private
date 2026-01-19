# System Overview

## High-Level Architektur

Workmate Private folgt einer modernen, modularen Architektur, die sowohl Self-Hosting als auch Cloud-Deployment unterstützt.
```
┌─────────────────────────────────────────────────────────────┐
│                        USER LAYER                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Flutter    │  │   Flutter    │  │   Flutter    │      │
│  │   Web App    │  │  Android App │  │   iOS App    │      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
│         │                  │                  │              │
└─────────┼──────────────────┼──────────────────┼──────────────┘
          │                  │                  │
          └──────────────────┴──────────────────┘
                             │
┌────────────────────────────▼─────────────────────────────────┐
│                       API GATEWAY                             │
│                    (FastAPI Backend)                          │
│  ┌────────────────────────────────────────────────────────┐  │
│  │                   REST API Endpoints                    │  │
│  │  /auth  /documents  /tasks  /calendar  /integrations   │  │
│  └────────────────────────────────────────────────────────┘  │
└───────────────────────────────────────────────────────────────┘
                             │
          ┌──────────────────┼──────────────────┐
          │                  │                  │
┌─────────▼─────────┐ ┌──────▼──────┐ ┌────────▼─────────┐
│   CORE SERVICES   │ │   AI ENGINE  │ │  INTEGRATIONS    │
│                   │ │              │ │                  │
│ • Document Mgmt   │ │ • Claude API │ │ • CalDAV         │
│ • Task Engine     │ │ • Tesseract  │ │ • Google Cal     │
│ • Reminder System │ │ • OCR        │ │ • Outlook        │
│ • SLA Monitor     │ │ • NLP        │ │ • Home Assistant │
│ • Calendar Sync   │ │              │ │ • MQTT           │
│                   │ │              │ │ • Paperless-ngx  │
└─────────┬─────────┘ └──────┬───────┘ └────────┬─────────┘
          │                  │                  │
          └──────────────────┼──────────────────┘
                             │
┌────────────────────────────▼─────────────────────────────────┐
│                      DATA LAYER                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │  PostgreSQL  │  │    SQLite    │  │  File Storage│       │
│  │   (Cloud)    │  │(Self-Hosted) │  │  (Local/S3)  │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
└───────────────────────────────────────────────────────────────┘
```

## Deployment-Modelle

### Self-Hosted
- User hostet auf eigenem Server/NAS
- SQLite als Datenbank
- Lokales Filesystem für Dokumente
- Optional: Lokale AI-Models (Ollama)
- Volle Kontrolle über Daten

### Cloud-Hosted
- Von K.I.T. Solutions gehostet
- PostgreSQL als Datenbank
- S3 für Dokumente
- Claude API für AI
- Managed Service mit Support

### Hybrid
- Backend kann auf Server laufen
- Frontend-Apps connecten via API
- Mix aus lokalen und Cloud-Services möglich

## Hauptkomponenten

### 1. Frontend (Flutter)
- **Verantwortung:** User Interface für alle Plattformen
- **Plattformen:** Web, Android, iOS
- **Technologie:** Dart + Flutter Framework
- **Features:**
  - Dokumenten-Scanner (Kamera-Integration)
  - Task-Management UI
  - Kalender-Ansicht
  - Benachrichtigungen
  - Settings & Integrations

### 2. Backend API (FastAPI)
- **Verantwortung:** Business Logic, API-Endpoints
- **Technologie:** Python + FastAPI
- **Features:**
  - RESTful API
  - Authentication & Authorization
  - Request Validation
  - Background Tasks (Celery)
  - WebSocket für Real-Time Updates

### 3. AI Engine
- **Verantwortung:** Dokumenten-Analyse, Text-Extraktion
- **Technologien:**
  - Claude API (Cloud)
  - Ollama/LLaMA (Self-Hosted)
  - Tesseract OCR (Fallback)
- **Features:**
  - Dokumenten-Klassifizierung
  - Entitäten-Extraktion (Beträge, Daten, etc.)
  - Kontext-Analyse
  - Prioritäts-Berechnung

### 4. Task & Reminder Engine
- **Verantwortung:** Task-Management, Reminder-Logik
- **Features:**
  - Task-Erstellung aus Dokumenten
  - SLA-Monitoring
  - Eskalations-Logik
  - Multi-Channel Notifications
  - Recurring Tasks

### 5. Calendar Service
- **Verantwortung:** Kalender-Synchronisation
- **Integrations:**
  - CalDAV (universal)
  - Google Calendar API
  - Microsoft Outlook API
  - Apple Calendar
- **Features:**
  - Bidirektionale Sync
  - Event-Management
  - Konflikt-Erkennung

### 6. Integration Layer
- **Verantwortung:** Externe Service-Integrationen
- **Services:**
  - Paperless-ngx (Dokumenten-Management)
  - Home Assistant (Smart Home)
  - MQTT (IoT)
  - Email (IMAP/SMTP)
  - Tracking-APIs (DHL, DPD, etc.)

### 7. Storage Layer
- **Verantwortung:** Persistierung von Daten und Files
- **Komponenten:**
  - Datenbank (SQLite/PostgreSQL)
  - File Storage (Local/S3)
  - Cache (Redis - optional)

## Data Flow: Beispiel "Rechnung scannen"
```
1. User scannt Rechnung mit Flutter App
   ↓
2. Bild wird an Backend API gesendet
   ↓
3. AI Engine analysiert Dokument
   - Claude Vision extrahiert Text
   - NLP erkennt: Typ=Rechnung, Betrag=89€, Frist=25.01.2026
   ↓
4. Task Engine erstellt Tasks
   - Task: "Rechnung bezahlen"
   - Deadline: 25.01.2026
   - Priority: Medium (steigt mit Zeit)
   ↓
5. Calendar Service synct mit User-Kalender
   - Event: "Rechnung fällig" am 25.01.
   ↓
6. Reminder Engine scheduled Notifications
   - 7 Tage vorher: Info
   - 2 Tage vorher: Warnung
   - 1 Tag vorher: Dringend
   ↓
7. Storage Layer speichert alles
   - Dokument als PDF/Image
   - Task in DB
   - Metadata
   ↓
8. User bekommt proaktive Benachrichtigung
```

## Skalierbarkeit

### Horizontal Scaling
- API-Server können repliziert werden
- Load Balancer verteilt Traffic
- Stateless Backend-Design

### Vertical Scaling
- Self-Hosted kann mit Hardware wachsen
- Cloud kann Ressourcen dynamisch anpassen

### Background Processing
- Celery für asynchrone Tasks
- Redis als Message Broker
- Separate Worker für AI-Processing

## Security

### Data Protection
- End-to-End Encryption für Dokumente (optional)
- HTTPS/TLS für alle Verbindungen
- Verschlüsselte DB-Backups

### Authentication
- JWT für API-Auth
- OAuth2 für Social Login
- 2FA Support

### Privacy
- GDPR-Compliant
- Data Export/Delete Funktionen
- Self-Hosting = volle Daten-Kontrolle

## Performance-Ziele

- **API Response Time:** < 200ms (p95)
- **Document Processing:** < 5s für Standard-Dokument
- **App Startup:** < 2s
- **Offline-Fähigkeit:** Basis-Features funktionieren offline

## Monitoring & Observability

- **Logging:** Strukturierte Logs (JSON)
- **Metrics:** Prometheus + Grafana (optional)
- **Error Tracking:** Sentry (optional)
- **Health Checks:** /health endpoint

## Backup & Recovery

- **Self-Hosted:** User-Verantwortung (Scripts bereitgestellt)
- **Cloud:** Automatische täglich Backups
- **Export:** JSON/CSV Export aller Daten