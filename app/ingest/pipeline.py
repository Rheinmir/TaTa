"""IngestPipeline — buffer tin theo hội thoại + debounce, lọc kênh.

Luồng:
  poll_and_buffer(): source.poll() → bỏ tin kênh bị lọc → gom vào state theo conversation
  harvest(now):      hội thoại nào IM ≥ window (đã lắng) → phát 1 batch + xoá pending
Đầu ra batch = {tenant_id, conversation_id, channel, messages:[...]} → cho Phase 2.

State dùng Store adapter (Postgres/Supabase/JSON) — bảng tata_ingest_state.
"""
import time
import logging

from app.stores.base import Store

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TaTa.Ingest.Pipeline")

DEFAULT_WINDOW = 180  # giây im lặng coi là 'hội thoại đã lắng'


class IngestStateStore(Store):
    id_prefix = "ing"

    def __init__(self, client=None):
        super().__init__("tata_ingest_state", client)

    def find(self, tenant_id, conversation_id):
        rows = self.list(tenant_id=tenant_id, conversation_id=conversation_id)
        return rows[0] if rows else None


class IngestPipeline:
    def __init__(self, source, channel_filter, tenant_id, state_store=None, window_seconds=DEFAULT_WINDOW):
        self.source = source
        self.filter = channel_filter
        self.tenant_id = tenant_id
        self.state = state_store or IngestStateStore()
        self.window = window_seconds

    def poll_and_buffer(self):
        """Kéo tin mới, lọc kênh, gom vào pending theo hội thoại. Trả số tin đã nhận."""
        msgs = self.source.poll()
        kept = 0
        for m in msgs:
            if not self.filter.allows(m.channel):
                continue
            row = self.state.find(self.tenant_id, m.conversation_id)
            md = m.to_dict()
            if row is None:
                self.state.insert({
                    "tenant_id": self.tenant_id,
                    "conversation_id": m.conversation_id,
                    "channel": m.channel,
                    "last_msg_ts": m.ts,
                    "pending": [md],
                })
            else:
                pending = list(row.get("pending") or [])
                pending.append(md)
                self.state.update(row["id"], {
                    "pending": pending,
                    "last_msg_ts": max(row.get("last_msg_ts") or 0, m.ts),
                    "channel": m.channel,
                })
            kept += 1
        return kept

    def harvest(self, now=None):
        """Phát batch cho hội thoại đã lắng (im ≥ window). Trả List[batch]."""
        now = now if now is not None else time.time()
        batches = []
        for row in self.state.list(tenant_id=self.tenant_id):
            pending = row.get("pending") or []
            if not pending:
                continue
            if now - (row.get("last_msg_ts") or 0) >= self.window:
                batches.append({
                    "tenant_id": self.tenant_id,
                    "conversation_id": row.get("conversation_id"),
                    "channel": row.get("channel"),
                    "messages": pending,
                })
                self.state.update(row["id"], {"pending": [], "last_emitted_ts": now})
        return batches
