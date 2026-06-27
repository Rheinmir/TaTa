-- Phase 1 — Ingest: state debounce theo hội thoại
CREATE TABLE IF NOT EXISTS tata_ingest_state (
  id              TEXT PRIMARY KEY,
  tenant_id       TEXT NOT NULL,
  conversation_id TEXT NOT NULL,
  channel         TEXT,
  last_msg_ts     DOUBLE PRECISION,
  last_emitted_ts DOUBLE PRECISION,
  pending         JSONB NOT NULL DEFAULT '[]',   -- tin đang chờ lắng
  created_at      DOUBLE PRECISION,
  updated_at      DOUBLE PRECISION
);
CREATE UNIQUE INDEX IF NOT EXISTS uq_ingest_conv ON tata_ingest_state (tenant_id, conversation_id);
