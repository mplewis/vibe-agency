# Quick Start Guide - Vibe Agency Planning Tool

**What is this?** Ein Tool das dir hilft, aus vagen Projektideen konkrete, umsetzbare Feature-Spezifikationen zu erstellen - ohne abzuheben.

**Wer nutzt das?** Du und andere Leute die ein Projekt planen wollen.

**Was macht es?** Führt dich durch einen strukturierten Prozess um Feature-Specs und Architektur-Entwürfe zu erstellen.

---

## 5-Minuten Überblick

### Phase 1: Planning (VIBE_ALIGNER)

**Input:** Deine vage Projektidee ("Ich will eine Booking-App für mein Yoga Studio")

**Prozess:**
1. System erklärt dir was MVP vs. v1.0 bedeutet
2. Du beschreibst deine Features
3. System validiert Machbarkeit (FAE constraints)
4. System prüft fehlende Dependencies (FDG)
5. System bewertet Komplexität (APCE)
6. Du verhandelst den Scope

**Output:** `feature_spec.json` - strukturierte, validierte Feature-Liste

### Phase 2: Architecture (GENESIS_BLUEPRINT)

**Input:** Deine `feature_spec.json` aus Phase 1

**Prozess:**
1. System wählt passende Core-Module
2. Designt Extensions
3. Generiert Config-Schema
4. Validiert die Architektur

**Output:** `architecture.json` - technischer Architektur-Entwurf

---

## Was du brauchst

**Prerequisites:**
- Python 3.11+
- Claude API Key (Anthropic)
- Git
- Dieses Repository

**Installation:**
```bash
git clone https://github.com/kimeisele/vibe-agency.git
cd vibe-agency
pip install pyyaml anthropic
```

---

## Dein erstes Projekt

### Option 1: Manuell (Aktuell)

**Schritt 1: Compose Prompt**
```bash
python3 test_vibe_aligner.py
```

Ergebnis: `VIBE_ALIGNER_TEST.md` (der zusammengesetzte Prompt)

**Schritt 2: Claude fragen**
- Öffne Claude Code oder claude.ai
- Copy/paste den kompletten Prompt aus `VIBE_ALIGNER_TEST.md`
- Beschreibe dein Projekt
- Claude führt dich durch den Prozess

**Schritt 3: Output speichern**
- Claude gibt dir ein JSON zurück
- Speichere es als `workspaces/dein-projekt/artifacts/planning/feature_spec.json`

**Schritt 4: Architecture erstellen**
- Wiederhole für GENESIS_BLUEPRINT
- Input: Dein `feature_spec.json`
- Output: `architecture.json`

### Option 2: Mit LLM Executor (Bald verfügbar)

```bash
# Coming soon - wird automatisiert
python3 scripts/run_planning.py --project "mein-yoga-studio"
```

---

## Was passiert im Hintergrund?

**Keine Multi-Agent Magie** - Es ist einfacher als es klingt:

1. **Prompt Composer** lädt Markdown-Templates + Knowledge Bases
2. **Concateniert** alles zu einem großen Prompt
3. **Claude** (eine Instanz) bekommt den Prompt
4. **Claude** führt dich durch den Prozess
5. **Du** bekommst strukturiertes JSON zurück

Das wars. Kein Orchestration-Wahnsinn. Nur gut strukturierte Prompts.

---

## Typischer Workflow

```
User: "Ich will eine Booking-App bauen"
  ↓
System: "Lass uns das strukturieren. v1.0 oder MVP?"
  ↓
User: "v1.0"
  ↓
System: "Welche Features brauchst du?"
  ↓
User: "Kalender, Buchungen, Zahlungen"
  ↓
System: "✅ Kalender: Machbar
         ✅ Buchungen: Machbar
         ⚠️  Zahlungen: Braucht Stripe/PayPal
         📊 Komplexität: 45 Punkte (OK für v1.0)"
  ↓
System generiert: feature_spec.json
  ↓
User reviewt und sagt OK
  ↓
System generiert: architecture.json
  ↓
FERTIG - Du hast einen konkreten Plan
```

---

## Wichtige Dateien

**Input-Dateien (von dir):**
- Keine - du beschreibst nur dein Projekt

**Output-Dateien (vom System):**
- `feature_spec.json` - Deine validierten Features
- `architecture.json` - Technischer Entwurf
- `project_manifest.json` - Projekt-Status

**Knowledge Bases (im System):**
- `FAE_constraints.yaml` - Was ist machbar?
- `FDG_dependencies.yaml` - Welche Dependencies?
- `APCE_rules.yaml` - Wie komplex ist es?

---

## Häufige Fragen

**Q: Ist das ein Multi-Agent System?**
A: Nein. Es ist **eine** Claude-Instanz mit gut strukturierten Prompts.

**Q: Brauche ich Temporal/Prefect/LangGraph?**
A: Nein. Einfache Python-Scripts reichen.

**Q: Kann ich es für echte Projekte nutzen?**
A: Ja! Fokus ist Planning & Analysis - das funktioniert schon.

**Q: Was kostet es?**
A: ~$0.50-$5 pro Planning-Phase (Claude API Kosten)

**Q: Muss ich alles automatisieren?**
A: Nein. Manuelle Nutzung (copy/paste Prompts) funktioniert perfekt.

---

## Nächste Schritte

1. **Lies:** `client-workflow.md` - Detaillierter Prozess
2. **Test:** Erstelle dein erstes feature_spec.json
3. **Feedback:** Was funktioniert? Was nicht?

---

**Support:** github.com/kimeisele/vibe-agency/issues

**Status:** MVP - Planning Phase funktioniert ✅
