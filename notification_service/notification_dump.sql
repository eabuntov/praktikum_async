-- =====================================================
-- Notification Service Database Initialization Script
-- =====================================================

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =====================================================
-- ENUM-LIKE CHECK CONSTRAINT DOMAINS
-- =====================================================

-- Notification status
CREATE TABLE IF NOT EXISTS notifications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    event_key TEXT NOT NULL,
    template_id UUID,
    payload JSONB NOT NULL,
    status TEXT NOT NULL DEFAULT 'queued'
        CHECK (status IN ('draft', 'queued', 'sending', 'completed', 'failed')),
    idempotency_key TEXT,
    created_by TEXT DEFAULT 'system',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    scheduled_at TIMESTAMPTZ,
    is_periodic BOOLEAN NOT NULL DEFAULT FALSE,
    cron_expression TEXT,
    repeat_until TIMESTAMPTZ
);

-- Idempotency constraint
CREATE UNIQUE INDEX IF NOT EXISTS uniq_notification_idempotency
    ON notifications (event_key, idempotency_key)
    WHERE idempotency_key IS NOT NULL;


-- =====================================================
-- Notification Targets
-- =====================================================

CREATE TABLE IF NOT EXISTS notification_targets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    notification_id UUID NOT NULL
        REFERENCES notifications(id) ON DELETE CASCADE,
    target_type TEXT NOT NULL
        CHECK (target_type IN ('user', 'segment')),
    target_value TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_notification_targets_notification
    ON notification_targets(notification_id);


-- =====================================================
-- User Notification Settings
-- =====================================================

CREATE TABLE IF NOT EXISTS user_notification_settings (
    user_id UUID NOT NULL,
    channel TEXT NOT NULL
        CHECK (channel IN ('email', 'sms', 'push')),
    enabled BOOLEAN NOT NULL DEFAULT TRUE,
    frequency TEXT NOT NULL DEFAULT 'immediate'
        CHECK (frequency IN ('immediate', 'daily', 'weekly')),
    PRIMARY KEY (user_id, channel)
);


-- =====================================================
-- Templates
-- =====================================================

CREATE TABLE IF NOT EXISTS notification_templates (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL UNIQUE,
    subject_template TEXT NOT NULL,
    body_template TEXT NOT NULL,
    html_template TEXT,
    version INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);


-- =====================================================
-- Send Log (Partitioned for Scale)
-- =====================================================

CREATE TABLE IF NOT EXISTS notification_send_log (
    id UUID DEFAULT uuid_generate_v4(),
    notification_id UUID NOT NULL,
    user_id UUID NOT NULL,
    channel TEXT NOT NULL
        CHECK (channel IN ('email', 'sms', 'push')),
    status TEXT NOT NULL
        CHECK (status IN ('pending', 'sent', 'failed', 'skipped')),
    error TEXT,
    sent_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (id, sent_at)
) PARTITION BY RANGE (sent_at);


-- Current month partition (example)
CREATE TABLE IF NOT EXISTS notification_send_log_current
    PARTITION OF notification_send_log
    FOR VALUES FROM (DATE_TRUNC('month', NOW()))
    TO (DATE_TRUNC('month', NOW()) + INTERVAL '1 month');


-- Deduplication guarantee
CREATE UNIQUE INDEX IF NOT EXISTS uniq_notification_user_channel
    ON notification_send_log (notification_id, user_id, channel, sent_at);


CREATE INDEX IF NOT EXISTS idx_send_log_notification
    ON notification_send_log (notification_id);

CREATE INDEX IF NOT EXISTS idx_send_log_user
    ON notification_send_log (user_id);


-- =====================================================
-- Generator State (Idempotency for Scheduled Jobs)
-- =====================================================

CREATE TABLE IF NOT EXISTS notification_generator_state (
    job_name TEXT PRIMARY KEY,
    last_processed_at TIMESTAMPTZ NOT NULL,
    version TEXT NOT NULL
);


-- =====================================================
-- Outbox Table (Optional but Recommended)
-- =====================================================

CREATE TABLE IF NOT EXISTS notification_outbox (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    notification_id UUID NOT NULL,
    event_payload JSONB NOT NULL,
    published BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_outbox_unpublished
    ON notification_outbox (published)
    WHERE published = FALSE;


-- =====================================================
-- Seed Template Example
-- =====================================================

INSERT INTO notification_templates (name, subject_template, body_template, html_template)
VALUES (
    'weekly_digest',
    'Your Weekly Cinema Digest',
    'Hello {{ user_name }}, here are your updates for week {{ week }}.',
    '<h1>Hello {{ user_name }}</h1><p>Here are your updates for week {{ week }}.</p>'
)
ON CONFLICT (name) DO NOTHING;


-- =====================================================
-- Comments (Documentation)
-- =====================================================

COMMENT ON TABLE notifications IS 'Logical notification intents.';
COMMENT ON TABLE notification_targets IS 'Target definitions: user or segment.';
COMMENT ON TABLE notification_send_log IS 'Delivery log with deduplication guarantee.';
COMMENT ON TABLE notification_generator_state IS 'Prevents duplicate scheduled notifications.';
COMMENT ON TABLE notification_outbox IS 'Ensures atomic DB->Kafka publishing if used.';

