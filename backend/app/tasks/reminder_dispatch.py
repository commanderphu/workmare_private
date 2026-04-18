"""
Celery beat task: dispatches due reminders every minute
"""

from ..celery import celery_app
from ..db.session import SessionLocal
from ..services.reminder_service import ReminderService
from ..services.push_notification_service import PushNotificationService
from ..models.user import User


@celery_app.task(name="app.tasks.dispatch_reminders")
def dispatch_reminders():
    """Check for due reminders and send push notifications."""
    db = SessionLocal()
    reminder_service = ReminderService()
    push_service = PushNotificationService()

    try:
        due = reminder_service.get_due_reminders(db)

        for reminder in due:
            task = reminder.task
            if not task:
                continue

            user = db.query(User).filter(User.id == task.user_id).first()
            if not user:
                continue

            sent = False
            error = None

            if "push" in (reminder.channels or []) and user.fcm_token:
                ok = push_service.send_reminder(
                    fcm_token=user.fcm_token,
                    task_title=task.title,
                    severity=reminder.severity,
                )
                sent = ok
                if not ok:
                    error = "FCM delivery failed"

            reminder_service.mark_reminder_sent(reminder, db, error=error if not sent else None)

        return {"dispatched": len(due)}

    finally:
        db.close()
