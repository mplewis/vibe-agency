# Client Workflow - Planning & Architecture

**Ziel:** Von "Ich hab ne Idee" zu "Ich hab einen konkreten Plan"

**Dauer:** 30-60 Minuten für Planning + Architecture

---

## Überblick

```
Schritt 1: Projekt-Setup        (5 Min)
Schritt 2: VIBE_ALIGNER nutzen  (15-30 Min)
Schritt 3: Feature Spec reviewen (5 Min)
Schritt 4: GENESIS nutzen       (10-20 Min)
Schritt 5: Architecture reviewen (5 Min)
```

**Ergebnis:** 2 Dateien die deinen Plan beschreiben

---

## Schritt 1: Projekt-Setup

### Was du machst:

```bash
# In vibe-agency directory
cd /pfad/zu/vibe-agency

# Teste ob VIBE_ALIGNER funktioniert
python3 test_vibe_aligner.py
```

**Erwarte:** `✅ SUCCESS! Prompt length: 7780 chars`

### Was passiert:

Das System lädt:
- VIBE_ALIGNER Prompt-Templates
- FAE Knowledge Base (Machbarkeits-Regeln)
- FDG Knowledge Base (Dependency Graph)
- APCE Knowledge Base (Komplexitäts-Regeln)

Und baut daraus einen zusammenhängenden Prompt.

---

## Schritt 2: VIBE_ALIGNER nutzen

### Was du machst:

**Option A: Manuell (jetzt)**

1. Öffne `VIBE_ALIGNER_TEST.md`
2. Kopiere den kompletten Inhalt
3. Gehe zu Claude Code oder claude.ai
4. Paste den Prompt
5. Beschreibe dein Projekt

**Option B: Mit LLM Executor (bald)**

```bash
python3 scripts/run_vibe_aligner.py \
  --project "yoga-studio-booking" \
  --interactive
```

### Der Prozess - Was Claude dich fragt:

#### Phase 1: Education & Calibration

**Claude:** "Lass uns über Scope reden. Kennst du den Unterschied zwischen MVP und v1.0?"

**Du:**
- "Ja, ich will v1.0" (feature-complete, poliert)
- "Nein, erklär mal" (Claude erklärt)
- "Ich will MVP" (minimal aber funktional)

**Warum:** Damit du realistische Erwartungen hast.

#### Phase 2: Feature Extraction

**Claude:** "Beschreibe dein Projekt. Was soll es können?"

**Du:** "Ich will eine Booking-App für mein Yoga Studio. Kunden sollen:
- Kurse im Kalender sehen
- Sich online anmelden
- Mit PayPal zahlen
- Email-Bestätigung bekommen"

**Claude:** "OK, ich strukturiere das..."

#### Phase 3: Feasibility Check (FAE)

**Claude prüft automatisch:**
- ✅ Kalender-Ansicht: Machbar (Standard Web-Feature)
- ✅ Online-Anmeldung: Machbar (Standard CRUD)
- ⚠️ PayPal Integration: Machbar aber braucht PayPal SDK
- ✅ Email-Versand: Machbar (Transactional Email Service)

**Claude sagt dir:**
"Alle Features sind für v1.0 machbar. PayPal braucht einen API-Account."

#### Phase 4: Gap Detection (FDG)

**Claude prüft:**
- Kalender → Braucht: Date/Time Library
- Buchungen → Braucht: User Auth System
- Zahlung → Braucht: PayPal SDK
- Email → Braucht: SendGrid/Mailgun

**Claude fragt:**
"Ich sehe dass du Zahlungen willst - soll das PayPal sein oder auch Kreditkarten?"

**Du:** "Nur PayPal reicht."

**Claude:** "OK, dann brauchen wir nur PayPal SDK, nicht Stripe."

#### Phase 5: Complexity Scoring (APCE)

**Claude berechnet:**
- Kalender-UI: 15 Punkte
- Buchungs-Logik: 20 Punkte
- PayPal Integration: 25 Punkte
- Email-System: 10 Punkte
- **TOTAL: 70 Punkte**

**Claude sagt:**
"Das ist ein mittelgroßes v1.0 Projekt (70 Punkte). Realistisch in 4-6 Wochen umsetzbar."

#### Phase 6: Output Generation

**Claude generiert:**

```json
{
  "project": {
    "name": "Yoga Studio Booking System",
    "scope": "v1.0"
  },
  "features": [
    {
      "id": "F001",
      "name": "Class Calendar View",
      "complexity": 15,
      "feasibility": "FEASIBLE",
      "dependencies": ["date-time-library"]
    },
    {
      "id": "F002",
      "name": "Online Booking",
      "complexity": 20,
      "feasibility": "FEASIBLE",
      "dependencies": ["user-auth", "database"]
    },
    {
      "id": "F003",
      "name": "PayPal Payment",
      "complexity": 25,
      "feasibility": "FEASIBLE",
      "dependencies": ["paypal-sdk", "F002"]
    },
    {
      "id": "F004",
      "name": "Email Confirmation",
      "complexity": 10,
      "feasibility": "FEASIBLE",
      "dependencies": ["email-service", "F002"]
    }
  ],
  "total_complexity": 70,
  "estimated_effort": "4-6 weeks"
}
```

---

## Schritt 3: Feature Spec reviewen

### Was du machst:

**Prüfe das JSON:**

✅ **Sind alle Features drin?** Fehlt was?
✅ **Sind Abhängigkeiten klar?** PayPal braucht Account?
✅ **Ist der Scope realistisch?** 70 Punkte OK?
✅ **Willst du was ändern?** Features entfernen/hinzufügen?

**Falls OK:**
- Speichere als `feature_spec.json`
- Weiter zu Schritt 4

**Falls nicht OK:**
- Sag Claude: "Ich will Feature X ändern"
- Claude updated das JSON
- Repeat

---

## Schritt 4: GENESIS_BLUEPRINT nutzen

### Was du machst:

**Jetzt geht's um Technical Architecture**

```bash
# Test (bald automatisiert)
python3 test_genesis_blueprint.py
```

**Öffne den generierten Prompt und paste zu Claude:**

**Du gibst Claude dein `feature_spec.json`**

### Der Prozess:

#### Phase 1: Core Module Selection

**Claude analysiert Features und wählt:**
- **Web Framework:** Next.js (React + SSR)
- **Database:** PostgreSQL (relational data)
- **Auth:** NextAuth.js (user authentication)
- **Payments:** PayPal REST API
- **Email:** SendGrid (transactional email)

**Claude erklärt Warum:**
"Next.js weil: Full-stack, SSR für SEO, TypeScript support"
"PostgreSQL weil: Buchungen brauchen Transactions"

#### Phase 2: Extension Design

**Claude designed Extensions:**
- Calendar Component (React component)
- Booking Engine (Backend logic)
- Payment Handler (PayPal integration)
- Notification Service (Email sender)

#### Phase 3: Config Schema

**Claude generiert Config:**

```typescript
// app.config.ts
export const config = {
  paypal: {
    clientId: process.env.PAYPAL_CLIENT_ID,
    secret: process.env.PAYPAL_SECRET,
    mode: 'sandbox' | 'production'
  },
  email: {
    provider: 'sendgrid',
    apiKey: process.env.SENDGRID_KEY,
    from: 'noreply@yoga-studio.com'
  },
  database: {
    url: process.env.DATABASE_URL
  }
}
```

#### Phase 4: Architecture Output

**Claude generiert:**

```json
{
  "architecture": {
    "framework": "Next.js 14",
    "language": "TypeScript",
    "database": "PostgreSQL",
    "deployment": "Vercel"
  },
  "modules": [
    {
      "name": "calendar",
      "type": "frontend",
      "dependencies": ["react", "date-fns"]
    },
    {
      "name": "booking-engine",
      "type": "backend",
      "dependencies": ["prisma", "paypal-sdk"]
    }
  ],
  "external_services": [
    "PayPal REST API",
    "SendGrid Email API"
  ],
  "estimated_setup_time": "1-2 days"
}
```

---

## Schritt 5: Architecture reviewen

### Was du machst:

**Prüfe die Architektur:**

✅ **Macht die Tech-Stack Wahl Sinn?** Next.js OK?
✅ **Sind die Dependencies klar?** Was muss installiert werden?
✅ **Sind externe Services machbar?** PayPal Account möglich?
✅ **Setup-Zeit realistisch?** 1-2 Tage OK?

**Falls OK:**
- Speichere als `architecture.json`
- **Du bist fertig mit Planning!**

**Falls nicht OK:**
- Sag Claude: "Ich will lieber Vue statt React"
- Claude updated die Architektur

---

## Was du jetzt hast

```
workspaces/yoga-studio/
  project_manifest.json       ← Status: PLANNING complete
  artifacts/
    planning/
      feature_spec.json       ← Validierte Features
      architecture.json       ← Technical Design
```

**Das sind deine Specs.** Du kannst sie:
- Entwicklern geben
- Selbst implementieren
- Outsourcen
- Als Basis für Angebote nutzen

---

## Typische Dauer

| Phase | Zeit |
|-------|------|
| VIBE_ALIGNER (Features) | 15-30 Min |
| Review Feature Spec | 5 Min |
| GENESIS (Architecture) | 10-20 Min |
| Review Architecture | 5 Min |
| **TOTAL** | **35-60 Min** |

---

## Häufige Fehler

**❌ Zu viele Features auf einmal**
- Lösung: Fokussiere auf 4-6 Kern-Features für v1.0

**❌ Scope während des Prozesses ändern**
- Lösung: Schließe VIBE_ALIGNER ab, dann starte neu wenn du was ändern willst

**❌ Dependencies ignorieren**
- Lösung: Wenn Claude sagt "braucht PayPal Account" → erstelle den Account

**❌ Unrealistische Zeiterwartung**
- Lösung: Wenn APCE sagt "4-6 Wochen" → das ist realistisch

---

## Was als nächstes?

**Wenn Planning fertig:**
1. Implementierung starten (manuell oder CODE_GENERATOR Phase)
2. Oder: Specs an Entwickler geben
3. Oder: Angebote einholen basierend auf specs

**Wenn du mehr Features willst:**
1. Zurück zu VIBE_ALIGNER
2. Starte "Update Existing Project" flow
3. GENESIS_UPDATE updated die Architektur

---

## Troubleshooting

Siehe: `troubleshooting.md`

---

**Next:** `operator-workflow.md` - Wie man das System selbst betreibt
