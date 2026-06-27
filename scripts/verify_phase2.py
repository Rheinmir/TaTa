"""Verify Phase 2 — AI extractor: confidence gate + dedup + 'không bắt sai' (offline FakeLLM)."""
import os
import sys
import json
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

PG = os.environ.get("TATA_DATABASE_URL")
if PG:
    print(f"[backend] Postgres: {PG.split('@')[-1]}")
    import psycopg2
    _c = psycopg2.connect(PG); _c.autocommit = True
    with _c.cursor() as cur:
        cur.execute("TRUNCATE tata_proposals")
    _c.close()
else:
    os.environ["TATA_STORE_DIR"] = tempfile.mkdtemp(prefix="tata_phase2_")
    os.environ.pop("SUPABASE_URL", None); os.environ.pop("SUPABASE_KEY", None)
    print("[backend] JSON fallback (tempdir)")

from app.extractor import FakeLLM, TaskExtractor  # noqa: E402
from app.extractor.llm import parse_tasks  # noqa: E402
from app.stores import ProposalStore  # noqa: E402

ok = True
def check(label, cond):
    global ok; print(f"  {'✅' if cond else '❌'} {label}"); ok = ok and cond

TENANT = "user-1"

# --- parse robustness ---
print("== parse_tasks ==")
check("bóc rào ```json", parse_tasks('```json\n{"tasks": []}\n```') == [])
check("bóc JSON lẫn chữ thừa", len(parse_tasks('rác {"tasks":[{"title":"x","confidence":0.9}]} rác')) == 1)

# --- Scenario A: 1 việc thật (conf cao) + 1 nhiễu (conf thấp) ---
print("== A: gate lọc confidence thấp ==")
resp_A = json.dumps({"tasks": [
    {"title": "Làm báo cáo tài chính Q2", "description": "gửi trước thứ 6",
     "assignee_hint": "Nam", "due": "2026-06-27", "priority": "High",
     "confidence": 0.88, "reason": "có người nhận + hành động + mốc"},
    {"title": "Có thể xem lại số liệu", "description": "mơ hồ",
     "assignee_hint": None, "due": None, "priority": "Low",
     "confidence": 0.40, "reason": "không chắc là việc"},
]})
ext = TaskExtractor(FakeLLM(lambda s, u: resp_A))
batchA = {"tenant_id": TENANT, "conversation_id": "A", "channel": "Zalo nhóm A",
          "messages": [{"sender": "Sếp", "text": "Nam làm báo cáo tài chính Q2 trước thứ 6 nhé"}]}
rA = ext.extract(batchA)
check("tạo 1 proposal (conf cao)", len(rA["created"]) == 1)
check("loại 1 do confidence thấp", rA["dropped_low"] == 1)
check("proposal có assignee_hint=Nam", rA["created"][0]["candidate_assignees"] == ["Nam"])

# --- Scenario B: toàn tán gẫu → KHÔNG bắt sai ---
print("== B: không bắt sai (chỉ tán gẫu) ==")
ext_B = TaskExtractor(FakeLLM(lambda s, u: json.dumps({"tasks": []})))
batchB = {"tenant_id": TENANT, "conversation_id": "B", "channel": "Zalo nhóm A",
          "messages": [{"sender": "An", "text": "haha ok"}, {"sender": "Bình", "text": "ăn cơm chưa"}]}
rB = ext_B.extract(batchB)
check("0 proposal từ tán gẫu", len(rB["created"]) == 0)

# --- Scenario C: dedup (chạy lại batch A) ---
print("== C: dedup ==")
rC = ext.extract(batchA)
check("lần 2 cùng việc → 0 tạo", len(rC["created"]) == 0)
check("đếm dedup = 1", rC["dropped_dedup"] == 1)

# --- tổng kiểm proposal trong store ---
ps = ProposalStore()
pend = ps.pending_for_tenant(TENANT)
check("store chỉ có đúng 1 proposal proposed", len(pend) == 1)

print("\n" + ("✅ PHASE 2 PASS" if ok else "❌ PHASE 2 FAIL"))
sys.exit(0 if ok else 1)
