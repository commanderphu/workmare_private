# Development Setup

## Prerequisites

### Required Software
```bash
# System Requirements
- OS: Linux (Ubuntu 22.04+), macOS 12+, Windows 10+ (WSL2)
- RAM: 8GB minimum, 16GB recommended
- Disk: 20GB free space

# Core Tools
- Python 3.11+
- Node.js 18+ (for build tools)
- Git 2.30+
- Docker & Docker Compose (optional, recommended)

# Flutter Development
- Flutter SDK 3.16+
- Android Studio (for Android development)
- Xcode (for iOS development, macOS only)
```

---

## Backend Setup

### 1. Clone Repository
```bash
git clone https://github.com/commanderphu/workmate-private.git
cd workmate-private
```

### 2. Python Environment

**Using venv:**
```bash
# Create virtual environment
python3.11 -m venv venv

# Activate
source venv/bin/activate  # Linux/macOS
# or
.\venv\Scripts\activate  # Windows

# Upgrade pip
pip install --upgrade pip
```

**Using conda (alternative):**
```bash
conda create -n workmate python=3.11
conda activate workmate
```

### 3. Install Dependencies
```bash
# Install backend dependencies
cd backend
pip install -r requirements.txt --break-system-packages

# Install development dependencies
pip install -r requirements-dev.txt --break-system-packages
```

**requirements.txt:**
```txt
fastapi==0.109.0
uvicorn[standard]==0.27.0
sqlalchemy==2.0.25
alembic==1.13.0
pydantic==2.5.0
celery==5.3.0
redis==5.0.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
anthropic==0.18.0
pytesseract==0.3.10
caldav==1.3.9
paho-mqtt==1.6.1
aiohttp==3.9.1
python-docx==1.1.0
openpyxl==3.1.2
PyPDF2==3.0.1
Pillow==10.2.0
python-dateutil==2.8.2
pytz==2023.3
```

**requirements-dev.txt:**
```txt
pytest==7.4.0
pytest-asyncio==0.21.0
pytest-cov==4.1.0
httpx==0.25.0
black==23.12.0
flake8==7.0.0
mypy==1.8.0
ipython==8.19.0
```

### 4. Environment Configuration
```bash
# Copy example env file
cp .env.example .env

# Edit with your settings
nano .env
```

**.env.example:**
```bash
# Application
APP_NAME="Workmate Private"
APP_ENV=development
DEBUG=true
SECRET_KEY=your-secret-key-here-change-in-production

# Database
DATABASE_URL=sqlite:///./workmate.db
# For PostgreSQL:
# DATABASE_URL=postgresql://user:password@localhost/workmate

# Redis
REDIS_URL=redis://localhost:6379/0

# Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/1

# AI Services
ANTHROPIC_API_KEY=your-anthropic-api-key
# For Self-Hosted Ollama:
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1:8b

# File Storage
STORAGE_BACKEND=local  # or 's3'
UPLOAD_DIR=./data/uploads
# For S3:
# AWS_ACCESS_KEY_ID=your-key
# AWS_SECRET_ACCESS_KEY=your-secret
# AWS_S3_BUCKET=workmate-files
# AWS_REGION=eu-central-1

# Email (SMTP)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
EMAIL_FROM=noreply@workmate.local

# Encryption
ENCRYPTION_KEY=generate-with-fernet-key-generator

# CORS
CORS_ORIGINS=["http://localhost:3000", "http://localhost:5173"]
```

### 5. Database Setup
```bash
# Run migrations
alembic upgrade head

# Create initial data (optional)
python scripts/init_db.py
```

**Initialize Database Script:**
```python
# scripts/init_db.py
import asyncio
from app.database import engine, Base
from app.models import User
from app.core.security import get_password_hash

async def init_db():
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Create test user
    async with AsyncSession(engine) as session:
        user = User(
            username="test",
            email="test@example.com",
            password_hash=get_password_hash("test123")
        )
        session.add(user)
        await session.commit()
    
    print("✅ Database initialized!")

if __name__ == "__main__":
    asyncio.run(init_db())
```

### 6. Start Services

**Option A: Manual (Development):**
```bash
# Terminal 1: Redis
redis-server

# Terminal 2: Backend API
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 3: Celery Worker
cd backend
celery -A app.celery worker --loglevel=info

# Terminal 4: Celery Beat (Scheduler)
cd backend
celery -A app.celery beat --loglevel=info
```

**Option B: Docker Compose (Easier):**
```bash
docker-compose up -d
```

**docker-compose.yml:**
```yaml
version: '3.8'

services:
  postgres:
    image: postgres:14-alpine
    environment:
      POSTGRES_USER: workmate
      POSTGRES_PASSWORD: workmate
      POSTGRES_DB: workmate
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
  
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
  
  backend:
    build: ./backend
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
    volumes:
      - ./backend:/app
      - ./data:/app/data
    ports:
      - "8000:8000"
    depends_on:
      - postgres
      - redis
    env_file:
      - .env
  
  celery:
    build: ./backend
    command: celery -A app.celery worker --loglevel=info
    volumes:
      - ./backend:/app
      - ./data:/app/data
    depends_on:
      - redis
      - postgres
    env_file:
      - .env
  
  celery-beat:
    build: ./backend
    command: celery -A app.celery beat --loglevel=info
    volumes:
      - ./backend:/app
    depends_on:
      - redis
    env_file:
      - .env

volumes:
  postgres_data:
```

### 7. Verify Backend
```bash
# Check API health
curl http://localhost:8000/api/health

# Expected response:
# {"status":"ok","version":"0.1.0"}

# Check API docs
open http://localhost:8000/docs
```

---

## Frontend Setup (Flutter)

### 1. Install Flutter

**Linux/macOS:**
```bash
# Download Flutter SDK
git clone https://github.com/flutter/flutter.git -b stable ~/flutter

# Add to PATH
echo 'export PATH="$HOME/flutter/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc

# Verify installation
flutter --version
flutter doctor
```

**Windows:**
- Download Flutter SDK: https://docs.flutter.dev/get-started/install/windows
- Extract to `C:\flutter`
- Add to PATH

### 2. Install Dependencies
```bash
cd frontend
flutter pub get
```

**pubspec.yaml:**
```yaml
name: workmate_private
description: Workmate Private - ADHD-friendly task management
version: 1.0.0+1

environment:
  sdk: '>=3.2.0 <4.0.0'

dependencies:
  flutter:
    sdk: flutter
  
  # HTTP & API
  http: ^1.1.0
  dio: ^5.4.0
  
  # State Management
  provider: ^6.1.0
  
  # Local Storage
  sqflite: ^2.3.0
  shared_preferences: ^2.2.0
  
  # Camera & Scanner
  camera: ^0.10.5
  image_picker: ^1.0.5
  
  # Notifications
  flutter_local_notifications: ^17.0.0
  
  # UI Components
  flutter_svg: ^2.0.9
  cached_network_image: ^3.3.0
  
  # Utilities
  intl: ^0.19.0
  path_provider: ^2.1.0
  uuid: ^4.2.0
  
dev_dependencies:
  flutter_test:
    sdk: flutter
  flutter_lints: ^3.0.0
  mockito: ^5.4.0
```

### 3. Configure API Endpoint
```dart
// lib/config/api_config.dart
class ApiConfig {
  static const String baseUrl = String.fromEnvironment(
    'API_URL',
    defaultValue: 'http://localhost:8000',
  );
  
  static const Duration timeout = Duration(seconds: 30);
}
```

### 4. Run Flutter App

**Web:**
```bash
flutter run -d chrome --web-port 3000
```

**Android (Emulator):**
```bash
# Start emulator
flutter emulators --launch Pixel_5

# Run app
flutter run -d emulator-5554
```

**Android (Physical Device):**
```bash
# Enable USB debugging on phone
# Connect via USB

flutter run
```

**iOS (macOS only):**
```bash
# Start simulator
open -a Simulator

# Run app
flutter run -d "iPhone 14"
```

---

## IDE Setup

### Visual Studio Code

**Recommended Extensions:**
```json
{
  "recommendations": [
    "ms-python.python",
    "ms-python.black-formatter",
    "ms-python.flake8",
    "ms-python.mypy-type-checker",
    "dart-code.dart-code",
    "dart-code.flutter",
    "esbenp.prettier-vscode",
    "dbaeumer.vscode-eslint"
  ]
}
```

**Settings (.vscode/settings.json):**
```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/venv/bin/python",
  "python.formatting.provider": "black",
  "python.linting.enabled": true,
  "python.linting.flake8Enabled": true,
  "editor.formatOnSave": true,
  "[python]": {
    "editor.defaultFormatter": "ms-python.black-formatter"
  },
  "[dart]": {
    "editor.formatOnSave": true
  }
}
```

### PyCharm / IntelliJ IDEA

1. Open Project
2. Configure Python Interpreter → Select venv
3. Enable Django/FastAPI support
4. Install Flutter plugin
5. Configure Flutter SDK path

---

## Testing Setup

### Backend Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test
pytest tests/test_documents.py

# Run with verbose output
pytest -v -s
```

**pytest.ini:**
```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
asyncio_mode = auto
addopts = 
    --strict-markers
    --cov=app
    --cov-report=term-missing
    --cov-report=html
```

### Frontend Tests
```bash
# Run all tests
flutter test

# Run with coverage
flutter test --coverage

# Run specific test
flutter test test/widget_test.dart
```

---

## Development Workflow

### Git Workflow
```bash
# Create feature branch
git checkout -b feature/document-scanner

# Make changes, commit
git add .
git commit -m "feat: add document scanner"

# Push to remote
git push origin feature/document-scanner

# Create Pull Request on GitHub
```

**Commit Message Convention:**
```
feat: Add new feature
fix: Fix bug
docs: Update documentation
style: Code style changes
refactor: Refactor code
test: Add tests
chore: Maintenance tasks
```

### Code Formatting

**Backend:**
```bash
# Format with black
black app/

# Lint with flake8
flake8 app/

# Type check with mypy
mypy app/
```

**Frontend:**
```bash
# Format with dart format
dart format lib/

# Analyze
flutter analyze
```

### Pre-commit Hook

**Install pre-commit:**
```bash
pip install pre-commit
pre-commit install
```

**.pre-commit-config.yaml:**
```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.12.0
    hooks:
      - id: black
  
  - repo: https://github.com/PyCQA/flake8
    rev: 7.0.0
    hooks:
      - id: flake8
  
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.8.0
    hooks:
      - id: mypy
```

---

## Troubleshooting

### Common Issues

**1. SQLAlchemy Import Error**
```bash
# Solution: Install with break-system-packages
pip install sqlalchemy --break-system-packages
```

**2. Redis Connection Failed**
```bash
# Check if Redis is running
redis-cli ping

# Start Redis
redis-server
```

**3. Celery Worker Not Starting**
```bash
# Check Redis connection
redis-cli ping

# Check Celery logs
celery -A app.celery worker --loglevel=debug
```

**4. Flutter Build Failed**
```bash
# Clean build
flutter clean
flutter pub get

# Rebuild
flutter run
```

**5. Port Already in Use**
```bash
# Find process using port 8000
lsof -ti:8000

# Kill process
kill -9 $(lsof -ti:8000)
```

---

## Next Steps

✅ Development environment is set up!

**Now you can:**
1. Start coding new features
2. Run tests
3. Contribute to the project

**Useful Commands:**
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f backend

# Run migrations
alembic upgrade head

# Create new migration
alembic revision --autogenerate -m "Add new table"

# Run tests
pytest

# Start Flutter app
flutter run
```

**Read next:**
- [API Reference](./api-reference.md)
- [Deployment Guide](./deployment.md)
- [Contributing Guidelines](./contributing.md)
