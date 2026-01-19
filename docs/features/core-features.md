# Core Features

## Overview

Workmate Private bietet eine durchgehende Feature-Suite, die speziell für Menschen mit ADHD entwickelt wurde. Jedes Feature ist darauf ausgelegt, kognitive Last zu reduzieren und proaktiv zu unterstützen.

---

## 1. Intelligente Dokumenten-Verarbeitung

### Beschreibung
Automatische Erkennung, Analyse und Verarbeitung von Dokumenten mit KI-Unterstützung.

### User Flow
```
1. User fotografiert Brief / scannt Dokument
2. Workmate analysiert automatisch:
   - Dokumenten-Typ
   - Wichtige Daten (Beträge, Fristen)
   - Handlungsnotwendigkeit
3. Erstellt automatisch Tasks
4. Synct mit Kalender
5. Scheduled Reminders
```

### Features
- **Multi-Input:** Handy-Kamera, Scanner, Email-Import
- **OCR:** Text-Extraktion aus Bildern/PDFs
- **KI-Klassifizierung:** Rechnung, Mahnung, Vertrag, Quittung
- **Metadaten-Extraktion:** Beträge, Daten, Absender, Rechnungsnummern
- **Confidence Score:** Zeigt Sicherheit der Erkennung

### ADHD-Benefit
✅ **Keine manuelle Eingabe** - Kein "Ich mach's später"  
✅ **Sofortige Verarbeitung** - Kein Vergessen  
✅ **Automatische Priorisierung** - Keine Überforderung

---

## 2. Proaktives Task-Management

### Beschreibung
Tasks werden nicht nur erstellt, sondern aktiv verwaltet mit automatischer Priorisierung und Eskalation.

### Features

**Task-Erstellung:**
- Automatisch aus Dokumenten
- Manuell durch User
- Aus Kalendern (optional)

**Task-Properties:**
- Titel, Beschreibung
- Deadline, Priorität
- Status (Offen, In Bearbeitung, Erledigt)
- Tags & Kategorien
- Betrag (falls relevant)

**Advanced Features:**
- **Dependencies:** "Task B erst nach Task A"
- **Sub-Tasks:** Große Tasks in Schritte aufteilen
- **Recurring Tasks:** Täglich, Wöchentlich, Monatlich
- **Templates:** Standard-Tasks für wiederkehrende Szenarien

### ADHD-Benefit
✅ **Struktur ohne Aufwand** - System organisiert für dich  
✅ **Kleine Schritte** - Sub-Tasks gegen Overwhelm  
✅ **Automatische Wiederholung** - Keine mentale Last

---

## 3. Dynamische Reminder mit Eskalation

### Beschreibung
Multi-Stage Reminders die intensiver werden, je näher die Deadline rückt.

### Eskalations-Logik

**7 Tage vorher:**
- Severity: Info
- Frequency: Einmalig
- Channels: Push

**2 Tage vorher:**
- Severity: Warning
- Frequency: Täglich
- Channels: Push + Email

**1 Tag vorher:**
- Severity: Urgent
- Frequency: Mehrmals täglich (9h, 13h, 17h, 20h)
- Channels: Push + Email + SMS

**Überfällig:**
- Severity: Critical
- Frequency: Stündlich
- Channels: Push + Email + SMS + Smart Home

### Smart Features
- **Quiet Hours:** Keine Reminders nachts (22:00-07:00)
- **Timezone-Aware:** Berücksichtigt User-Zeitzone
- **Snooze:** Reminder verschieben
- **Acknowledge:** Bestätigen ohne zu erledigen

### ADHD-Benefit
✅ **Unmöglich zu ignorieren** - Eskalation verhindert Vergessen  
✅ **Kontextuelle Infos** - "Rechnung 89€, Telekom" statt nur "Rechnung"  
✅ **Multi-Channel** - Erreicht dich überall

---

## 4. Multi-Channel Benachrichtigungen

### Beschreibung
Benachrichtigungen über verschiedene Kanäle, je nach Dringlichkeit und User-Präferenz.

### Verfügbare Channels

**📱 Push Notifications**
- In-App Notifications
- Native OS-Notifications
- Badge Count
- Sound & Vibration

**📧 Email**
- HTML Templates
- Action Buttons
- Attachment Support

**💬 SMS**
- Für kritische Reminders
- Optional (Kosten!)
- Kurz & prägnant

**💬 Messaging Apps**
- **Telegram:** Bot-Integration
- **WhatsApp:** Business API
- **Discord:** Webhook
- **Signal:** API

**🏠 Smart Home**
- **Home Assistant:** Light, Speaker, Display
- **MQTT:** Custom Devices
- **Beispiele:**
  - Lichter blinken rot
  - Ankündigung über Lautsprecher
  - Display zeigt Reminder

### Channel Selection Logic
```python
if priority == "critical":
    channels = ["push", "email", "sms", "smart_home"]
elif priority == "high":
    channels = ["push", "email", "smart_home"]
elif priority == "medium":
    channels = ["push", "email"]
else:
    channels = ["push"]
```

### User Configuration
User kann pro Task-Typ Channels konfigurieren:
```json
{
  "invoice": ["push", "email"],
  "reminder": ["push", "email", "sms", "smart_home"],
  "contract": ["push", "email"],
  "receipt": ["push"]
}
```

### ADHD-Benefit
✅ **Erreichbarkeit** - Da wo du bist  
✅ **Redundanz** - Mehrere Kanäle = schwerer zu ignorieren  
✅ **Physische Alerts** - Smart Home spricht ADHD-Gehirn anders an

---

## 5. SLA-Monitoring & Priorisierung

### Beschreibung
Automatisches Tracking von Fristen mit dynamischer Prioritäts-Berechnung.

### Priority Algorithm

**Faktoren:**
1. **Zeit bis Deadline**
   - < 0 Tage (überfällig): +100
   - < 1 Tag: +80
   - < 2 Tage: +60
   - < 7 Tage: +40
   - >= 7 Tage: +20

2. **Dokumenten-Typ Multiplier**
   - Mahnung: 1.5x
   - Vertrag: 1.3x
   - Rechnung: 1.2x
   - Quittung: 1.0x

3. **Betrag Factor**
   - > 500€: 1.3x
   - > 100€: 1.1x
   - < 100€: 1.0x

**Finale Priorität:**
```
score = time_score * type_multiplier * amount_factor

if score >= 80: CRITICAL
elif score >= 60: HIGH
elif score >= 40: MEDIUM
else: LOW
```

### Status Levels
- **OK:** > 7 Tage bis Deadline
- **Warning:** 2-7 Tage
- **Urgent:** < 2 Tage
- **Critical:** < 24h oder überfällig

### ADHD-Benefit
✅ **Automatische Priorisierung** - Kein "Was ist wichtiger?"  
✅ **Transparente Logik** - User versteht warum was dringend ist  
✅ **Proaktive Warnung** - Bevor es zu spät ist

---

## 6. Kalender-Integration

### Beschreibung
Two-Way Synchronisation mit externen Kalendern.

### Supported Calendars
- **CalDAV:** Nextcloud, ownCloud, Apple Calendar
- **Google Calendar:** Direct API
- **Microsoft Outlook:** Graph API
- **Apple Calendar:** CalDAV

### Sync Modes

**One-Time Sync:**
- Manuell getriggert
- Nützlich für initiales Setup

**Periodic Sync:**
- Alle 15 Minuten
- Background Job

**Real-Time (Webhooks):**
- Google Calendar Push Notifications
- Outlook Subscriptions
- Instant Updates

### Conflict Resolution

**Szenario:** Task in Workmate geändert, Event in Google auch geändert

**Options:**
1. **Keep Local** - Workmate überschreibt
2. **Keep Remote** - Google überschreibt
3. **Manual Merge** - User entscheidet

**UI:**
```
Konflikt erkannt!

Workmate:  "Telekom Rechnung" - 25.01. 10:00
Google:    "Telekom bezahlen" - 25.01. 14:00

[Keep Workmate] [Keep Google] [Manual Merge]
```

### ADHD-Benefit
✅ **Zentrale Übersicht** - Alles an einem Ort  
✅ **Flexibilität** - Nutze deinen liebsten Kalender  
✅ **Keine Doppelarbeit** - Sync ist automatisch

---

## 7. Smart Home Integration

### Beschreibung
Physische Erinnerungen über Smart Home Devices.

### Use Cases

**Kritische Reminder:**
- Lichter blinken rot
- Lautsprecher Ankündigung
- Display zeigt Task

**Beispiel-Szenario:**
```
Task: "Telekom Rechnung fällig in 2 Stunden!"

→ Home Assistant triggert:
  - Office Light: Rot blinken 3x
  - Google Home: "Erinnerung: Telekom Rechnung fällig!"
  - Smart Display: Zeigt Task-Details
```

### Supported Platforms

**Home Assistant:**
- REST API Integration
- Services: light, switch, notify, tts
- Automations

**MQTT:**
- Publish to Topics
- Custom Devices
- Flexible

### Configuration Example
```yaml
# Home Assistant Automation
automation:
  - alias: "Workmate Critical Reminder"
    trigger:
      platform: webhook
      webhook_id: workmate_critical
    action:
      - service: light.turn_on
        target:
          entity_id: light.office
        data:
          color_name: red
          brightness: 255
      - delay: 00:00:01
      - service: light.turn_off
        target:
          entity_id: light.office
      - repeat:
          count: 2
          sequence:
            - service: light.turn_on
              target:
                entity_id: light.office
            - delay: 00:00:01
            - service: light.turn_off
              target:
                entity_id: light.office
      - service: tts.google_say
        data:
          message: "{{ trigger.json.message }}"
```

### ADHD-Benefit
✅ **Physische Reize** - Nicht ignorierbar  
✅ **Multisensorisch** - Sehen + Hören  
✅ **Im Raum präsent** - Nicht nur auf Screen

---

## 8. Paperless-ngx Integration

### Beschreibung
Optionale Integration mit bestehenden Paperless-ngx Installationen.

### Features

**Document Import:**
- Automatischer Import aus Paperless
- Mapping: Paperless Document → Workmate Document
- Metadaten übernehmen

**Two-Way Sync:**
- Workmate → Paperless: Tags, Custom Fields
- Paperless → Workmate: Neue Dokumente

**Benefits:**
- Nutze bestehende Paperless-Infrastruktur
- Workmate als "smarte Layer" on top
- Keine Duplizierung

### ADHD-Benefit
✅ **Nutzt bestehendes System** - Keine Migration nötig  
✅ **Best of both worlds** - Paperless Archiv + Workmate Intelligenz

---

## 9. Intelligente Suche & Filter

### Beschreibung
Schnelles Finden von Dokumenten und Tasks, auch mit Tippfehlern.

### Search Modes

**Simple Search:**
- Titel, Beschreibung
- Exakte Matches

**Full-Text Search:**
- Durchsucht Dokumenten-Content
- PostgreSQL Full-Text
- Ranking nach Relevanz

**Fuzzy Search:**
- Tippfehler-tolerant
- Levenshtein Distance
- "Telkom" findet "Telekom"

### Smart Filters

**Vordefiniert:**
- "Überfällige Tasks"
- "Offene Rechnungen"
- "Tasks diese Woche"
- "Verträge mit Kündigungsfrist < 3 Monate"

**Kombinierbar:**
```
Status: Open
Priority: High
Due Date: This Week
Amount: > 50€
```

### Quick Search Examples
```
"telekom rechnung"          → Findet alle Telekom-Rechnungen
"überfällig >100"           → Überfällige Tasks über 100€
"vertrag kündigung"         → Verträge mit Kündigungsfrist
"tag:wichtig status:open"   → Offene wichtige Tasks
```

### ADHD-Benefit
✅ **Schnelles Finden** - Keine frustrierte Suche  
✅ **Fehlertoleranz** - Tippfehler OK  
✅ **Smart Filters** - Komplexe Suchen einfach gemacht

---

## 10. Analytics & Motivation

### Beschreibung
Visualisierung von Fortschritt und Erfolgen zur Motivation.

### Stats Dashboard

**Overview:**
- Total Tasks (Open, Done, Overdue)
- Documents by Type
- This Week: Completed Tasks
- Average Completion Time

**Charts:**
- Task Completion (7/30 Tage Line Chart)
- Document Types (Pie Chart)
- Priority Distribution (Bar Chart)

### Achievements (Gamification)

**Examples:**
- 🎉 **Task Master:** 10 Tasks erledigt
- ⭐ **Perfect Week:** Keine überfälligen Tasks
- 🔥 **Streak:** 5 Tage in Folge Tasks erledigt
- 💪 **Speedrunner:** Task in < 1 Tag erledigt
- 📚 **Archivar:** 50 Dokumente verarbeitet

### Progress Indicators
```
This Week:  ████████░░ 80% (8/10 Tasks)
This Month: ██████░░░░ 60% (24/40 Tasks)

Streak: 🔥 5 days
```

### ADHD-Benefit
✅ **Sichtbarer Fortschritt** - Dopamin-Kick  
✅ **Gamification** - Macht Aufgaben "fun"  
✅ **Positive Verstärkung** - Fokus auf Erfolge

---

## Feature Priority Matrix

### MVP (Must-Have)
1. ✅ Dokumenten-Verarbeitung
2. ✅ Task-Management (Basic)
3. ✅ Reminders (Basic)
4. ✅ Push Notifications
5. ✅ Kalender-Sync (CalDAV)

### Phase 2 (Should-Have)
6. ✅ Eskalations-Logik
7. ✅ Email Notifications
8. ✅ Tags & Filter
9. ✅ Search
10. ✅ Analytics (Basic)

### Phase 3 (Nice-to-Have)
11. ✅ Smart Home Integration
12. ✅ Messaging Apps (Telegram, etc.)
13. ✅ Paperless-ngx Integration
14. ✅ Dependencies & Sub-Tasks
15. ✅ Recurring Tasks

### Future
16. 🔮 AI-Suggestions ("Du vergisst oft X")
17. 🔮 Voice Input
18. 🔮 Collaborative Tasks
19. 🔮 Budget-Tracking
20. 🔮 Banking Integration

---

## Zusammenfassung

Workmate Private kombiniert:
- **Intelligente Automation** → Weniger manuelle Arbeit
- **Proaktive Unterstützung** → System denkt mit
- **Multi-Channel Delivery** → Erreicht dich überall
- **ADHD-optimiertes Design** → Mit deinem Gehirn, nicht dagegen

**Das Resultat:** Ein digitaler Partner, der dich nie vergisst.