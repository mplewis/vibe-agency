# STEWARD Protocol - Security Model

**Status:** ⚠️ DRAFT (TODO before v1.0.0)
**Last Updated:** 2025-11-21

---

## 🔐 SECURITY PRINCIPLES

1. **Cryptographic Identity** - Agents identified by public key fingerprints
2. **Key Rotation** - Agents can rotate keys without losing identity
3. **Revocation** - Compromised keys can be revoked immediately
4. **Multi-Sig** - Critical agents require multiple signatures
5. **Time-Bounded Trust** - Attestations expire, force periodic re-verification
6. **Transparent Audit** - All operations logged in tamper-evident ledger

---

## 🔑 KEY MANAGEMENT

### Key Generation

```bash
# Generate primary keypair
$ steward keygen --agent-id vibe-agency-orchestrator

Generating RSA-4096 keypair...
✅ Private key: .steward/vibe-agency-orchestrator_id_rsa
✅ Public key: .steward/vibe-agency-orchestrator_id_rsa.pub
✅ Fingerprint: sha256:abc123def456...

⚠️  CRITICAL: Back up private key to secure location!
   - Use encrypted storage (KMS, 1Password, etc.)
   - Never commit to git
   - Generate recovery key (optional)
```

### Key Storage Best Practices

```yaml
# Recommended key storage hierarchy

production:
  storage: "AWS KMS / Google Secret Manager / HashiCorp Vault"
  backup: "Encrypted offline storage"
  access: "Multi-person approval required"

development:
  storage: "Local filesystem with encryption"
  backup: "Secure password manager"
  access: "Developer only"

ci_cd:
  storage: "GitHub Secrets / GitLab CI Variables"
  backup: "Not needed (can regenerate)"
  access: "CI/CD pipeline only"
```

---

## 🔄 KEY ROTATION

### Rotation Triggers

Rotate keys when:
- ✅ **Scheduled rotation** (every 365 days recommended)
- ⚠️ **Security incident** (potential compromise)
- ⚠️ **Employee departure** (if they had key access)
- ⚠️ **Algorithm weakness** (e.g., SHA-1 → SHA-256)

### Rotation Process

```bash
# 1. Generate new keypair
$ steward keygen --agent-id vibe-agency-orchestrator --rotate

Generating new RSA-4096 keypair...
✅ New private key: .steward/vibe-agency-orchestrator_id_rsa.new
✅ New public key: .steward/vibe-agency-orchestrator_id_rsa.pub.new
✅ New fingerprint: sha256:xyz789...

# 2. Update manifest with new key (but keep old key for transition)
$ steward manifest update-key --new-key .steward/vibe-agency-orchestrator_id_rsa.pub.new

Updated steward.json:
  primary_key: sha256:xyz789... (NEW)
  rotation_history:
    - sha256:abc123... (DEPRECATED, valid until 2025-12-21)

# 3. Sign manifest with BOTH keys (dual signature period)
$ steward sign steward.json --primary-key .steward/vibe-agency-orchestrator_id_rsa.new \
                             --secondary-key .steward/vibe-agency-orchestrator_id_rsa

✅ Manifest signed with dual signature
✅ Old key valid for 30 days (grace period)
✅ New key primary after 2025-12-21

# 4. Publish updated manifest
$ steward publish

✅ Published with dual signature
⚠️  Old key will be revoked on 2025-12-21 (30 days)

# 5. After grace period, revoke old key
$ steward revoke-key sha256:abc123...

✅ Key revoked: sha256:abc123...
✅ All old signatures invalidated
✅ Agents must now use new key
```

### Manifest Format with Key Rotation

```json
{
  "identity": {
    "primary_key": {
      "fingerprint": "sha256:xyz789...",
      "algorithm": "RSA-4096",
      "issued_date": "2025-11-21T00:00:00Z",
      "expires": "2026-11-21T00:00:00Z"
    },

    "rotation_history": [
      {
        "fingerprint": "sha256:abc123...",
        "algorithm": "RSA-4096",
        "issued_date": "2024-11-21T00:00:00Z",
        "deprecated_date": "2025-11-21T00:00:00Z",
        "revoked_date": "2025-12-21T00:00:00Z",
        "revocation_reason": "scheduled_rotation",
        "grace_period_days": 30
      }
    ]
  }
}
```

---

## 🚫 KEY REVOCATION

### Immediate Revocation (Key Compromise)

```bash
# Emergency revocation (no grace period)
$ steward revoke-key sha256:abc123... --reason key_compromise --immediate

⚠️  WARNING: This will IMMEDIATELY invalidate all signatures!
⚠️  Agents using old key will be unable to delegate.
⚠️  This action cannot be undone.

Continue? [y/N]: y

✅ Key revoked immediately
✅ Revocation published to registry
✅ All attestations signed with old key invalidated

Next steps:
  1. Generate new keypair: steward keygen --rotate
  2. Re-attest all capabilities: steward attest --all
  3. Notify delegating agents: steward notify-delegators
```

### Revocation Verification

```bash
# Other agents check revocation status
$ steward verify vibe-agency-orchestrator

Verifying agent identity...
✅ Current key valid: sha256:xyz789...
⚠️  Previous key REVOKED: sha256:abc123... (reason: key_compromise)

Revocation published: 2025-11-21T10:00:00Z
Verification source: steward-registry.org/revocations

Safe to delegate: YES (current key not compromised)
```

### Revocation List Format

```json
{
  "revocations": [
    {
      "agent_id": "vibe-agency-orchestrator",
      "revoked_key": "sha256:abc123...",
      "revoked_date": "2025-11-21T10:00:00Z",
      "reason": "key_compromise",
      "evidence": "https://incident-report.example.com/2025-11-21",
      "revoked_by": "sha256:xyz789...",  // Signed with new key
      "signature": "..."
    }
  ]
}
```

---

## 🔐 MULTI-SIGNATURE SUPPORT

### When to Use Multi-Sig

Use multi-sig for:
- **Critical agents** (infrastructure, financial operations)
- **High-trust requirements** (healthcare, legal domains)
- **Organizational agents** (require approval from multiple team members)

### Multi-Sig Configuration

```json
{
  "identity": {
    "multi_sig": {
      "enabled": true,
      "threshold": 2,  // Require 2 of 3 signatures
      "signers": [
        {
          "id": "team-member-1",
          "pubkey": "sha256:key1...",
          "role": "lead_developer"
        },
        {
          "id": "team-member-2",
          "pubkey": "sha256:key2...",
          "role": "security_officer"
        },
        {
          "id": "team-member-3",
          "pubkey": "sha256:key3...",
          "role": "operations_manager"
        }
      ]
    }
  }
}
```

### Multi-Sig Workflow

```bash
# 1. Developer initiates attestation
$ steward attest --capability orchestrate_sdlc --multi-sig

Running tests...
✅ 369/383 tests passing (96%)

Generating attestation certificate...
✅ Attestation: attestations/orchestrate_sdlc_2025-11-21.json

⏳ Waiting for signatures (1/2 required)
   - team-member-1: ✅ SIGNED (2025-11-21T10:00:00Z)
   - team-member-2: ⏳ PENDING
   - team-member-3: ⏳ PENDING

# 2. Security officer reviews and signs
$ steward multi-sig-approve attestations/orchestrate_sdlc_2025-11-21.json \
                            --key .steward/team-member-2_id_rsa

Reviewing attestation...
  - Agent: vibe-agency-orchestrator v4.0.0
  - Capability: orchestrate_sdlc
  - Test results: 369/383 passing (96%)
  - No security issues detected

Approve? [y/N]: y

✅ Signed by team-member-2
✅ Threshold reached (2/2 required)
✅ Attestation now valid

# 3. Publish to registry
$ steward publish

✅ Multi-sig attestation published
✅ All signatures verified
```

---

## 🛡️ ATTACK MITIGATION

### 1. Key Compromise Detection

```yaml
monitoring:
  # Alert on suspicious activity
  - unusual_delegation_patterns
  - signing_from_unexpected_locations
  - high_frequency_operations
  - failed_verification_attempts

automated_response:
  - suspend_agent (after 5 failed verifications)
  - notify_owner
  - require_manual_reactivation
```

### 2. Typosquatting Prevention

```python
# Registry checks for similar agent IDs
def check_typosquatting(new_agent_id: str) -> List[str]:
    """
    Detect potential typosquatting attacks.
    """
    similar_agents = []

    for existing_agent in registry:
        # Levenshtein distance
        if levenshtein_distance(new_agent_id, existing_agent.id) <= 2:
            similar_agents.append(existing_agent)

        # Homograph attack (unicode lookalikes)
        if looks_similar(new_agent_id, existing_agent.id):
            similar_agents.append(existing_agent)

    return similar_agents

# Example:
# New: "vibe-agency-orchestratοr" (greek omicron)
# Existing: "vibe-agency-orchestrator" (latin o)
# → WARNING: Potential homograph attack
```

### 3. Sybil Attack Resistance

```yaml
registry_policy:
  new_agent_restrictions:
    - min_uptime_proof: "7 days"
    - min_test_coverage: 0.5
    - email_verification: required
    - rate_limit: "5 agents per identity per month"

  trust_score_penalties:
    - new_agent: -0.3  # Start with reduced trust
    - no_endorsements: -0.1
    - similar_name_to_existing: -0.2
```

### 4. Replay Attack Prevention

```json
{
  "delegation": {
    "nonce": "unique-random-value",
    "timestamp": "2025-11-21T10:00:00Z",
    "expires": "2025-11-21T11:00:00Z",
    "signature": "..."
  }
}
```

---

## 🔍 AUDIT TRAIL

### Required Logging

All security-sensitive operations must be logged:

```json
{
  "audit_log": [
    {
      "timestamp": "2025-11-21T10:00:00Z",
      "event_type": "key_rotation",
      "agent_id": "vibe-agency-orchestrator",
      "old_key": "sha256:abc123...",
      "new_key": "sha256:xyz789...",
      "initiated_by": "team-member-1",
      "signature": "..."
    },
    {
      "timestamp": "2025-11-21T10:05:00Z",
      "event_type": "attestation_generated",
      "agent_id": "vibe-agency-orchestrator",
      "capability": "orchestrate_sdlc",
      "test_coverage": 0.96,
      "signed_by": ["team-member-1", "team-member-2"],
      "signature": "..."
    }
  ]
}
```

### Tamper-Evident Logging

```python
# Merkle tree for audit log integrity
class AuditLog:
    def append(self, event: dict):
        # Hash previous log entry
        prev_hash = self.get_last_hash()

        # Hash current event
        event_hash = sha256(json.dumps(event))

        # Combine hashes (Merkle tree node)
        combined_hash = sha256(prev_hash + event_hash)

        # Store
        self.log.append({
            "event": event,
            "hash": combined_hash,
            "prev_hash": prev_hash
        })

    def verify_integrity(self) -> bool:
        # Recompute all hashes, verify chain
        for i, entry in enumerate(self.log):
            recomputed = sha256(
                entry["prev_hash"] + sha256(entry["event"])
            )
            if recomputed != entry["hash"]:
                return False  # Tampering detected!
        return True
```

---

## 🚨 INCIDENT RESPONSE

### Security Incident Workflow

```yaml
1. Detection:
   - Monitor logs for anomalies
   - Check failed verification attempts
   - Review delegation patterns

2. Containment:
   - Immediately revoke compromised key
   - Suspend agent from registry
   - Notify all delegating agents

3. Investigation:
   - Review audit logs
   - Identify scope of compromise
   - Determine root cause

4. Recovery:
   - Generate new keypair
   - Re-attest all capabilities
   - Resume operations with new key

5. Post-Mortem:
   - Document incident
   - Update security procedures
   - Publish transparency report
```

---

## ✅ SECURITY CHECKLIST

### Before v1.0.0 Production

- [ ] Key rotation mechanism implemented
- [ ] Revocation protocol tested
- [ ] Multi-sig support for critical agents
- [ ] Typosquatting detection in registry
- [ ] Sybil attack resistance measures
- [ ] Replay attack prevention (nonce + timestamp)
- [ ] Tamper-evident audit logging
- [ ] Incident response playbook documented
- [ ] Security monitoring alerts configured
- [ ] Penetration testing completed

---

## 📚 REFERENCES

- **Key Management:** NIST SP 800-57 (Key Management Recommendations)
- **Multi-Sig:** BIP-0011 (Bitcoin Multi-Signature)
- **Revocation:** RFC 5280 (X.509 Certificate Revocation)
- **Audit Logging:** NIST SP 800-92 (Log Management)

---

**Status:** ⚠️ DRAFT - Implementation required before v1.0.0
**Critical:** Key rotation + revocation are non-negotiable for production use
