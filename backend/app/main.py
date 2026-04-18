"""
Workmate Private Backend API
Intelligent document and task management for ADHD
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import time
import platform

from .core.config import settings
from .api.v1 import api_router
from .api.v1.files import router as files_router

START_TIME = time.time()

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Intelligent document and task management for ADHD",
    version=settings.VERSION,
    debug=settings.DEBUG,
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix=settings.API_V1_PREFIX)

# Include files router (outside /api/v1 for direct file access)
app.include_router(files_router, prefix="/files", tags=["files"])


@app.get("/")
def root():
    """Root endpoint - API info"""
    return {
        "message": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "Development" if settings.DEBUG else "Production",
        "docs": f"{settings.API_V1_PREFIX}/docs",
    }


@app.get("/health")
def health_check():
    """Health check endpoint - JSON"""
    uptime = int(time.time() - START_TIME)
    db_ok = _check_db()
    redis_ok = _check_redis()
    return {
        "status": "healthy" if db_ok and redis_ok else "degraded",
        "uptime_seconds": uptime,
        "environment": settings.ENVIRONMENT,
        "services": {"database": db_ok, "redis": redis_ok},
    }


@app.get("/health/ui", response_class=HTMLResponse)
def health_dashboard():
    """Health check dashboard"""
    uptime = int(time.time() - START_TIME)
    days, rem = divmod(uptime, 86400)
    hours, rem = divmod(rem, 3600)
    mins, secs = divmod(rem, 60)
    uptime_str = f"{days}d {hours}h {mins}m {secs}s" if days else f"{hours}h {mins}m {secs}s"

    db_ok = _check_db()
    redis_ok = _check_redis()
    all_ok = db_ok and redis_ok

    def badge(ok: bool) -> str:
        color = "#10b981" if ok else "#ef4444"
        text = "Online" if ok else "Offline"
        return f'<span style="background:{color};color:#fff;padding:4px 12px;border-radius:9999px;font-size:13px;font-weight:600">{text}</span>'

    status_color = "#10b981" if all_ok else "#f59e0b"
    status_text = "Healthy" if all_ok else "Degraded"

    return f"""<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta http-equiv="refresh" content="30">
<title>Workmate Private - Health</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;background:#0f172a;color:#e2e8f0;min-height:100vh;display:flex;align-items:center;justify-content:center}}
.card{{background:#1e293b;border-radius:16px;padding:40px;max-width:480px;width:100%;box-shadow:0 25px 50px rgba(0,0,0,.4)}}
.header{{text-align:center;margin-bottom:32px}}
.header h1{{font-size:20px;color:#94a3b8;font-weight:400;margin-bottom:8px}}
.status{{display:inline-flex;align-items:center;gap:10px;font-size:28px;font-weight:700}}
.dot{{width:14px;height:14px;border-radius:50%;background:{status_color};box-shadow:0 0 12px {status_color};animation:pulse 2s infinite}}
@keyframes pulse{{0%,100%{{opacity:1}}50%{{opacity:.5}}}}
.grid{{display:grid;gap:16px}}
.row{{display:flex;justify-content:space-between;align-items:center;padding:12px 16px;background:#0f172a;border-radius:10px}}
.row .label{{color:#94a3b8;font-size:14px}}
.row .value{{font-size:14px;font-weight:600}}
.footer{{text-align:center;margin-top:24px;color:#475569;font-size:12px}}
</style>
</head>
<body>
<div class="card">
  <div class="header">
    <h1>{settings.PROJECT_NAME}</h1>
    <div class="status"><span class="dot"></span> {status_text}</div>
  </div>
  <div class="grid">
    <div class="row"><span class="label">Uptime</span><span class="value">{uptime_str}</span></div>
    <div class="row"><span class="label">Version</span><span class="value">v{settings.VERSION}</span></div>
    <div class="row"><span class="label">Environment</span><span class="value">{settings.ENVIRONMENT}</span></div>
    <div class="row"><span class="label">Python</span><span class="value">{platform.python_version()}</span></div>
    <div class="row"><span class="label">Database</span>{badge(db_ok)}</div>
    <div class="row"><span class="label">Redis</span>{badge(redis_ok)}</div>
  </div>
  <div class="footer">Auto-refresh alle 30s</div>
</div>
</body>
</html>"""


def _check_db() -> bool:
    try:
        from .db.session import SessionLocal
        from sqlalchemy import text
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        return True
    except Exception:
        return False


def _check_redis() -> bool:
    try:
        import redis
        r = redis.from_url(settings.CELERY_BROKER_URL)
        r.ping()
        return True
    except Exception:
        return False
