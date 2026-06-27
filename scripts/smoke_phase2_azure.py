"""Smoke test Phase 2 trên Azure gpt-4.1-mini THẬT + tin Zalo thật (/tmp/zalo_msgs.json).

Chunk 240 tin thành các 'batch hội thoại' ~25 tin, chạy TaskExtractor (AzureLiteLLMClient),
in các proposal trích được để soi precision (việc thật vs tán gẫu).

Cần env (đặt trong .env.caveman, gitignored):
  TATA_DATABASE_URL, TATA_LLM_BASE_URL, TATA_LLM_API_KEY, TATA_LLM_FLAVOR=azure,
  AZURE_API_VERSION, TATA_EXTRACT_MODEL=gpt-4.1-mini
"""
import os
import sys
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# nạp .env.caveman
from app.stores.base import _load_env_caveman  # noqa: E402
_load_env_caveman()

from app.extractor import TaskExtractor, AzureLiteLLMClient  # noqa: E402
from app.stores import ProposalStore  # noqa: E402

CHUNK = int(os.environ.get("SMOKE_CHUNK", "25"))
TENANT = "smoke-zalo"

llm = AzureLiteLLMClient()
if not llm.configured:
    print("❌ Chưa cấu hình LLM (TATA_LLM_BASE_URL/API_KEY trong .env.caveman). Dừng.")
    sys.exit(2)
print(f"[LLM] flavor={llm.flavor} model={llm.model} base={llm.base_url[:48]}...")

msgs = json.load(open("/tmp/zalo_msgs.json", encoding="utf-8"))
print(f"[data] {len(msgs)} tin · chunk={CHUNK}")

# dọn proposal của tenant smoke (Postgres)
if os.environ.get("TATA_DATABASE_URL"):
    import psycopg2
    c = psycopg2.connect(os.environ["TATA_DATABASE_URL"]); c.autocommit = True
    with c.cursor() as cur:
        cur.execute("DELETE FROM tata_proposals WHERE tenant_id=%s", [TENANT])
    c.close()

ext = TaskExtractor(llm)
total_created = total_low = total_dedup = 0
for i in range(0, len(msgs), CHUNK):
    chunk = msgs[i:i + CHUNK]
    batch = {
        "tenant_id": TENANT,
        "conversation_id": f"smoke-{i // CHUNK}",
        "channel": "Zalo nhóm (thật)",
        "messages": [{"sender": m.get("uid") or m.get("dir"), "text": m["text"]} for m in chunk],
    }
    try:
        r = ext.extract(batch)
    except Exception as e:  # noqa: BLE001
        print(f"  chunk {i//CHUNK}: LỖI gọi LLM: {e}")
        continue
    total_created += len(r["created"]); total_low += r["dropped_low"]; total_dedup += r["dropped_dedup"]
    for p in r["created"]:
        print(f"  ✦ [{p['confidence']:.2f}] {p['title']}  ← {(p.get('reason') or '')[:50]}")

print(f"\n== KẾT QUẢ: {total_created} đề xuất / {len(msgs)} tin "
      f"(loại {total_low} conf thấp, {total_dedup} trùng) ==")
print("→ Soi: đề xuất có đúng là 'việc giao rõ ràng' không? Tán gẫu có lọt không?")
pend = ProposalStore().pending_for_tenant(TENANT)
print(f"   proposals 'proposed' trong store: {len(pend)}")
