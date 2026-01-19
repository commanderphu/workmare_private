# Use Cases

## Überblick

Workmate Private löst konkrete, alltägliche Probleme, mit denen besonders Menschen mit ADHD konfrontiert sind. Diese Use Cases sind nicht theoretisch – sie basieren auf echten Erfahrungen und zeigen, wie Workmate Private im echten Leben hilft.

Jeder Use Case folgt dem gleichen Pattern:
1. **Problem** – Was ist die Herausforderung?
2. **ADHD-Context** – Warum ist das für ADHD besonders schwer?
3. **Current Workarounds** – Was machen Leute aktuell?
4. **Workmate Solution** – Wie löst Workmate Private es?
5. **Technical Flow** – Wie funktioniert es technisch?

---

## Use Case 1: Post-Management

### Problem
Ein Brief kommt an (Rechnung, Mahnung, Vertrag). Du legst ihn zur Seite, um ihn "später" zu bearbeiten. Der Brief verschwindet im Papierstapel. Die nächste Post kommt. Irgendwann kommt die Mahnung – oder schlimmer, der Inkasso-Brief.

### ADHD-Context
**"Aus den Augen, aus dem Sinn"** ist keine Redensart für uns, sondern neurologische Realität. Das ADHD-Gehirn hat massive Probleme mit:
- **Working Memory:** Brief weglegen = sofort vergessen
- **Time Blindness:** "Frist in 2 Wochen" fühlt sich an wie "irgendwann später"
- **Overwhelm:** Der Stapel wird größer → Vermeidung wird stärker
- **Priorisierung:** "Wichtig aber nicht dringend" registriert unser Gehirn nicht

### Current Workarounds
- ❌ "Ich leg's auf den Schreibtisch" → Verschwindet unter anderem Zeug
- ❌ "Ich mach's gleich" → Wird durch nächste Ablenkung ersetzt
- ❌ Reminder-Apps → "Rechnung bezahlen" ohne Kontext hilft nicht
- ❌ Partner/Familie bittet dich dran zu denken → Schafft Abhängigkeit und Frustration

Nichts davon funktioniert langfristig, weil sie alle davon ausgehen, dass **du** dich erinnerst.

### Workmate Solution

**Der Prozess:**

1. **Brief kommt an** – Du machst ein Foto mit dem Handy oder scannst ihn
2. **KI analysiert** – Workmate erkennt:
   - Dokumenten-Typ (Rechnung, Mahnung, Vertrag, etc.)
   - Betrag und Empfänger
   - Fälligkeitsdatum / Frist
   - Priorität / Dringlichkeit
3. **Auto-Reminder erstellt** – Basierend auf der Frist:
   - Rechnung fällig in 14 Tagen → Reminder 7 Tage vorher + 2 Tage vorher
   - Mahnung → Sofort hohe Priorität
4. **Kalender-Integration** – Termin wird automatisch eingetragen
5. **SLA-Monitoring** – Wenn kritisch wird:
   - Benachrichtigungen werden häufiger
   - Priorität steigt automatisch
   - Optional: Smart Home Integration (Licht blinkt, etc.)

**Du musst dich an nichts erinnern – Workmate übernimmt das.**

### Technical Flow
```
[Foto/Scan] → [Upload] → [Claude API: Dokumenten-Analyse] 
    ↓
[Extract: Type, Amount, Date, Priority]
    ↓
[Create Task in DB] → [Calendar Sync] → [Reminder Schedule]
    ↓
[SLA Monitor] → [Escalation Engine] → [Multi-Channel Notifications]
```

---

## Use Case 2: Verträge & Kündigungsfristen

### Problem
Du schließt einen Vertrag ab (Fitnessstudio, Handyvertrag, Versicherung). Im Kleingedruckten steht: "24 Monate Laufzeit, 3 Monate Kündigungsfrist zum Vertragsende". Klingt einfach? 

In der Realität: Du vergisst die Frist, der Vertrag verlängert sich automatisch um weitere 12-24 Monate. Du zahlst für etwas, das du nicht mehr willst.

### ADHD-Context
- **Future-Planning:** Unser Gehirn ist schlecht darin, 21 Monate im Voraus zu denken
- **Reminder-Überflutung:** Zu viele Reminder = alle werden ignoriert
- **"Ich mach's später":** Die Frist ist ja noch lang hin → vergessen
- **Impulsive Vertragsabschlüsse:** Im Moment klingt's gut, Konsequenzen werden nicht bedacht

### Current Workarounds
- ❌ "Ich trag's mir in den Kalender ein" → Wird beim Vertragsabschluss vergessen
- ❌ Excel-Tabelle mit Verträgen → Wird nie aktualisiert, gerät aus dem Blick
- ❌ Partner übernimmt es → Abhängigkeit, unangenehm

### Workmate Solution

1. **Vertragsdokument scannen** – Beim Unterschreiben direkt Foto machen
2. **KI extrahiert Daten:**
   - Vertragspartner
   - Laufzeit
   - Kündigungsfrist
   - Verlängerungsbedingungen
   - Monatliche Kosten
3. **Langfrist-Reminder:**
   - 4 Monate vor Ende: "Dein Vertrag läuft bald aus – willst du behalten oder kündigen?"
   - 3 Monate vor Ende: "Erinnerung: Kündigungsfrist läuft"
   - 2 Wochen vor Ende: "DRINGEND: Kündigungsfrist endet bald!"
4. **Kündigungsassistent:**
   - Kündigungsvorlage generieren
   - Empfängeradresse vorausfüllen
   - Versanddatum tracken

### Technical Flow
```
[Vertragsscan] → [KI-Analyse] → [Extract: Dates, Terms, Party]
    ↓
[Calculate: Contract End - 3 Months]
    ↓
[Schedule: Multi-Stage Reminders]
    ↓
[Optional: Generate Cancellation Letter]
```

---

## Use Case 3: Online-Bestellungen & Paket-Tracking

### Problem
Du bestellst online (Amazon, Kleinanzeigen, eBay). Bekommst Bestellbestätigung. Vergisst es. Paket kommt nicht. Du checkst erst nach Wochen "Moment, wo ist eigentlich...?"

Oder: Paket wird geliefert, du bist nicht da, Benachrichtigung im Briefkasten verschwindet → Paket geht zurück.

### ADHD-Context
- **Impulsive Käufe:** "Jetzt kaufen" ohne nachzudenken
- **Vergesslichkeit:** 5 Minuten nach Bestellung ist sie aus dem Kopf
- **Tracking-Chaos:** 5 verschiedene Shops, 5 verschiedene Tracking-Systeme
- **Postfiliale:** "Ich hol's morgen ab" → wird zu "irgendwann" → zurück an Absender

### Current Workarounds
- ❌ Bestellbestätigungs-Emails durchsuchen → Unübersichtlich
- ❌ Jedes Tracking einzeln checken → Zeitaufwändig
- ❌ "Ich hab's bestellt, irgendwann kommt's" → Oder halt nicht

### Workmate Solution

1. **Bestellbestätigung scannen** (Email-Anhang oder Screenshot)
2. **KI extrahiert:**
   - Artikel
   - Shop
   - Bestellnummer
   - Erwartete Lieferzeit
3. **Tracking-Integration:**
   - Automatisches Tracking über APIs (DHL, DPD, Hermes, etc.)
   - Status-Updates als Benachrichtigungen
4. **Proaktive Reminders:**
   - "Paket sollte heute ankommen – bist du zuhause?"
   - "Paket liegt bei Postfiliale, Abholung bis [Datum]"
   - "Paket ist überfällig – Shop kontaktieren?"

### Technical Flow
```
[Email/Screenshot] → [Parse: Order Details, Tracking Number]
    ↓
[Identify: Carrier] → [API Integration: DHL/DPD/etc]
    ↓
[Status Monitoring] → [Push Notifications]
    ↓
[Deadline Detection] → [Escalation Reminders]
```

---

## Use Case 4: Arzttermine & Rezepte

### Problem
**Arzttermine:** Termin in 3 Wochen gemacht. Vergessen. Nicht hingegangen. Praxis ist sauer.

**Rezepte:** Rezept bekommen. Einlösen vergessen. Medikamente gehen aus. Dann erst einlösen, aber Rezept ist abgelaufen.

### ADHD-Context
- **Time Blindness:** "3 Wochen" fühlt sich an wie "Ewigkeit"
- **Rezept-Overwhelm:** "Ich mach's gleich" → liegt 2 Monate rum
- **Apotheken-Gang:** Braucht Executive Function, die oft fehlt
- **Konsequenzen:** Ohne Medikamente → ADHD wird schlimmer → Teufelskreis

### Current Workarounds
- ❌ Arzt-Reminder-Anruf → Kommt oft nicht oder zu kurzfristig
- ❌ Rezept an Kühlschrank kleben → Fällt ab, verschwindet
- ❌ "Ich hab noch genug Pillen" → Bis plötzlich nicht mehr

### Workmate Solution

**Arzttermine:**
1. Terminkarte fotografieren oder Email scannen
2. KI extrahiert: Datum, Uhrzeit, Praxis, Adresse
3. Reminder-Kette:
   - 1 Woche vorher: "Termin nächste Woche"
   - 1 Tag vorher: "Morgen Arzttermin – alles klar?"
   - 2 Stunden vorher: "In 2h Arzttermin – losfahren?"

**Rezepte:**
1. Rezept fotografieren
2. KI erkennt: Medikament, Menge, Ablaufdatum
3. Tracking:
   - "Rezept einlösen in nächsten 3 Tagen"
   - "Rezept läuft bald ab!"
4. Optional: Apotheken-Finder in der Nähe

### Technical Flow
```
[Arzttermin-Scan] → [OCR + Parsing] → [Extract: Date, Time, Location]
    ↓
[Calendar Integration] → [Multi-Stage Reminders]

[Rezept-Scan] → [OCR] → [Extract: Medicine, Expiry]
    ↓
[Deadline Calculation] → [Pharmacy Locator API]
    ↓
[Reminder Engine] → [Stock Monitoring (optional)]
```

---

## Use Case 5: Wartungsarbeiten (Auto, Wohnung, Geräte)

### Problem
TÜV, Heizungswartung, Rauchmelder-Prüfung, Versicherungs-Check – alles Dinge, die regelmäßig gemacht werden müssen. Alle vergessen wir.

Resultat: TÜV überfällig → Bußgeld. Heizung kaputt im Winter. Versicherung ungültig weil nicht gewartet.

### ADHD-Context
- **Wiederkehrende Tasks:** Unser Kryptonit
- **"Nicht dringend":** Bis es dringend ist – dann Panik
- **Overwhelm:** So viele Dinge zu tracken → aufgeben
- **Prokrastination:** "Nächste Woche" wird zu "nächsten Monat"

### Current Workarounds
- ❌ "Ich merk's mir schon" → Narrator: Er merkte es sich nicht
- ❌ Jährliche Erinnerung im Kalender → Wird verschoben, verschoben, verschoben...
- ❌ Partner übernimmt → Wieder Abhängigkeit

### Workmate Solution

1. **Dokument scannen** (TÜV-Bericht, Wartungsprotokoll, etc.)
2. **KI erkennt:**
   - Art der Wartung
   - Datum der letzten Durchführung
   - Intervall (jährlich, alle 2 Jahre, etc.)
3. **Wiederkehrende Reminder:**
   - 2 Monate vorher: "TÜV bald fällig – Termin machen?"
   - 1 Monat vorher: "Erinnerung: TÜV"
   - 2 Wochen vorher: "DRINGEND: TÜV läuft ab!"
4. **Service-Finder:**
   - Werkstatt/Dienstleister in der Nähe
   - Optional: Direkt Termin-Buchung

### Technical Flow
```
[Wartungsdokument] → [KI-Analyse] → [Extract: Type, Last Date, Interval]
    ↓
[Calculate: Next Due Date]
    ↓
[Recurring Reminder Schedule]
    ↓
[Service Locator API] → [Optional: Booking Integration]
```

---

## Weitere Use Cases (Backlog)

- **Steuerfristen** (Steuererklärung, Vorauszahlungen)
- **Abonnements** (Streaming, Software, Magazine)
- **Geburtstage & Geschenke** (Rechtzeitig dran denken, bestellen)
- **Haustier-Versorgung** (Tierarzt, Impfungen, Futter)
- **Lebensmittel-Ablaufdaten** (Keine vergammelten Reste mehr)
- **Reisedokumente** (Reisepass läuft ab, Visa-Fristen)

Diese können in späteren Phasen hinzugefügt werden.

---

## Zusammenfassung

Alle Use Cases folgen dem gleichen Prinzip:

**Workmate Private übernimmt die mentale Last, die für ADHD-Gehirne unerträglich ist.**

Nicht "disziplinierter werden", sondern **"das System arbeitet für dich".**