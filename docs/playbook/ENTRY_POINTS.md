# STEWARD ENTRY POINTS

When user request is unclear, suggest one of these 9 specialized modes:

## The 9 Entry Points

**[1] 💡 New Project**  
→ VIBE_ALIGNER (GAD-1XX Planning Framework)  
Use: Starting from zero, need feature spec  

**[2] 🚀 Continue Work** [DEFAULT]  
→ STEWARD Session Mode (GAD-5XX Runtime)  
Use: Picking up where you left off  

**[3] 🔍 Research Knowledge**  
→ Knowledge Department (GAD-6XX)  
Use: Need domain knowledge or patterns  

**[4] 📊 Show Status**  
→ Status Reporter (GAD-5XX Runtime)  
Use: Project health check  

**[5] ✅ Quality Check**  
→ Pre-Push QA (GAD-4XX + GAD-7XX)  
Use: Before pushing code  

**[6] 📝 Update Docs**  
→ Documentation Writer (GAD-2XX Orchestration)  
Use: Document changes or features  

**[7] 🧪 Run Tests**  
→ Test Runner (GAD-4XX Quality)  
Use: Verify everything works  

**[8] 🎓 Learn Something**  
→ Educator Mode (GAD-6XX Knowledge)  
Use: Explain concepts or architecture  

**[9] 🔄 Refactor/Optimize**  
→ Refactor Mode (GAD-2XX Orchestration)  
Use: Improve code quality  

---

## Default Behavior

**If unclear which mode:** Ask user with 2-3 most relevant options.

**Default mode:** [2] Continue Work (Session Mode)

---

## Routing Logic

Each entry point connects to specific GAD pillars:
- **GAD-1XX:** Planning & Research (New projects)
- **GAD-2XX:** Core Orchestration (Docs, Refactor)
- **GAD-4XX:** Quality & Testing (QA, Tests)
- **GAD-5XX:** Runtime Engineering (Session, Status)
- **GAD-6XX:** Knowledge Department (Research, Learning)
- **GAD-7XX:** STEWARD Governance (Quality gates)

All work at all layers (Browser/Claude Code/Runtime) via graceful degradation.
