-- Phase 0 — AI trích & giao việc: schema cho Supabase/Postgres
-- Chạy khi deploy DB thật. Dev dùng JSON fallback (app/stores) nên không bắt buộc.
-- Tasks dùng lại bảng có sẵn của DatabaseConnector (app/database.py).

-- Đa người dùng: mỗi user 1 bridge riêng (multi-tenant)
CREATE TABLE IF NOT EXISTS tata_users (
  id           TEXT PRIMARY KEY,
  name         TEXT NOT NULL,
  bridge_id    TEXT NOT NULL,            -- zca-bridge của user này
  email        TEXT,
  channels     JSONB NOT NULL DEFAULT '[]',
  role         TEXT NOT NULL DEFAULT 'reviewer',  -- reviewer | admin
  active       BOOLEAN NOT NULL DEFAULT true,
  created_at   DOUBLE PRECISION,
  updated_at   DOUBLE PRECISION
);
CREATE INDEX IF NOT EXISTS idx_users_bridge ON tata_users (bridge_id);

-- Kho nhân sự + năng lực + kênh (người & AI agent). Dual-store ↔ Notion.
CREATE TABLE IF NOT EXISTS tata_personnel (
  id               TEXT PRIMARY KEY,
  name             TEXT NOT NULL,
  kind             TEXT NOT NULL DEFAULT 'human',   -- human | ai
  skills           JSONB NOT NULL DEFAULT '[]',
  email            TEXT,
  zalo_account     TEXT,
  teams_account    TEXT,
  ai_hook_url      TEXT,                 -- chỉ với kind='ai'
  ai_system_prompt TEXT,
  ai_harness       TEXT,
  active           BOOLEAN NOT NULL DEFAULT true,
  created_at       DOUBLE PRECISION,
  updated_at       DOUBLE PRECISION
);
CREATE INDEX IF NOT EXISTS idx_personnel_active ON tata_personnel (active);

-- Hàng đợi đề xuất task (chưa phải task) — HITL duyệt ở dashboard
CREATE TABLE IF NOT EXISTS tata_proposals (
  id                  TEXT PRIMARY KEY,
  tenant_id           TEXT NOT NULL,     -- thuộc user/bridge nào (scope duyệt)
  title               TEXT NOT NULL,
  description         TEXT,
  source_ref          TEXT,              -- link/msg id chat gốc
  channel             TEXT,
  candidate_assignees JSONB NOT NULL DEFAULT '[]',
  confidence          DOUBLE PRECISION NOT NULL DEFAULT 0,
  reason              TEXT,
  due                 TEXT,
  priority            TEXT NOT NULL DEFAULT 'Medium',
  dedup_key           TEXT,
  assignee            TEXT,
  approved_by         TEXT,
  status              TEXT NOT NULL DEFAULT 'proposed',  -- proposed|approved|rejected
  created_at          DOUBLE PRECISION,
  updated_at          DOUBLE PRECISION
);
CREATE INDEX IF NOT EXISTS idx_proposals_tenant_status ON tata_proposals (tenant_id, status);
CREATE UNIQUE INDEX IF NOT EXISTS uq_proposals_dedup ON tata_proposals (tenant_id, dedup_key) WHERE dedup_key IS NOT NULL;
