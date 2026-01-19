# Reminder Engine

## Overview

Die Reminder Engine ist das proaktive Herzstück von Workmate Private. Sie sorgt dafür, dass keine Deadline vergessen wird durch intelligente, mehrstufige Erinnerungen mit dynamischer Eskalation.

---

## Core Concepts

### Multi-Stage Reminders

**Grundprinzip:** Je näher die Deadline, desto dringender und häufiger die Reminders.

**Stages:**
1. **Info** (7+ Tage vorher)
2. **Warning** (2-7 Tage vorher)
3. **Urgent** (< 2 Tage)
4. **Critical** (< 24h oder überfällig)

### Dynamic Escalation

**Frequency Escalation:**
- Info: Einmalig
- Warning: Täglich
- Urgent: Mehrmals täglich (4x)
- Critical: Stündlich

**Channel Escalation:**
- Info: Push
- Warning: Push + Email
- Urgent: Push + Email + SMS
- Critical: Push + Email + SMS + Smart Home

---

## Architecture
```
┌─────────────────────────────────────────────────┐
│          Reminder Engine Service                │
│                                                 │
│  ┌─────────────────────────────────────────┐   │
│  │      Reminder Scheduler (Celery)        │   │
│  └─────────────┬───────────────────────────┘   │
│                │                                │
│  ┌─────────────▼───────────────────────────┐   │
│  │      Escalation Calculator              │   │
│  └─────────────┬───────────────────────────┘   │
│                │                                │
│  ┌─────────────▼───────────────────────────┐   │
│  │      Notification Dispatcher            │   │
│  └─────────────┬───────────────────────────┘   │
│                │                                │
│  ┌─────────────▼───────────────────────────┐   │
│  │      SLA Monitor                        │   │
│  └─────────────────────────────────────────┘   │
└─────────────────────────────────────────────────┘
```

---

## Reminder Scheduling

### Task-Based Scheduling
```python
from datetime import datetime, timedelta
from typing import List

class ReminderScheduler:
    def schedule_for_task(self, task: Task) -> List[ReminderEvent]:
        """Generate reminder schedule for a task"""
        
        if not task.due_date:
            return []  # No reminders without deadline
        
        now = datetime.now()
        due = task.due_date
        delta_days = (due - now).days
        
        events = []
        
        # Stage 1: Info (7 days before)
        if delta_days >= 7:
            events.append(ReminderEvent(
                task_id=task.id,
                trigger_at=due - timedelta(days=7),
                severity=ReminderSeverity.INFO,
                channels=["push"],
                message=self._generate_message(task, "info")
            ))
        
        # Stage 2: Warning (2 days before, daily)
        if delta_days >= 2:
            for day in range(2, min(delta_days, 7)):
                events.append(ReminderEvent(
                    task_id=task.id,
                    trigger_at=due - timedelta(days=day),
                    severity=ReminderSeverity.WARNING,
                    channels=["push", "email"],
                    message=self._generate_message(task, "warning", days_left=day)
                ))
        
        # Stage 3: Urgent (last day, 4x)
        if delta_days >= 1:
            for hour in [9, 13, 17, 20]:
                trigger = due.replace(hour=hour, minute=0, second=0) - timedelta(days=1)
                if trigger > now:
                    events.append(ReminderEvent(
                        task_id=task.id,
                        trigger_at=trigger,
                        severity=ReminderSeverity.URGENT,
                        channels=["push", "email", "sms"],
                        message=self._generate_message(task, "urgent")
                    ))
        
        # Stage 4: Critical (overdue, hourly)
        if delta_days < 0:
            # Schedule next hour
            next_hour = (now + timedelta(hours=1)).replace(minute=0, second=0)
            events.append(ReminderEvent(
                task_id=task.id,
                trigger_at=next_hour,
                severity=ReminderSeverity.CRITICAL,
                channels=["push", "email", "sms", "smart_home"],
                message=self._generate_message(task, "critical", days_overdue=abs(delta_days))
            ))
        
        return events
```

### Message Generation
```python
def _generate_message(
    self,
    task: Task,
    severity: str,
    days_left: int = None,
    days_overdue: int = None
) -> str:
    """Generate contextual reminder message"""
    
    base = task.title
    
    if task.amount:
        base += f" ({task.amount:.2f} {task.currency})"
    
    if severity == "info":
        return f"ℹ️ Erinnerung: {base} in {days_left} Tagen fällig"
    
    elif severity == "warning":
        return f"⚠️ Achtung: {base} in {days_left} Tagen fällig!"
    
    elif severity == "urgent":
        return f"🔥 DRINGEND: {base} morgen fällig!"
    
    elif severity == "critical":
        if days_overdue == 0:
            return f"🚨 HEUTE FÄLLIG: {base}"
        else:
            return f"🚨 ÜBERFÄLLIG: {base} seit {days_overdue} Tagen!"
```

---

## Celery Background Jobs

### Periodic Task
```python
from celery import Celery
from celery.schedules import crontab

app = Celery('workmate')

app.conf.beat_schedule = {
    'check-reminders-every-5-minutes': {
        'task': 'workmate.tasks.check_and_send_reminders',
        'schedule': crontab(minute='*/5'),
    },
}

@app.task
async def check_and_send_reminders():
    """Check for due reminders and send them"""
    
    now = datetime.now()
    
    # Get all pending reminders that should trigger now
    reminders = await db.query(Reminder).filter(
        Reminder.status == ReminderStatus.PENDING,
        Reminder.trigger_at <= now
    ).all()
    
    for reminder in reminders:
        try:
            # Send notifications
            await notification_service.send_reminder(reminder)
            
            # Update status
            reminder.status = ReminderStatus.SENT
            reminder.sent_at = now
            await db.save(reminder)
            
            # If critical, schedule next reminder
            if reminder.severity == ReminderSeverity.CRITICAL:
                await _schedule_next_critical_reminder(reminder.task_id)
        
        except Exception as e:
            logger.error(f"Failed to send reminder {reminder.id}: {e}")
            reminder.status = ReminderStatus.FAILED
            reminder.error_message = str(e)
            await db.save(reminder)
```

### On-Demand Scheduling
```python
@app.task
async def schedule_reminders_for_task(task_id: UUID):
    """Schedule all reminders when task is created/updated"""
    
    task = await db.get_task(task_id)
    
    # Delete existing pending reminders
    await db.query(Reminder).filter(
        Reminder.task_id == task_id,
        Reminder.status == ReminderStatus.PENDING
    ).delete()
    
    # Generate new schedule
    scheduler = ReminderScheduler()
    events = scheduler.schedule_for_task(task)
    
    # Save to database
    for event in events:
        reminder = Reminder(
            task_id=task.id,
            trigger_at=event.trigger_at,
            severity=event.severity,
            channels=event.channels,
            message=event.message,
            status=ReminderStatus.PENDING
        )
        await db.save(reminder)
```

---

## Smart Features

### Quiet Hours
```python
class QuietHoursFilter:
    def should_send_now(
        self,
        reminder: Reminder,
        user: User
    ) -> bool:
        """Check if reminder should be sent considering quiet hours"""
        
        prefs = user.notification_preferences
        
        if not prefs.get("quiet_hours", {}).get("enabled", False):
            return True  # No quiet hours configured
        
        now = datetime.now(tz=timezone(user.timezone))
        quiet_start = prefs["quiet_hours"]["start"]  # "22:00"
        quiet_end = prefs["quiet_hours"]["end"]      # "07:00"
        
        current_time = now.time()
        start_time = datetime.strptime(quiet_start, "%H:%M").time()
        end_time = datetime.strptime(quiet_end, "%H:%M").time()
        
        # Check if in quiet period
        if start_time <= end_time:
            # Normal case: 22:00 - 07:00
            in_quiet = start_time <= current_time <= end_time
        else:
            # Overnight: 22:00 - 07:00 next day
            in_quiet = current_time >= start_time or current_time <= end_time
        
        if in_quiet:
            # Only send critical reminders during quiet hours
            return reminder.severity == ReminderSeverity.CRITICAL
        
        return True
    
    def reschedule_for_after_quiet_hours(
        self,
        reminder: Reminder,
        user: User
    ) -> datetime:
        """Reschedule reminder for after quiet hours"""
        
        prefs = user.notification_preferences
        quiet_end = prefs["quiet_hours"]["end"]
        
        next_send = datetime.now(tz=timezone(user.timezone)).replace(
            hour=int(quiet_end.split(":")[0]),
            minute=int(quiet_end.split(":")[1]),
            second=0
        )
        
        # If already past quiet end today, send tomorrow
        if next_send < datetime.now(tz=timezone(user.timezone)):
            next_send += timedelta(days=1)
        
        return next_send
```

### Snooze Functionality
```python
class ReminderSnoozeService:
    SNOOZE_OPTIONS = {
        "15min": timedelta(minutes=15),
        "1hour": timedelta(hours=1),
        "3hours": timedelta(hours=3),
        "tomorrow": timedelta(days=1),
        "next_week": timedelta(weeks=1)
    }
    
    async def snooze_reminder(
        self,
        reminder_id: UUID,
        snooze_duration: str
    ):
        """Snooze reminder for specified duration"""
        
        reminder = await db.get_reminder(reminder_id)
        
        if snooze_duration not in self.SNOOZE_OPTIONS:
            raise ValueError(f"Invalid snooze duration: {snooze_duration}")
        
        delta = self.SNOOZE_OPTIONS[snooze_duration]
        new_trigger = datetime.now() + delta
        
        # Update reminder
        reminder.trigger_at = new_trigger
        reminder.snoozed_until = new_trigger
        reminder.status = ReminderStatus.PENDING
        
        await db.save(reminder)
        
        logger.info(f"Reminder {reminder_id} snoozed until {new_trigger}")
```

### Acknowledge without Completing
```python
async def acknowledge_reminder(reminder_id: UUID):
    """User acknowledges reminder without completing task"""
    
    reminder = await db.get_reminder(reminder_id)
    reminder.acknowledged_at = datetime.now()
    await db.save(reminder)
    
    # Don't send more reminders for this severity level
    # But still escalate if deadline approaches
```

---

## SLA Integration

### Priority-Based Scheduling
```python
class PriorityAwareScheduler(ReminderScheduler):
    def schedule_for_task(self, task: Task) -> List[ReminderEvent]:
        """Adjust reminder frequency based on task priority"""
        
        events = super().schedule_for_task(task)
        
        if task.priority == TaskPriority.CRITICAL:
            # More frequent reminders
            events = self._increase_frequency(events)
        
        elif task.priority == TaskPriority.LOW:
            # Less frequent reminders
            events = self._decrease_frequency(events)
        
        return events
    
    def _increase_frequency(self, events: List[ReminderEvent]) -> List[ReminderEvent]:
        """Double the frequency for critical tasks"""
        new_events = []
        for event in events:
            new_events.append(event)
            # Add intermediate reminder
            if event.severity in [ReminderSeverity.WARNING, ReminderSeverity.URGENT]:
                intermediate = event.copy()
                intermediate.trigger_at += timedelta(hours=12)
                new_events.append(intermediate)
        return sorted(new_events, key=lambda e: e.trigger_at)
```

### Amount-Based Escalation
```python
def adjust_for_amount(self, task: Task, events: List[ReminderEvent]):
    """Escalate more aggressively for high-amount tasks"""
    
    if not task.amount:
        return events
    
    HIGH_AMOUNT_THRESHOLD = 500.0
    
    if task.amount >= HIGH_AMOUNT_THRESHOLD:
        # Start reminders earlier
        for event in events:
            if event.severity == ReminderSeverity.INFO:
                event.trigger_at -= timedelta(days=3)  # 10 days before instead of 7
        
        # Add SMS channel to warning stage
        for event in events:
            if event.severity == ReminderSeverity.WARNING:
                if "sms" not in event.channels:
                    event.channels.append("sms")
    
    return events
```

---

## User Interaction

### Reminder Actions API
```python
@app.post("/reminders/{reminder_id}/snooze")
async def snooze_reminder(
    reminder_id: UUID,
    duration: str = "1hour",
    current_user: User = Depends(get_current_user)
):
    """Snooze a reminder"""
    
    reminder = await db.get_reminder(reminder_id)
    
    if reminder.task.user_id != current_user.id:
        raise HTTPException(403, "Not authorized")
    
    await reminder_service.snooze_reminder(reminder_id, duration)
    
    return {"status": "snoozed", "until": reminder.snoozed_until}

@app.post("/reminders/{reminder_id}/acknowledge")
async def acknowledge_reminder(
    reminder_id: UUID,
    current_user: User = Depends(get_current_user)
):
    """Acknowledge reminder without completing task"""
    
    reminder = await db.get_reminder(reminder_id)
    
    if reminder.task.user_id != current_user.id:
        raise HTTPException(403, "Not authorized")
    
    await reminder_service.acknowledge_reminder(reminder_id)
    
    return {"status": "acknowledged"}

@app.post("/reminders/{reminder_id}/complete")
async def complete_task_from_reminder(
    reminder_id: UUID,
    current_user: User = Depends(get_current_user)
):
    """Mark task as complete from reminder"""
    
    reminder = await db.get_reminder(reminder_id)
    task = reminder.task
    
    if task.user_id != current_user.id:
        raise HTTPException(403, "Not authorized")
    
    # Complete task
    task.status = TaskStatus.DONE
    task.completed_at = datetime.now()
    await db.save(task)
    
    # Cancel all pending reminders for this task
    await db.query(Reminder).filter(
        Reminder.task_id == task.id,
        Reminder.status == ReminderStatus.PENDING
    ).update({Reminder.status: ReminderStatus.CANCELLED})
    
    return {"status": "completed"}
```

---

## Testing

### Unit Tests
```python
@pytest.mark.asyncio
async def test_reminder_schedule_generation():
    task = Task(
        id=uuid4(),
        title="Test Task",
        due_date=datetime.now() + timedelta(days=10),
        priority=TaskPriority.MEDIUM
    )
    
    scheduler = ReminderScheduler()
    events = scheduler.schedule_for_task(task)
    
    # Should have info stage (7 days)
    info_events = [e for e in events if e.severity == ReminderSeverity.INFO]
    assert len(info_events) == 1
    
    # Should have warning stages (2-6 days)
    warning_events = [e for e in events if e.severity == ReminderSeverity.WARNING]
    assert len(warning_events) == 5
    
    # Should have urgent stages (last day, 4x)
    urgent_events = [e for e in events if e.severity == ReminderSeverity.URGENT]
    assert len(urgent_events) == 4

@pytest.mark.asyncio
async def test_quiet_hours_filtering():
    user = User(
        timezone="Europe/Berlin",
        notification_preferences={
            "quiet_hours": {
                "enabled": True,
                "start": "22:00",
                "end": "07:00"
            }
        }
    )
    
    # Create reminder at 23:00
    reminder = Reminder(
        severity=ReminderSeverity.WARNING,
        trigger_at=datetime.now().replace(hour=23, minute=0)
    )
    
    filter = QuietHoursFilter()
    
    # Non-critical should not send
    assert not filter.should_send_now(reminder, user)
    
    # Critical should send even during quiet hours
    reminder.severity = ReminderSeverity.CRITICAL
    assert filter.should_send_now(reminder, user)
```

---

## Monitoring & Analytics

### Metrics
```python
class ReminderAnalytics:
    async def get_effectiveness_metrics(self, days: int = 30):
        """Calculate reminder effectiveness"""
        
        reminders = await db.get_reminders_in_period(days=days)
        
        total = len(reminders)
        sent = len([r for r in reminders if r.status == ReminderStatus.SENT])
        acknowledged = len([r for r in reminders if r.acknowledged_at])
        led_to_completion = len([
            r for r in reminders 
            if r.task.completed_at and r.task.completed_at > r.sent_at
        ])
        
        return {
            "total_reminders": total,
            "delivery_rate": sent / total if total > 0 else 0,
            "acknowledgment_rate": acknowledged / sent if sent > 0 else 0,
            "completion_rate": led_to_completion / sent if sent > 0 else 0,
            "avg_time_to_action": self._calculate_avg_time_to_action(reminders)
        }
```

---

## Zusammenfassung

**Reminder Engine Features:**
- ✅ Multi-Stage Escalation
- ✅ Dynamic Frequency
- ✅ Multi-Channel Delivery
- ✅ Quiet Hours Support
- ✅ Snooze & Acknowledge
- ✅ Priority-Aware
- ✅ Amount-Based Adjustment
- ✅ SLA Integration

**ADHD-Optimierung:**
- Unmöglich zu ignorieren
- Kontextuelle Messages
- Flexible User-Kontrolle
- Respektiert Ruhezeiten