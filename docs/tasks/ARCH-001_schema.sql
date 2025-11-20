-- ============================================================================
-- VIBE AGENCY - PERSISTENCE SCHEMA v1.0
-- ============================================================================
-- Purpose: Normalized SQLite schema for agent operation persistence
-- Phase: 2.5 - Foundation Scalability
-- Created: 2025-11-20
-- Schema Version: 1
-- ============================================================================

-- Set schema version for migrations
PRAGMA user_version = 1;

-- Enable foreign key enforcement (required for referential integrity)
PRAGMA foreign_keys = ON;

-- ============================================================================
-- TABLE: missions
-- ============================================================================
-- Purpose: Core mission lifecycle tracking
-- Stores: Mission metadata, phase progression, completion status
-- ============================================================================
CREATE TABLE missions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    mission_uuid TEXT UNIQUE NOT NULL,      -- External identifier for API/file references
    phase TEXT NOT NULL,                    -- PLANNING, CODING, TESTING, DEPLOYMENT, MAINTENANCE
    status TEXT NOT NULL,                   -- pending, in_progress, completed, failed
    created_at TEXT NOT NULL,               -- ISO 8601 timestamp (e.g., '2025-11-20T14:30:00Z')
    completed_at TEXT,                      -- ISO 8601 timestamp (NULL if still active)
    metadata JSON,                          -- Flexible storage for mission-specific data

    -- Constraints
    CHECK (status IN ('pending', 'in_progress', 'completed', 'failed')),
    CHECK (phase IN ('PLANNING', 'CODING', 'TESTING', 'DEPLOYMENT', 'MAINTENANCE'))
);

-- Performance index: Query active missions efficiently
CREATE INDEX idx_missions_status ON missions(status);

-- Performance index: Query missions by phase
CREATE INDEX idx_missions_phase ON missions(phase);

-- ============================================================================
-- TABLE: tool_calls
-- ============================================================================
-- Purpose: Audit trail of all agent tool executions
-- Supports: "What tools were used?", "Why did this fail?", "How long did X take?"
-- ============================================================================
CREATE TABLE tool_calls (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    mission_id INTEGER NOT NULL,            -- Links to parent mission
    tool_name TEXT NOT NULL,                -- e.g., 'WebFetch', 'Bash', 'Read'
    args JSON NOT NULL,                     -- Tool input parameters (as JSON object)
    result JSON,                            -- Tool output (NULL if error occurred)
    timestamp TEXT NOT NULL,                -- ISO 8601 timestamp of execution
    duration_ms INTEGER,                    -- Execution time in milliseconds
    success INTEGER NOT NULL,               -- 0 = failed, 1 = succeeded
    error_message TEXT,                     -- Error details (NULL if success=1)

    -- Referential integrity: Cascade delete when mission is deleted
    FOREIGN KEY (mission_id) REFERENCES missions(id) ON DELETE CASCADE,

    -- Constraints
    CHECK (success IN (0, 1))
);

-- Performance index: Query tool calls by mission and time (for audit queries)
CREATE INDEX idx_tool_calls_mission_time ON tool_calls(mission_id, timestamp);

-- Performance index: Query failed tool calls
CREATE INDEX idx_tool_calls_success ON tool_calls(success);

-- Performance index: Query tool usage statistics
CREATE INDEX idx_tool_calls_name ON tool_calls(tool_name);

-- ============================================================================
-- TABLE: decisions
-- ============================================================================
-- Purpose: Agent decision provenance (why did the agent choose X?)
-- Supports: "Why was approach Y chosen?", "What was the rationale?"
-- ============================================================================
CREATE TABLE decisions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    mission_id INTEGER NOT NULL,            -- Links to parent mission
    decision_type TEXT NOT NULL,            -- e.g., 'architecture_choice', 'tool_selection', 'approach'
    rationale TEXT,                         -- Human-readable explanation of decision
    timestamp TEXT NOT NULL,                -- ISO 8601 timestamp
    agent_name TEXT,                        -- Which agent made this decision (e.g., 'STEWARD', 'CODING')
    context JSON,                           -- Additional context data (alternatives considered, etc.)

    -- Referential integrity
    FOREIGN KEY (mission_id) REFERENCES missions(id) ON DELETE CASCADE
);

-- Performance index: Query decisions by mission and time
CREATE INDEX idx_decisions_mission_time ON decisions(mission_id, timestamp);

-- Performance index: Query decisions by type
CREATE INDEX idx_decisions_type ON decisions(decision_type);

-- Performance index: Query decisions by agent
CREATE INDEX idx_decisions_agent ON decisions(agent_name);

-- ============================================================================
-- TABLE: playbook_runs
-- ============================================================================
-- Purpose: Playbook execution metrics (performance tracking)
-- Supports: "How long do playbooks take?", "Which playbooks fail most?"
-- ============================================================================
CREATE TABLE playbook_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    mission_id INTEGER NOT NULL,            -- Links to parent mission (NULL for standalone runs)
    playbook_name TEXT NOT NULL,            -- e.g., 'restaurant.plan', 'research.analyze_topic'
    phase TEXT,                             -- SDLC phase (PLANNING, CODING, etc.)
    started_at TEXT NOT NULL,               -- ISO 8601 timestamp
    completed_at TEXT,                      -- ISO 8601 timestamp (NULL if still running)
    success INTEGER,                        -- 0 = failed, 1 = succeeded, NULL = in_progress
    metrics JSON,                           -- Execution metrics (tool_count, decision_count, etc.)
    error_message TEXT,                     -- Error details (NULL if success=1)

    -- Referential integrity (allow NULL mission_id for standalone playbook runs)
    FOREIGN KEY (mission_id) REFERENCES missions(id) ON DELETE CASCADE,

    -- Constraints
    CHECK (success IS NULL OR success IN (0, 1))
);

-- Performance index: Query playbook runs by mission
CREATE INDEX idx_playbook_runs_mission ON playbook_runs(mission_id);

-- Performance index: Query playbook performance statistics
CREATE INDEX idx_playbook_runs_name ON playbook_runs(playbook_name);

-- Performance index: Query playbook failures
CREATE INDEX idx_playbook_runs_success ON playbook_runs(success);

-- ============================================================================
-- TABLE: agent_memory
-- ============================================================================
-- Purpose: Context persistence across agent invocations
-- Supports: Session state, user preferences, learned patterns
-- ============================================================================
CREATE TABLE agent_memory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    mission_id INTEGER NOT NULL,            -- Links to parent mission (NULL for global memory)
    key TEXT NOT NULL,                      -- Memory key (e.g., 'last_playbook', 'user_preference')
    value JSON,                             -- Memory value (flexible JSON storage)
    timestamp TEXT NOT NULL,                -- ISO 8601 timestamp of last update
    ttl INTEGER,                            -- Time-to-live in seconds (NULL = no expiration)
    expires_at TEXT,                        -- Computed expiration timestamp (NULL if ttl is NULL)

    -- Referential integrity
    FOREIGN KEY (mission_id) REFERENCES missions(id) ON DELETE CASCADE,

    -- Ensure unique keys per mission
    UNIQUE (mission_id, key)
);

-- Performance index: Query memory by mission and key (for fast context lookups)
CREATE INDEX idx_agent_memory_mission_key ON agent_memory(mission_id, key);

-- Performance index: Query expired memory for cleanup
CREATE INDEX idx_agent_memory_expires ON agent_memory(expires_at);

-- ============================================================================
-- VIEWS (Optional - for common queries)
-- ============================================================================

-- View: Active missions with latest activity
CREATE VIEW active_missions AS
SELECT
    m.id,
    m.mission_uuid,
    m.phase,
    m.status,
    m.created_at,
    COUNT(DISTINCT tc.id) AS tool_call_count,
    COUNT(DISTINCT d.id) AS decision_count,
    MAX(tc.timestamp) AS last_tool_call_at
FROM missions m
LEFT JOIN tool_calls tc ON tc.mission_id = m.id
LEFT JOIN decisions d ON d.mission_id = m.id
WHERE m.status IN ('pending', 'in_progress')
GROUP BY m.id;

-- View: Tool usage statistics
CREATE VIEW tool_usage_stats AS
SELECT
    tool_name,
    COUNT(*) AS total_calls,
    SUM(success) AS successful_calls,
    AVG(duration_ms) AS avg_duration_ms,
    MAX(duration_ms) AS max_duration_ms
FROM tool_calls
GROUP BY tool_name;

-- View: Playbook performance metrics
CREATE VIEW playbook_performance AS
SELECT
    playbook_name,
    COUNT(*) AS total_runs,
    SUM(success) AS successful_runs,
    AVG(CAST((julianday(completed_at) - julianday(started_at)) * 86400000 AS INTEGER)) AS avg_duration_ms
FROM playbook_runs
WHERE completed_at IS NOT NULL
GROUP BY playbook_name;

-- ============================================================================
-- MAINTENANCE TRIGGERS (Auto-cleanup)
-- ============================================================================

-- Trigger: Auto-compute expires_at when TTL is set
CREATE TRIGGER compute_memory_expiration
AFTER INSERT ON agent_memory
FOR EACH ROW
WHEN NEW.ttl IS NOT NULL
BEGIN
    UPDATE agent_memory
    SET expires_at = datetime(NEW.timestamp, '+' || NEW.ttl || ' seconds')
    WHERE id = NEW.id;
END;

-- ============================================================================
-- SCHEMA VALIDATION QUERIES
-- ============================================================================
-- Run these to verify schema integrity after creation:
--
-- 1. List all tables:
--    .tables
--    Expected: agent_memory decisions missions playbook_runs tool_calls
--
-- 2. Verify foreign keys are enabled:
--    PRAGMA foreign_keys;
--    Expected: 1
--
-- 3. Check schema version:
--    PRAGMA user_version;
--    Expected: 1
--
-- 4. Test referential integrity:
--    INSERT INTO missions (mission_uuid, phase, status, created_at)
--        VALUES ('test-001', 'PLANNING', 'pending', '2025-11-20T00:00:00Z');
--    INSERT INTO tool_calls (mission_id, tool_name, args, timestamp, success)
--        VALUES (1, 'test_tool', '{}', '2025-11-20T00:01:00Z', 1);
--    DELETE FROM missions WHERE mission_uuid = 'test-001';
--    SELECT COUNT(*) FROM tool_calls;  -- Expected: 0 (cascade delete worked)
-- ============================================================================
