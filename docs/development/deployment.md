# Deployment Guide

## Deployment Options

Workmate Private can be deployed in multiple ways:

1. **Self-Hosted (Local Network)**
2. **Self-Hosted (VPS/Cloud)**
3. **Docker Compose**
4. **Kubernetes**

---

## Prerequisites

### Hardware Requirements

**Minimum:**
- CPU: 2 cores
- RAM: 4GB
- Disk: 20GB SSD
- Network: 10 Mbps

**Recommended:**
- CPU: 4 cores
- RAM: 8GB
- Disk: 50GB SSD
- Network: 100 Mbps

### Software Requirements

- Docker 24.0+
- Docker Compose 2.0+
- OR: Python 3.11+, Node.js 18+, PostgreSQL 14+, Redis 7+

---

## Option 1: Docker Compose (Recommended)

### 1. Prepare Server
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo apt install docker-compose-plugin

# Verify
docker --version
docker compose version
```

### 2. Clone & Configure
```bash
# Clone repository
git clone https://github.com/commanderphu/workmate-private.git
cd workmate-private

# Copy production env
cp .env.example .env.production

# Edit configuration
nano .env.production
```

**.env.production:**
```bash
# Application
APP_NAME="Workmate Private"
APP_ENV=production
DEBUG=false
SECRET_KEY=GENERATE_STRONG_SECRET_KEY_HERE

# Domain
DOMAIN=workmate.yourdomain.com

# Database
DATABASE_URL=postgresql://workmate:STRONG_PASSWORD@postgres:5432/workmate

# Redis
REDIS_URL=redis://redis:6379/0

# Celery
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/1

# AI Services
ANTHROPIC_API_KEY=your-production-api-key
# OR for self-hosted:
# OLLAMA_URL=http://ollama:11434
# OLLAMA_MODEL=llama3.1:8b

# File Storage
STORAGE_BACKEND=s3  # or 'local'
# For S3:
AWS_ACCESS_KEY_ID=your-key
AWS_SECRET_ACCESS_KEY=your-secret
AWS_S3_BUCKET=workmate-files
AWS_REGION=eu-central-1

# Email
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=noreply@yourdomain.com
SMTP_PASSWORD=app-specific-password
EMAIL_FROM=noreply@yourdomain.com

# Encryption
ENCRYPTION_KEY=GENERATE_WITH_FERNET

# CORS
CORS_ORIGINS=["https://workmate.yourdomain.com"]
```

**Generate Secrets:**
```bash
# SECRET_KEY
openssl rand -hex 32

# ENCRYPTION_KEY (Fernet)
python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

### 3. Production Docker Compose

**docker-compose.production.yml:**
```yaml
version: '3.8'

services:
  postgres:
    image: postgres:14-alpine
    restart: always
    environment:
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: ${POSTGRES_DB}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - workmate

  redis:
    image: redis:7-alpine
    restart: always
    command: redis-server --requirepass ${REDIS_PASSWORD}
    volumes:
      - redis_data:/data
    networks:
      - workmate

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile.production
    restart: always
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000
    volumes:
      - ./data:/app/data
    depends_on:
      - postgres
      - redis
    env_file:
      - .env.production
    networks:
      - workmate
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  celery:
    build:
      context: ./backend
      dockerfile: Dockerfile.production
    restart: always
    command: celery -A app.celery worker --loglevel=info --concurrency=4
    volumes:
      - ./data:/app/data
    depends_on:
      - redis
      - postgres
    env_file:
      - .env.production
    networks:
      - workmate

  celery-beat:
    build:
      context: ./backend
      dockerfile: Dockerfile.production
    restart: always
    command: celery -A app.celery beat --loglevel=info
    depends_on:
      - redis
    env_file:
      - .env.production
    networks:
      - workmate

  nginx:
    image: nginx:alpine
    restart: always
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./nginx/ssl:/etc/nginx/ssl
      - ./frontend/build:/usr/share/nginx/html
    depends_on:
      - backend
    networks:
      - workmate

volumes:
  postgres_data:
  redis_data:

networks:
  workmate:
    driver: bridge
```

### 4. Nginx Configuration

**nginx/nginx.conf:**
```nginx
upstream backend {
    server backend:8000;
}

# HTTP → HTTPS Redirect
server {
    listen 80;
    server_name workmate.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

# HTTPS Server
server {
    listen 443 ssl http2;
    server_name workmate.yourdomain.com;

    # SSL Certificates
    ssl_certificate /etc/nginx/ssl/fullchain.pem;
    ssl_certificate_key /etc/nginx/ssl/privkey.pem;
    
    # SSL Configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # Security Headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    # API Backend
    location /api {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # WebSocket
    location /ws {
        proxy_pass http://backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }

    # Frontend (Flutter Web)
    location / {
        root /usr/share/nginx/html;
        try_files $uri $uri/ /index.html;
    }

    # File uploads
    client_max_body_size 20M;
}
```

### 5. SSL Certificates

**Option A: Let's Encrypt (Free)**
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d workmate.yourdomain.com

# Auto-renewal (cron)
sudo crontab -e
# Add: 0 0 * * * certbot renew --quiet
```

**Option B: Self-Signed (Development)**
```bash
mkdir -p nginx/ssl
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout nginx/ssl/privkey.pem \
  -out nginx/ssl/fullchain.pem \
  -subj "/CN=workmate.local"
```

### 6. Deploy
```bash
# Build and start
docker compose -f docker-compose.production.yml up -d

# Check logs
docker compose logs -f backend

# Run migrations
docker compose exec backend alembic upgrade head

# Create admin user
docker compose exec backend python scripts/create_admin.py
```

### 7. Verify Deployment
```bash
# Check health
curl https://workmate.yourdomain.com/api/health

# Expected: {"status":"ok","version":"0.1.0"}

# Check services
docker compose ps

# All should be "Up" and healthy
```

---

## Option 2: Manual Deployment (VPS)

### 1. Install Dependencies
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python
sudo apt install python3.11 python3.11-venv python3-pip

# Install PostgreSQL
sudo apt install postgresql postgresql-contrib

# Install Redis
sudo apt install redis-server

# Install Nginx
sudo apt install nginx
```

### 2. Setup Database
```bash
# Create database
sudo -u postgres psql
CREATE DATABASE workmate;
CREATE USER workmate WITH PASSWORD 'strong_password';
GRANT ALL PRIVILEGES ON DATABASE workmate TO workmate;
\q
```

### 3. Deploy Backend
```bash
# Create app user
sudo useradd -m -s /bin/bash workmate

# Clone repo
sudo -u workmate git clone https://github.com/commanderphu/workmate-private.git /home/workmate/app
cd /home/workmate/app

# Create venv
sudo -u workmate python3.11 -m venv venv

# Install dependencies
sudo -u workmate venv/bin/pip install -r backend/requirements.txt

# Copy config
sudo -u workmate cp .env.example .env
sudo -u workmate nano .env

# Run migrations
sudo -u workmate venv/bin/alembic upgrade head
```

### 4. Systemd Services

**backend.service:**
```ini
[Unit]
Description=Workmate Private Backend
After=network.target postgresql.service redis.service

[Service]
Type=simple
User=workmate
WorkingDirectory=/home/workmate/app/backend
Environment="PATH=/home/workmate/app/venv/bin"
ExecStart=/home/workmate/app/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

**celery-worker.service:**
```ini
[Unit]
Description=Workmate Celery Worker
After=network.target redis.service

[Service]
Type=simple
User=workmate
WorkingDirectory=/home/workmate/app/backend
Environment="PATH=/home/workmate/app/venv/bin"
ExecStart=/home/workmate/app/venv/bin/celery -A app.celery worker --loglevel=info
Restart=always

[Install]
WantedBy=multi-user.target
```

**celery-beat.service:**
```ini
[Unit]
Description=Workmate Celery Beat
After=network.target redis.service

[Service]
Type=simple
User=workmate
WorkingDirectory=/home/workmate/app/backend
Environment="PATH=/home/workmate/app/venv/bin"
ExecStart=/home/workmate/app/venv/bin/celery -A app.celery beat --loglevel=info
Restart=always

[Install]
WantedBy=multi-user.target
```

**Enable & Start:**
```bash
sudo systemctl enable backend celery-worker celery-beat
sudo systemctl start backend celery-worker celery-beat

# Check status
sudo systemctl status backend
```

### 5. Configure Nginx

Use same config as Docker section, but:
```nginx
upstream backend {
    server 127.0.0.1:8000;
}
```
```bash
sudo ln -s /etc/nginx/sites-available/workmate /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

---

## Option 3: Kubernetes

**Coming soon - for large-scale deployments**

---

## Monitoring

### 1. Prometheus + Grafana

**docker-compose.monitoring.yml:**
```yaml
version: '3.8'

services:
  prometheus:
    image: prom/prometheus
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    ports:
      - "9090:9090"
    networks:
      - workmate

  grafana:
    image: grafana/grafana
    volumes:
      - grafana_data:/var/lib/grafana
    ports:
      - "3001:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    networks:
      - workmate

volumes:
  prometheus_data:
  grafana_data:
```

### 2. Logs

**Centralized Logging with Loki:**
```bash
docker plugin install grafana/loki-docker-driver:latest --alias loki --grant-all-permissions

# Add to docker-compose:
logging:
  driver: loki
  options:
    loki-url: "http://localhost:3100/loki/api/v1/push"
```

**View Logs:**
```bash
# Docker Compose
docker compose logs -f backend

# Systemd
sudo journalctl -u backend -f
```

---

## Backup & Restore

### Database Backup

**Automated Backup Script:**
```bash
#!/bin/bash
# backup.sh

BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# PostgreSQL
docker compose exec -T postgres pg_dump -U workmate workmate > "$BACKUP_DIR/db_$DATE.sql"

# Files
tar -czf "$BACKUP_DIR/files_$DATE.tar.gz" ./data

# Cleanup old backups (keep 30 days)
find $BACKUP_DIR -name "*.sql" -mtime +30 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete

echo "Backup completed: $DATE"
```

**Cron Job:**
```bash
# Daily at 2 AM
0 2 * * * /home/workmate/backup.sh >> /var/log/workmate-backup.log 2>&1
```

### Restore
```bash
# Stop services
docker compose down

# Restore database
cat backup.sql | docker compose exec -T postgres psql -U workmate workmate

# Restore files
tar -xzf files_backup.tar.gz -C ./data

# Start services
docker compose up -d
```

---

## Updates

### Update Deployment
```bash
# Pull latest code
cd /home/workmate/app
git pull origin main

# Rebuild (Docker)
docker compose -f docker-compose.production.yml build
docker compose -f docker-compose.production.yml up -d

# OR (Manual)
sudo -u workmate venv/bin/pip install -r backend/requirements.txt
sudo -u workmate venv/bin/alembic upgrade head
sudo systemctl restart backend celery-worker
```

### Zero-Downtime Updates

**Blue-Green Deployment:**
```bash
# Run new version on different port
docker compose -f docker-compose.blue.yml up -d

# Test new version
curl http://localhost:8001/api/health

# Switch Nginx upstream
# Update nginx.conf: server backend:8001;
sudo nginx -s reload

# Stop old version
docker compose -f docker-compose.green.yml down
```

---

## Security Checklist

### Pre-Deployment

- [ ] Strong SECRET_KEY generated
- [ ] Strong database passwords
- [ ] ENCRYPTION_KEY generated
- [ ] DEBUG=false in production
- [ ] HTTPS enabled with valid certificate
- [ ] Firewall configured (only 80, 443 open)
- [ ] SSH key-based authentication only
- [ ] Fail2ban installed
- [ ] Regular security updates enabled

### Post-Deployment

- [ ] Change default admin password
- [ ] Test all integrations
- [ ] Configure backups
- [ ] Setup monitoring alerts
- [ ] Test restore procedure
- [ ] Document deployment

---

## Troubleshooting

### Service Won't Start
```bash
# Check logs
docker compose logs backend

# Check systemd
sudo journalctl -u backend -n 50

# Common issues:
# - Database not accessible → check DATABASE_URL
# - Redis not accessible → check REDIS_URL
# - Port already in use → check with: lsof -i :8000
```

### Database Connection Failed
```bash
# Test connection
docker compose exec postgres psql -U workmate -d workmate

# Check PostgreSQL logs
docker compose logs postgres
```

### High Memory Usage
```bash
# Check memory
docker stats

# Reduce Celery workers
# In docker-compose: --concurrency=2
```

### Slow Response Times
```bash
# Check backend logs for slow queries
# Enable query logging in PostgreSQL
# Add indexes for common queries
```

---

## Performance Tuning

### PostgreSQL

**postgresql.conf:**
```conf
shared_buffers = 256MB
effective_cache_size = 1GB
maintenance_work_mem = 64MB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
random_page_cost = 1.1
work_mem = 4MB
```

### Nginx
```nginx
# Worker processes
worker_processes auto;

# Connections
worker_connections 1024;

# Caching
proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=my_cache:10m max_size=1g inactive=60m;
proxy_cache my_cache;
proxy_cache_valid 200 60m;
```

---

## Support

**Issues:** https://github.com/commanderphu/workmate-private/issues  
**Discussions:** https://github.com/commanderphu/workmate-private/discussions  
**Docs:** https://workmate.private/docs