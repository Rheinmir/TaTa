"""MessageSource — nguồn tin nhắn cho ingest.

- FakeSource: kịch bản cố định (test offline, không cần Chatwoot).
- ChatwootSource: đọc thật từ Chatwoot API theo account của tenant.
Mỗi poll() trả danh sách Message MỚI kể từ lần poll trước.
"""
import logging
from dataclasses import dataclass, asdict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TaTa.Ingest.Source")


@dataclass
class Message:
    conversation_id: str
    channel: str          # tên inbox/kênh (để lọc + hiển thị)
    sender: str
    text: str
    ts: float             # epoch giây
    msg_id: str

    def to_dict(self):
        return asdict(self)


class MessageSource:
    def poll(self):
        """Trả List[Message] mới kể từ lần gọi trước."""
        raise NotImplementedError


class FakeSource(MessageSource):
    """Mỗi phần tử của `polls` là list Message trả về cho 1 lần poll() (theo thứ tự)."""

    def __init__(self, polls):
        self._polls = list(polls)

    def poll(self):
        return self._polls.pop(0) if self._polls else []


class ChatwootSource(MessageSource):
    """Đọc tin mới từ Chatwoot: list conversations đổi gần đây → messages từng conv.

    Cần base_url + account_id + token (per-tenant). Theo dõi watermark `since_ts`.
    Chỉ lấy tin đến (message_type incoming) — tin của khách, không lấy tin agent gửi ra.
    """

    def __init__(self, base_url, account_id, token, since_ts=0.0, session=None):
        self.base_url = base_url.rstrip("/")
        self.account_id = account_id
        self.token = token
        self.since_ts = since_ts
        import requests
        self._s = session or requests.Session()
        self._s.headers.update({"api_access_token": token})

    def _get(self, path, **params):
        url = f"{self.base_url}/api/v1/accounts/{self.account_id}{path}"
        r = self._s.get(url, params=params, timeout=15)
        r.raise_for_status()
        return r.json()

    def poll(self):
        out = []
        newest = self.since_ts
        try:
            conv_data = self._get("/conversations", status="all")
            payload = (conv_data.get("data") or {}).get("payload") or conv_data.get("payload") or []
            for conv in payload:
                last_act = conv.get("last_activity_at") or 0
                if last_act <= self.since_ts:
                    continue
                cid = conv.get("id")
                inbox = (conv.get("meta") or {}).get("channel") or conv.get("inbox_id")
                msgs = self._get(f"/conversations/{cid}/messages")
                for m in (msgs.get("payload") or []):
                    ts = m.get("created_at") or 0
                    if ts <= self.since_ts or m.get("message_type") != 0:
                        continue  # chỉ tin đến, mới hơn watermark
                    sender = ((m.get("sender") or {}).get("name")) or "Người gửi"
                    text = (m.get("content") or "").strip()
                    if not text:
                        continue
                    out.append(Message(str(cid), str(inbox), sender, text, float(ts), str(m.get("id"))))
                    newest = max(newest, float(ts))
        except Exception as e:  # noqa: BLE001
            logger.warning("ChatwootSource poll lỗi: %s", e)
        self.since_ts = max(self.since_ts, newest)
        return out
