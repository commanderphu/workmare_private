# Architecture Decision Records (ADR)

## Overview

This document tracks major technical and architectural decisions made during the development of Workmate Private.

**Format:** Lightweight ADR (not strict)  
**Purpose:** Document *why* decisions were made, not just *what*

---

## ADR-001: Projekt-Sprache Deutsch

**Date:** 2026-01-19  
**Status:** Accepted  
**Deciders:** Joshua

### Context
Workmate Private is built by a German developer (Joshua) for the ADHD community, with initial focus on German-speaking users.

### Decision
- **User-facing documentation:** German (README, concept, features)
- **Code, comments, commit messages:** English (industry standard)
- **Development docs:** English (for potential international contributors)

### Rationale
- Primary users are German ADHD community
- Code in English is standard practice
- Keeps codebase accessible to international developers
- Documentation can be translated later if needed

### Consequences
- German-speaking users feel more included
- Technical debt: May need translation later for growth
- Mixed language in repo (acceptable tradeoff)

---

## ADR-002: Flutter for Frontend

**Date:** 2026-01-19  
**Status:** Accepted  
**Deciders:** Joshua

### Context
Need cross-platform frontend (Web + Mobile). Options: React Native, Flutter, Separate apps.

### Decision
Use **Flutter** for all platforms (Web, Android, iOS).

### Rationale
**Pros:**
- Single codebase for Web + Mobile
- Native performance
- Material Design out-of-the-box (ADHD-friendly clean UI)
- Growing ecosystem
- Joshua wants to learn Dart/Flutter

**Cons:**
- New language (Dart) to learn
- Web support still maturing
- Larger bundle size than pure web

### Alternatives Considered
- **React Native:** More mature, but worse web support
- **Vue.js + Native apps:** Double work, harder to maintain
- **PWA only:** No native mobile features (camera, notifications)

### Consequences
- Faster development once initial learning curve passed
- Consistent UX across platforms
- Need to learn Dart (acceptable, Joshua wants this)

---

## ADR-003: Python + FastAPI for Backend

**Date:** 2026-01-19  
**Status:** Accepted  
**Deciders:** Joshua

### Context
Backend framework choice. Options: Django, FastAPI, Node.js, Go.

### Decision
Use **Python 3.11+ with FastAPI**.

### Rationale
**Pros:**
- Joshua already knows Python (from WorkmateOS)
- FastAPI is modern, async, fast
- Excellent AI/ML library ecosystem (anthropic, tesseract)
- Type hints + automatic API docs
- Easy to deploy

**Cons:**
- Slightly slower than Go/Rust (acceptable for our scale)

### Alternatives Considered
- **Django:** Too heavy, we don't need Django ORM/Admin
- **Node.js:** Would need to learn, Python better for AI integration
- **Go:** Faster, but steeper learning curve

### Consequences
- Fast development (familiar stack)
- Great AI integration
- May need optimization at scale (future problem)

---

## ADR-004: SQLite + PostgreSQL Hybrid

**Date:** 2026-01-19  
**Status:** Accepted  
**Deciders:** Joshua

### Context
Database choice for self-hosted vs cloud deployment.

### Decision
Support **both SQLite and PostgreSQL** via SQLAlchemy abstraction.

### Rationale
- **SQLite:** Perfect for self-hosted, zero config, single user
- **PostgreSQL:** Production-ready for cloud, multi-user, scaling
- SQLAlchemy makes this easy to support both

### Consequences
- More flexible for users
- Slightly more complex (need to test both)
- Migration path: SQLite → PostgreSQL easy

---

## ADR-005: Claude API + Ollama Dual Support

**Date:** 2026-01-19  
**Status:** Accepted  
**Deciders:** Joshua

### Context
AI for document analysis. Cloud vs Local.

### Decision
Support **both Claude API (cloud) and Ollama (local)** with strategy pattern.

### Rationale
**Claude API:**
- Best accuracy for document analysis
- Vision API for images
- Reliable, fast
- Costs money

**Ollama:**
- Privacy (local)
- Free
- Works offline
- Requires GPU for good performance

**Why both?**
- Users can choose based on needs
- Cost-conscious users use Ollama
- Privacy-focused users use Ollama
- Cloud users use Claude for best results

### Consequences
- More code complexity (strategy pattern)
- Need to test both
- Better user choice

---

## ADR-006: Open Source (MIT License)

**Date:** 2026-01-19  
**Status:** Accepted  
**Deciders:** Joshua

### Context
Licensing model for Workmate Private.

### Decision
**Open Source with MIT License** (final license TBD, leaning MIT).

### Rationale
**Why Open Source:**
- Trust & transparency for ADHD community
- Community contributions
- Give back to neuro community
- Portfolio piece for K.I.T. Solutions

**Why MIT (vs GPL):**
- More permissive
- Easier for others to integrate
- Not copyleft (users can fork & modify freely)

### Monetization Strategy
- Core = Free forever
- Optional paid hosted service
- Optional support/setup services
- Never paywall core ADHD features

### Consequences
- Can't prevent competitors from using code (acceptable)
- Community-driven development
- Goodwill in ADHD community

---

## ADR-007: Reminder Escalation Strategy

**Date:** 2026-01-19  
**Status:** Accepted  
**Deciders:** Joshua

### Context
How to ensure ADHD users don't ignore reminders?

### Decision
**Multi-stage escalation with increasing frequency and channels.**

**Stages:**
1. Info (7d before): 1x push
2. Warning (2d before): Daily, push + email
3. Urgent (<2d): 4x daily, push + email + SMS
4. Critical (overdue): Hourly, all channels + smart home

### Rationale
**ADHD-Specific:**
- Single reminder = easily ignored
- Escalation matches urgency perception
- Multi-channel = harder to miss
- Physical alerts (smart home) work better for ADHD

### Consequences
- More complex reminder logic
- Risk of annoying users (mitigated by quiet hours)
- Higher notification costs (SMS, API calls)
- **But:** Actually prevents forgotten deadlines

---

## ADR-008: Docker Compose for Deployment

**Date:** 2026-01-19  
**Status:** Accepted  
**Deciders:** Joshua

### Context
Deployment strategy for self-hosted users.

### Decision
Primary deployment method: **Docker Compose**.

### Rationale
**Pros:**
- Easy setup (one command)
- Consistent environment
- Portable
- Includes all services (postgres, redis, celery)
- Standard in self-hosting community

**Cons:**
- Requires Docker knowledge (acceptable, target audience is tech-savvy)

### Alternatives Considered
- **Manual install:** Too complex, too many dependencies
- **Kubernetes:** Overkill for single-user
- **Snap/Flatpak:** Limited, less flexible

### Consequences
- Great DX for self-hosters
- Need good Docker documentation
- Alternative manual install docs for advanced users

---

## ADR-009: Paperless-ngx as Optional Integration

**Date:** 2026-01-19  
**Status:** Accepted  
**Deciders:** Joshua

### Context
Many power users already use Paperless-ngx. Compete or integrate?

### Decision
**Integrate, don't compete.** Paperless-ngx is optional integration.

### Rationale
- Paperless is established, excellent at archiving
- We're better at proactive task management
- Integration = best of both worlds
- Avoids reinventing the wheel
- Target different use cases (archival vs action)

### Consequences
- More complex (but optional)
- Appeals to power users
- Positions Workmate as "smart layer" not replacement

---

## ADR-010: Home Assistant for Smart Home

**Date:** 2026-01-19  
**Status:** Accepted  
**Deciders:** Joshua

### Context
Smart home integration for physical reminders.

### Decision
Primary integration: **Home Assistant + MQTT**.

### Rationale
- Home Assistant is the leading open-source smart home platform
- MQTT is standard for IoT
- Both align with self-hosting philosophy
- Huge community, many integrations
- Privacy-focused

### Alternatives Considered
- **Direct device APIs:** Too many to support
- **Cloud services (Alexa/Google):** Privacy concerns
- **Custom protocol:** Reinventing wheel

### Consequences
- Powerful integration for those who use it
- Complex for non-Home-Assistant users (acceptable, it's optional)

---

## ADR-011: No Native Mobile Push (Yet)

**Date:** 2026-01-19  
**Status:** Accepted (Temporary)  
**Deciders:** Joshua

### Context
Push notifications on mobile require Firebase (Android) or APNs (iOS).

### Decision
**Phase 1: Use Flutter local notifications only.**  
**Phase 2+: Add Firebase for real push.**

### Rationale
- Local notifications work for MVP when app is running
- Firebase setup adds complexity
- Focus on core features first
- Can add later without breaking changes

### Consequences
- Reminders only work when app open (limitation)
- Need to add Firebase in Phase 2
- Users may complain (mitigated by email/SMS fallback)

---

## ADR-012: Monthly Roadmap Reviews

**Date:** 2026-01-19  
**Status:** Accepted  
**Deciders:** Joshua

### Context
ADHD makes long-term planning hard. How to stay on track?

### Decision
**Review roadmap monthly, adjust as needed.**

### Rationale
- Flexibility for ADHD brain
- Feedback-driven development
- No rigid deadlines = less stress
- Progress over perfection

### Consequences
- Roadmap is living document
- Dates are estimates, not promises
- Community understands this (ADHD-focused project)

---

## Template for New ADRs
```markdown
## ADR-XXX: Title

**Date:** YYYY-MM-DD  
**Status:** Proposed | Accepted | Deprecated | Superseded  
**Deciders:** Name(s)

### Context
What is the issue/decision to be made?

### Decision
What did we decide?

### Rationale
Why this decision?
- Pros
- Cons
- ADHD-specific considerations (if relevant)

### Alternatives Considered
What else did we think about?

### Consequences
What are the results (positive and negative)?
```

---

## Decision Status

- **Proposed:** Under discussion
- **Accepted:** Decided and implemented
- **Deprecated:** No longer relevant
- **Superseded:** Replaced by newer decision

---

**Living Document:** Decisions will be added as the project evolves.