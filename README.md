# Workmate Private

> **Dein digitaler Arbeitskollege. Von einem Neurodivergenten für die Neurodivergenten.**

![Status: In Development](https://img.shields.io/badge/status-in%20development-yellow)
![License: MIT](https://img.shields.io/badge/license-MIT-blue)
![Made with ❤️ for ADHD](https://img.shields.io/badge/made%20with%20%E2%9D%A4%EF%B8%8F%20for-ADHD-ff69b4)
![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen)

## 🎯 Was ist Workmate Private?

Ein intelligentes Organisationssystem, das speziell für Menschen mit ADHD entwickelt wurde. Workmate Private hilft dir dabei, keine Rechnungen mehr zu vergessen, keine Fristen zu verpassen und den Papierkram endlich in den Griff zu bekommen – ohne dass du dich selbst „zusammenreißen" musst.

## 💡 Die Idee dahinter

Die Welt wurde von und für neurotypische Menschen designt. Bürokratie, Dokumenten-Management, Fristen – alles Systeme, die uns Neurodivergente systematisch benachteiligen.

**Warum sollten wir uns ständig anpassen, wenn wir auch Systeme bauen können, die mit unserem Gehirn funktionieren statt dagegen?**

Workmate Private ist die Antwort darauf: Ein Tool, das nicht versucht, dich zu „reparieren", sondern dich enablet.

**[Mehr zur Vision →](docs/concept/vision.md)**

## ✨ Features

- 📄 **Intelligente Dokumenten-Erkennung** – Scanne Post per Handy oder Scanner, importiere Email-Anhänge
- 🤖 **KI-gestützte Analyse** – Erkennt automatisch Fristen, Beträge, Prioritäten und Dokumenten-Typen
- ⏰ **Proaktive Erinnerungen** – Nie wieder Mahnungen wegen vergessener Zahlungen
- 📅 **Kalender-Integration** – Termine und Deadlines werden automatisch eingetragen
- ⚠️ **SLA-Monitoring** – Kritische Fristen werden eskaliert, bevor es zu spät ist
- 🏠 **Smart Home Support** – Wichtige Erinnerungen auch über dein Zuhause (Lichter, Benachrichtigungen)
- 📱 **Android & Web** – Überall verfügbar, wo du bist

**[Alle Use Cases →](docs/concept/use-cases.md)**

## 🎯 Use Cases

### Post-Management
**Problem:** Brief kommt rein → wird zur Seite gelegt → verschwindet im Stapel → Mahnung  
**Lösung:** Scan → KI-Analyse → Auto-Reminder → Kalender → Eskalation bei kritischen Fristen

### Verträge & Kündigungsfristen
**Problem:** Kündigungsfrist verpasst, Vertrag verlängert sich automatisch  
**Lösung:** Vertragsdokumente scannen → KI erkennt Kündigungsfrist → Reminder 3 Monate vorher

### Online-Bestellungen
**Problem:** Bestellung vergessen, Paket kommt nicht oder steht irgendwo  
**Lösung:** Bestellbestätigung scannen → Liefertracking → Reminder wenn Paket fällig ist

### Arzttermine & Rezepte
**Problem:** Rezept läuft ab, Arzttermin vergessen  
**Lösung:** Rezept scannen → Ablaufdatum tracken → Rechtzeitige Erinnerung

**[Mehr Use Cases →](docs/concept/use-cases.md)**

## 🛠️ Tech Stack

*(Coming soon – aktuell in Planung)*

Geplant:
- **Backend:** Python, FastAPI
- **Frontend Web:** Vue.js
- **Mobile:** Android (Kotlin/Java)
- **KI:** Claude API für Dokumenten-Analyse
- **Datenbank:** PostgreSQL
- **Integrationen:** Paperless-ngx, CalDAV, Smart Home APIs

**[Tech-Stack Details →](docs/architecture/tech-stack.md)**

## 🚀 Quick Start

*(Coming soon – Projekt ist in aktiver Entwicklung)*

Das Projekt befindet sich aktuell in der Konzept- und Architekturphase. Ein funktionierender Prototyp folgt in den nächsten Monaten.

## 📚 Dokumentation

Die komplette Projekt-Dokumentation findest du im [`docs/`](docs/) Ordner:

### Concept
- [Vision & Philosophie](docs/concept/vision.md)
- [Warum für Neurodivergente?](docs/concept/why-neurodivergent.md)
- [Use Cases](docs/concept/use-cases.md)

### Architecture
- [System Overview](docs/architecture/system-overview.md)
- [Komponenten](docs/architecture/components.md)
- [Datenmodell](docs/architecture/data-model.md)
- [Tech Stack](docs/architecture/tech-stack.md)

### Features
- [Core Features](docs/features/core-features.md)
- [Document Scanner](docs/features/document-scanner.md)
- [AI Processor](docs/features/ai-processor.md)
- [Reminder Engine](docs/features/reminder-engine.md)
- **Integrationen:**
  - [Kalender](docs/features/integrations/calendar.md)
  - [Smart Home](docs/features/integrations/smart-home.md)
  - [Paperless-ngx](docs/features/integrations/paperless-ngx.md)

### Development
- [Setup Guide](docs/development/setup.md)
- [API Reference](docs/development/api-reference.md)
- [Deployment](docs/development/deployment.md)
- [Contributing](docs/development/contributing.md)

### Planning
- [Roadmap](docs/planning/roadmap.md)
- [Milestones](docs/planning/milestones.md)
- [Architecture Decisions](docs/planning/decisions.md)

## 🤝 Contributing

Workmate Private ist Open Source! Beiträge, Ideen und Feedback sind herzlich willkommen.

**[Contributing Guidelines →](CONTRIBUTING.md)**

Egal ob du Code beitragen, Features vorschlagen oder einfach nur deine ADHD-Erfahrungen teilen möchtest – jeder Input hilft!

## 🧪 Beta Testing

Workmate Private wird aktuell mit ausgewählten Beta-Testern entwickelt und getestet, die selbst von ADHD betroffen sind. Ihr Feedback fließt direkt in die Entwicklung ein und hilft dabei, ein Tool zu schaffen, das wirklich die Probleme löst, die wir täglich erleben.

**Du hast ADHD und würdest gerne testen?**  
Das Projekt befindet sich noch in einer frühen Phase, aber ich plane, das Beta-Programm in den kommenden Monaten zu erweitern. Bei Interesse kannst du dich gerne melden – je mehr echte Use Cases ich verstehe, desto besser wird das Tool.

## 📖 Die Story

Im Sommer 2020 wurde ich mit ADHD diagnostiziert. In den Jahren 2021/22 setzte ich mich intensiv mit dem Thema Neurodivergenz auseinander und kam zu einer wichtigen Erkenntnis:

**Die Welt wurde so designed, dass sie uns Neurodiverse systematisch aussortiert.**

Statt mich weiter anzupassen, stellte ich mir die Frage: **Warum bauen wir nicht Systeme, die uns inkludieren und uns in der aktuellen Welt enablen?**

Workmate Private ist meine Antwort darauf. Ein Tool, das aus persönlicher Erfahrung entstanden ist und das Problem an der Wurzel anpackt: Nicht wir müssen uns ändern, sondern die Systeme.

## 📄 Lizenz

MIT License *(coming soon)*

---

**Made with ❤️ by [CommanderPhu](https://github.com/commanderphu)**  
*Part of the Workmate ecosystem*