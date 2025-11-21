# STEWARD Protocol - Design Drafts

**Status:** 🚧 DRAFT - Community Feedback Phase
**Version:** 0.1.0-draft
**Started:** 2025-11-21

---

## 🎯 WHAT IS THIS?

This directory contains **design drafts** for the **STEWARD Protocol** - a universal standard for AI agent identity, discovery, verification, and delegation.

**Vision:** "Docker for AI Agents" + "LinkedIn for Agents"

Instead of static markdown files that become outdated, we're designing a **complete protocol** with:
- 🤖 Machine-readable agent manifests (`steward.json`)
- 🔍 Discovery & registry system (find agents by capability)
- 🔐 Cryptographic verification (sign + attest capabilities)
- 🤝 Standardized delegation protocol (task submission + monitoring)
- ⭐ Reputation system (trust scores + endorsements)

---

## 📁 FILES IN THIS DIRECTORY

### 1. `STEWARD_PROTOCOL_SPEC.md`
**The main specification document.**

Contains:
- Vision & requirements
- 5-layer architecture (Manifest → Registry → APIs → CLI → Applications)
- Solutions to staleness problem
- Comparison with Docker, OpenAPI, LinkedIn
- Implementation roadmap (MVP in 4 weeks)

**Start here** to understand the full vision.

### 2. `STEWARD_JSON_SCHEMA.json`
**JSON Schema for agent manifests.**

Defines the structure of `steward.json` files:
- Agent identity (id, version, fingerprint)
- Credentials (mandate, constraints, prime directive)
- Capabilities (interfaces, operations, quality metrics)
- Runtime introspection endpoints
- Governance (principal, audit trail)

**Machine-readable specification** that can validate manifests.

### 3. `EXAMPLES.md`
**Real-world usage examples.**

Shows how agents would use the protocol:
- Discovery & verification
- Task delegation & monitoring
- Multi-agent collaboration
- Publishing agents to registry
- Trust scores & reputation
- Handling stale attestations

**Concrete examples** to understand practical usage.

---

## 🤔 WHY DO WE NEED THIS?

### Current Problem: Static STEWARD.md

The current approach (filling out STEWARD.md template) has issues:

1. **Staleness**: Markdown files become outdated
   - Test pass rate changes → manual update needed
   - Capabilities evolve → manual update needed
   - Version bumps → manual update needed

2. **No Discovery**: How do agents find each other?
   - Google search? 🤷
   - Manual curation? 📝
   - Word of mouth? 💬

3. **No Verification**: How do agents trust each other?
   - Read markdown and hope it's accurate? 🤞
   - Run tests manually? ⏳
   - Trust blindly? 💣

4. **No Standardization**: Every agent invents their own format
   - Different manifests → hard to parse
   - Different interfaces → hard to integrate
   - Different trust models → hard to evaluate

### Solution: STEWARD Protocol

A **complete standard** like Docker or HTTP:

```bash
# Discovery (like 'docker search')
steward discover --capability orchestrate_sdlc

# Verification (like SSL certificates)
steward verify vibe-agency-orchestrator

# Delegation (like REST API calls)
steward delegate vibe-agency-orchestrator --operation orchestrate_sdlc

# Monitoring (like 'docker logs')
steward monitor <task-id>
```

**Benefits:**
- ✅ Always current (runtime introspection)
- ✅ Cryptographically verified (signing + attestation)
- ✅ Standardized (same commands for all agents)
- ✅ Discoverable (searchable registry)
- ✅ Trustworthy (reputation scores)

---

## 🏗️ ARCHITECTURE OVERVIEW

```
┌─────────────────────────────────────────────────────────────┐
│ 1. AGENT MANIFEST (steward.json)                            │
│    Machine-readable identity, capabilities, quality metrics │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ 2. STEWARD REGISTRY                                         │
│    Agent index, versions, trust scores, attestations        │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ 3. PROTOCOL APIS                                            │
│    Discovery, Verification, Delegation, Monitoring          │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ 4. STEWARD CLI                                              │
│    steward discover, verify, delegate, monitor              │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ 5. AGENT APPLICATIONS                                       │
│    AI agents using protocol (STEWARD, others)               │
└─────────────────────────────────────────────────────────────┘
```

---

## 🗺️ COMPARISON WITH EXISTING STANDARDS

| Feature | Docker | LinkedIn | HTTP | **STEWARD** |
|---------|--------|----------|------|-------------|
| **Purpose** | Container runtime | Professional network | Web communication | Agent coordination |
| **Identity** | Image name/tag | Profile | Domain name | Agent ID + fingerprint |
| **Discovery** | Docker Hub | Search + filters | DNS | Registry + search |
| **Verification** | Image signing | Endorsements | SSL/TLS | Signing + attestation |
| **Execution** | `docker run` | Job application | HTTP request | `steward delegate` |
| **Monitoring** | `docker logs` | Profile views | Server logs | `steward monitor` |
| **Trust** | Verified publishers | Recommendations | Certificate authorities | Trust scores + tests |

**STEWARD = Docker + LinkedIn + OpenAPI for AI Agents**

---

## 📋 IMPLEMENTATION ROADMAP

### Phase 1: MVP (4 weeks) - Git-Based Registry

**Week 1: Specification**
- [ ] Finalize `steward.json` JSON Schema
- [ ] Define delegation payload format
- [ ] Write attestation certificate spec

**Week 2: CLI Basics**
- [ ] `steward init` - Create manifest
- [ ] `steward verify` - Verify signature
- [ ] `steward search` - Search git registry

**Week 3: Git Registry**
- [ ] Registry structure (GitHub repo)
- [ ] Index generation (JSON files)
- [ ] Search implementation

**Week 4: Cryptography**
- [ ] `steward keygen` - Generate keypair
- [ ] `steward sign` - Sign manifest
- [ ] `steward attest` - Generate attestations

### Phase 2: Protocol Extensions (8 weeks)

- [ ] Health checks & introspection
- [ ] Attestation expiry & refresh
- [ ] Trust score calculation
- [ ] Delegation monitoring

### Phase 3: Federated Registry (12 weeks)

- [ ] Federated discovery protocol
- [ ] Cross-registry search
- [ ] Reputation aggregation
- [ ] Web of trust

---

## 🤝 HOW TO CONTRIBUTE

### 1. Review the Specification

Read `STEWARD_PROTOCOL_SPEC.md` and provide feedback:

**Questions to consider:**
- Is the JSON Schema complete?
- Are the APIs well-designed?
- Is the trust model sound?
- Are there security concerns?
- Is the roadmap realistic?

**Leave feedback:**
- GitHub Issues: Tag with `[STEWARD Protocol]`
- Comments in draft files (as markdown comments)
- Alternative designs in separate files

### 2. Suggest Use Cases

Add more examples to `EXAMPLES.md`:
- What scenarios are missing?
- What edge cases need coverage?
- What failure modes need handling?

### 3. Prototype Components

Pick a component and build a proof-of-concept:
- `steward` CLI tool (Python or Rust)
- JSON Schema validator
- Git-based registry
- Attestation generator
- Trust score calculator

### 4. Compare with Alternatives

Research existing standards and suggest improvements:
- What can we learn from Docker?
- What can we learn from OpenAPI/Swagger?
- What can we learn from OAuth/OIDC?
- What can we learn from blockchain identity systems?

---

## ❓ OPEN QUESTIONS

These need community discussion:

### 1. Registry Model
- **Git-based** (simple, transparent) vs **Centralized** (fast, reliable) vs **Federated** (censorship-resistant)?
- How do we handle registry downtime?
- How do we prevent spam/malicious agents?

### 2. Trust Model
- How should trust scores be calculated?
- Should there be "verified" badges (like Twitter)?
- How do we handle reputation attacks?
- Should trust scores decay over time?

### 3. Attestation Format
- How long should attestations be valid? (24h? 7d? configurable?)
- What should trigger re-attestation?
- How do we handle partial failures (96% tests passing - good enough?)
- Should attestations be cryptographically signed?

### 4. Security
- How do we prevent agent impersonation?
- How do we handle key compromise?
- Should there be a revocation mechanism?
- Rate limiting on delegation requests?

### 5. Interoperability
- Should STEWARD be compatible with existing agent frameworks?
- Should we define bindings for multiple languages (Python, JS, Rust)?
- Should there be a REST API in addition to CLI?

---

## 📚 RELATED WORK

Research these before implementing:

### Identity & Discovery
- **DID (Decentralized Identifiers)** - W3C standard for self-sovereign identity
- **Verifiable Credentials** - W3C standard for credential verification
- **mDNS/DNS-SD** - Zero-config service discovery

### Delegation & Orchestration
- **OpenAPI/Swagger** - API specification standard
- **gRPC** - High-performance RPC framework
- **JSON-RPC** - Lightweight RPC protocol

### Trust & Reputation
- **PGP Web of Trust** - Decentralized trust model
- **Certificate Transparency** - Public log of certificates
- **Blockchain Identity** - Ethereum Name Service (ENS), etc.

### Registries
- **Docker Hub** - Container registry
- **npm** - JavaScript package registry
- **PyPI** - Python package registry
- **Maven Central** - Java package registry

---

## 🎯 NEXT STEPS

1. **Community Feedback** (2 weeks)
   - Share drafts with community
   - Collect feedback via GitHub Issues
   - Iterate on design

2. **Finalize Spec** (1 week)
   - Incorporate feedback
   - Publish v1.0.0-rc1 (release candidate)

3. **Build MVP** (4 weeks)
   - Implement `steward` CLI
   - Create git-based registry
   - Generate example manifests

4. **Proof-of-Concept** (2 weeks)
   - Demonstrate STEWARD protocol with vibe-agency
   - Show 2-agent delegation (vibe-agency ↔ external agent)
   - Measure performance & UX

5. **Publish RFC** (1 week)
   - Formal RFC document
   - Submit to relevant communities
   - Seek wider adoption

---

## 📞 CONTACT

**Project:** vibe-agency
**Repository:** https://github.com/kimeisele/vibe-agency
**Discussions:** GitHub Issues (tag: `[STEWARD Protocol]`)

**Status:** 🚧 DRAFT - Seeking feedback

---

**Remember:** This is "Docker for AI Agents" - we're building the infrastructure for the AI Agent Economy.

Let's make agent-to-agent delegation as easy as `docker run`.
