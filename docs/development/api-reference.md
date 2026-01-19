# API Reference

## Base URL
```
Development: http://localhost:8000
Production: https://api.workmate.private
```

## Authentication

All API requests require authentication via JWT tokens.

### Login

**POST** `/api/v1/auth/login`

**Request:**
```json
{
  "username": "joshua",
  "password": "secure_password"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

### Authenticated Requests

Include token in Authorization header:
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/v1/tasks
```

---

## Documents

### Upload Document

**POST** `/api/v1/documents/upload`

**Content-Type:** `multipart/form-data`

**Request:**
```bash
curl -X POST \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@document.pdf" \
  http://localhost:8000/api/v1/documents/upload
```

**Response:**
```json
{
  "document_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "processing",
  "message": "Document uploaded successfully"
}
```

### Get Document

**GET** `/api/v1/documents/{document_id}`

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "title": "Telekom Rechnung Januar 2026",
  "type": "invoice",
  "processing_status": "done",
  "confidence_score": 0.95,
  "metadata": {
    "amount": 89.99,
    "currency": "EUR",
    "due_date": "2026-01-25",
    "sender": {
      "name": "Telekom Deutschland GmbH"
    }
  },
  "uploaded_at": "2026-01-19T10:30:00Z",
  "processed_at": "2026-01-19T10:30:15Z"
}
```

### List Documents

**GET** `/api/v1/documents`

**Query Parameters:**
- `page` (int, default: 1)
- `page_size` (int, default: 20)
- `type` (string, optional): filter by type
- `status` (string, optional): filter by status

**Response:**
```json
{
  "total": 150,
  "page": 1,
  "page_size": 20,
  "results": [
    {
      "id": "...",
      "title": "...",
      "type": "invoice",
      "uploaded_at": "..."
    }
  ]
}
```

### Delete Document

**DELETE** `/api/v1/documents/{document_id}`

**Response:**
```json
{
  "message": "Document deleted successfully"
}
```

---

## Tasks

### Create Task

**POST** `/api/v1/tasks`

**Request:**
```json
{
  "title": "Telekom Rechnung bezahlen",
  "description": "Rechnung vom 10.01.2026",
  "due_date": "2026-01-25T23:59:59Z",
  "priority": "high",
  "document_id": "550e8400-e29b-41d4-a716-446655440000",
  "amount": 89.99,
  "tags": ["rechnung", "telekom"]
}
```

**Response:**
```json
{
  "id": "660e8400-e29b-41d4-a716-446655440001",
  "title": "Telekom Rechnung bezahlen",
  "status": "open",
  "priority": "high",
  "due_date": "2026-01-25T23:59:59Z",
  "created_at": "2026-01-19T10:35:00Z"
}
```

### Get Task

**GET** `/api/v1/tasks/{task_id}`

**Response:**
```json
{
  "id": "660e8400-e29b-41d4-a716-446655440001",
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "document_id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Telekom Rechnung bezahlen",
  "description": "Rechnung vom 10.01.2026",
  "status": "open",
  "priority": "high",
  "due_date": "2026-01-25T23:59:59Z",
  "amount": 89.99,
  "currency": "EUR",
  "tags": ["rechnung", "telekom"],
  "created_at": "2026-01-19T10:35:00Z",
  "updated_at": "2026-01-19T10:35:00Z"
}
```

### List Tasks

**GET** `/api/v1/tasks`

**Query Parameters:**
- `status` (string): open, in_progress, done, cancelled
- `priority` (string): low, medium, high, critical
- `due_before` (datetime): filter tasks due before date
- `due_after` (datetime): filter tasks due after date
- `page` (int, default: 1)
- `page_size` (int, default: 20)

**Response:**
```json
{
  "total": 45,
  "page": 1,
  "page_size": 20,
  "results": [...]
}
```

### Update Task

**PATCH** `/api/v1/tasks/{task_id}`

**Request:**
```json
{
  "status": "done",
  "completed_at": "2026-01-19T15:00:00Z"
}
```

**Response:**
```json
{
  "id": "660e8400-e29b-41d4-a716-446655440001",
  "status": "done",
  "completed_at": "2026-01-19T15:00:00Z"
}
```

### Delete Task

**DELETE** `/api/v1/tasks/{task_id}`

---

## Reminders

### Get Reminders for Task

**GET** `/api/v1/tasks/{task_id}/reminders`

**Response:**
```json
{
  "reminders": [
    {
      "id": "770e8400-e29b-41d4-a716-446655440002",
      "task_id": "660e8400-e29b-41d4-a716-446655440001",
      "trigger_at": "2026-01-18T09:00:00Z",
      "severity": "warning",
      "status": "sent",
      "sent_at": "2026-01-18T09:00:05Z"
    }
  ]
}
```

### Snooze Reminder

**POST** `/api/v1/reminders/{reminder_id}/snooze`

**Request:**
```json
{
  "duration": "1hour"
}
```

**Response:**
```json
{
  "status": "snoozed",
  "until": "2026-01-19T16:00:00Z"
}
```

---

## Calendar

### Get Calendar Events

**GET** `/api/v1/calendar/events`

**Query Parameters:**
- `start` (datetime): filter events starting after
- `end` (datetime): filter events ending before

**Response:**
```json
{
  "events": [
    {
      "id": "880e8400-e29b-41d4-a716-446655440003",
      "task_id": "660e8400-e29b-41d4-a716-446655440001",
      "title": "Telekom Rechnung fällig",
      "start_time": "2026-01-25T00:00:00Z",
      "end_time": "2026-01-25T23:59:59Z",
      "sync_status": "synced"
    }
  ]
}
```

### Sync Calendar

**POST** `/api/v1/calendar/sync`

**Response:**
```json
{
  "status": "success",
  "synced_events": 15,
  "conflicts": 0
}
```

---

## Integrations

### List Integrations

**GET** `/api/v1/integrations`

**Response:**
```json
{
  "integrations": [
    {
      "id": "paperless",
      "name": "Paperless-ngx",
      "enabled": true,
      "last_sync_at": "2026-01-19T10:00:00Z",
      "sync_status": "success"
    }
  ]
}
```

### Enable Integration

**POST** `/api/v1/integrations/{integration_type}/enable`

**Request (Paperless example):**
```json
{
  "url": "http://paperless.local:8000",
  "token": "your-paperless-token"
}
```

**Response:**
```json
{
  "status": "enabled",
  "message": "Integration enabled successfully"
}
```

### Disable Integration

**POST** `/api/v1/integrations/{integration_type}/disable`

---

## Analytics

### Get Summary

**GET** `/api/v1/analytics/summary`

**Response:**
```json
{
  "tasks": {
    "total": 150,
    "open": 25,
    "done": 120,
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
  }
}
```

---

## Search

### Search Documents & Tasks

**GET** `/api/v1/search`

**Query Parameters:**
- `q` (string, required): search query
- `type` (string): documents, tasks, or both (default)
- `page` (int, default: 1)

**Response:**
```json
{
  "query": "telekom rechnung",
  "total_results": 12,
  "results": [
    {
      "type": "document",
      "id": "...",
      "title": "Telekom Rechnung Januar 2026",
      "score": 0.95
    },
    {
      "type": "task",
      "id": "...",
      "title": "Telekom Rechnung bezahlen",
      "score": 0.89
    }
  ]
}
```

---

## WebSockets

### Real-Time Updates

**Connect:** `ws://localhost:8000/ws/{user_id}`

**Authentication:** Send JWT token in first message

**Events:**
```json
{
  "event": "document_processed",
  "data": {
    "document_id": "...",
    "status": "done"
  }
}
```
```json
{
  "event": "reminder_triggered",
  "data": {
    "reminder_id": "...",
    "task_id": "...",
    "severity": "urgent"
  }
}
```

---

## Error Responses

### Standard Error Format
```json
{
  "detail": "Error message",
  "status_code": 400,
  "error_code": "VALIDATION_ERROR"
}
```

### Common Status Codes

- `200` - Success
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `422` - Validation Error
- `500` - Internal Server Error

---

## Rate Limiting

**Limits:**
- Anonymous: 100 requests/hour
- Authenticated: 1000 requests/hour

**Headers:**
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 995
X-RateLimit-Reset: 1642608000
```

---

## API Clients

### Python
```python
import requests

BASE_URL = "http://localhost:8000"

# Login
response = requests.post(
    f"{BASE_URL}/api/v1/auth/login",
    json={"username": "test", "password": "test123"}
)
token = response.json()["access_token"]

# Authenticated request
headers = {"Authorization": f"Bearer {token}"}
tasks = requests.get(f"{BASE_URL}/api/v1/tasks", headers=headers)
```

### Dart/Flutter
```dart
import 'package:dio/dio.dart';

class WorkmateAPI {
  final Dio dio = Dio(BaseOptions(
    baseUrl: 'http://localhost:8000',
  ));
  
  String? token;
  
  Future<void> login(String username, String password) async {
    final response = await dio.post('/api/v1/auth/login', data: {
      'username': username,
      'password': password,
    });
    
    token = response.data['access_token'];
    dio.options.headers['Authorization'] = 'Bearer $token';
  }
  
  Future<List<Task>> getTasks() async {
    final response = await dio.get('/api/v1/tasks');
    return (response.data['results'] as List)
        .map((json) => Task.fromJson(json))
        .toList();
  }
}
```

---

## OpenAPI Schema

Full OpenAPI schema available at:

**Swagger UI:** `http://localhost:8000/docs`  
**ReDoc:** `http://localhost:8000/redoc`  
**JSON Schema:** `http://localhost:8000/openapi.json`