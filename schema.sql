-- Workflow Instances
CREATE TABLE IF NOT EXISTS workflow_instances (
    instance_id     VARCHAR(36) PRIMARY KEY,
    template_id     VARCHAR(100) NOT NULL,
    status          VARCHAR(20) NOT NULL,   -- pending / running / completed / failed
    triggered_by    VARCHAR(100),
    triggered_at    TIMESTAMP DEFAULT NOW(),
    completed_at    TIMESTAMP,
    inputs          JSONB,
    outputs         JSONB
);

-- Audit Trail
CREATE TABLE IF NOT EXISTS audit_trail (
    id              SERIAL PRIMARY KEY,
    instance_id     VARCHAR(36) REFERENCES workflow_instances(instance_id),
    step_name       VARCHAR(100),
    started_at      TIMESTAMP,
    completed_at    TIMESTAMP,
    status          VARCHAR(20),   -- success / failed
    input_snapshot  JSONB,
    output_snapshot JSONB,
    error_message   TEXT
);
-- Enforce immutability
REVOKE UPDATE, DELETE ON audit_trail FROM PUBLIC;

-- Appeals Table
CREATE TABLE IF NOT EXISTS appeals (
    appeal_id        SERIAL PRIMARY KEY,
    appeal_of        VARCHAR(36) REFERENCES workflow_instances(instance_id),
    new_instance_id  VARCHAR(36) REFERENCES workflow_instances(instance_id),
    outcome          VARCHAR(20),  -- accepted / rejected
    appealed_at      TIMESTAMP DEFAULT NOW()
);