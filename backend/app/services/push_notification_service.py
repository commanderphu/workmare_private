"""
Firebase Cloud Messaging (FCM) push notification service
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)

_firebase_initialized = False


def _init_firebase() -> bool:
    global _firebase_initialized
    if _firebase_initialized:
        return True

    from ..core.config import settings
    if not settings.FIREBASE_CREDENTIALS_PATH:
        logger.warning("FIREBASE_CREDENTIALS_PATH not set – push notifications disabled")
        return False

    try:
        import firebase_admin
        from firebase_admin import credentials
        cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS_PATH)
        firebase_admin.initialize_app(cred)
        _firebase_initialized = True
        return True
    except Exception as e:
        logger.error(f"Firebase init failed: {e}")
        return False


class PushNotificationService:

    def send(
        self,
        fcm_token: str,
        title: str,
        body: str,
        data: Optional[dict] = None,
    ) -> bool:
        """
        Send a push notification to a single device.
        Returns True on success, False on failure.
        """
        if not _init_firebase():
            return False

        try:
            from firebase_admin import messaging

            message = messaging.Message(
                notification=messaging.Notification(title=title, body=body),
                data={k: str(v) for k, v in (data or {}).items()},
                token=fcm_token,
                android=messaging.AndroidConfig(
                    priority="high",
                    notification=messaging.AndroidNotification(
                        icon="notification_icon",
                        color="#10b981",
                    ),
                ),
            )
            messaging.send(message)
            return True

        except Exception as e:
            logger.error(f"FCM send failed (token={fcm_token[:20]}...): {e}")
            return False

    def send_reminder(self, fcm_token: str, task_title: str, severity: str) -> bool:
        severity_labels = {
            "info": "Erinnerung",
            "warning": "Bald fällig",
            "urgent": "Dringend",
            "critical": "Kritisch – sofort handeln!",
        }
        title = severity_labels.get(severity, "Erinnerung")
        body = task_title
        return self.send(
            fcm_token=fcm_token,
            title=title,
            body=body,
            data={"severity": severity, "type": "reminder"},
        )
