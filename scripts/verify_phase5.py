"""Verify Phase 5 — AI-assignee hook: giao AI → fire webhook payload (system_prompt+harness); người → không hook."""
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

PG = os.environ.get("TATA_DATABASE_URL")
if PG:
    print(f"[backend] Postgres: {PG.split('@')[-1]}")
    import psycopg2
    _c = psycopg2.connect(PG); _c.autocommit = True
    with _c.cursor() as cur:
        cur.execute("TRUNCATE tata_proposals, tata_personnel")
    _c.close()
else:
    os.environ["TATA_STORE_DIR"] = tempfile.mkdtemp(prefix="tata_phase5_")
    os.environ.pop("SUPABASE_URL", None); os.environ.pop("SUPABASE_KEY", None)
    print("[backend] JSON fallback (tempdir)")

from app.stores import PersonnelStore, ProposalStore  # noqa: E402
from app.hooks import AIHook  # noqa: E402
from app.review_service import ReviewService  # noqa: E402

ok = True
def check(label, cond):
    global ok; print(f"  {'✅' if cond else '❌'} {label}"); ok = ok and cond

class FakeDB:
    def __init__(self): self.tasks = []
    def insert_task(self, t):
        t = dict(t); t["id"] = f"task-{len(self.tasks)+1}"; self.tasks.append(t); return t

# capture HTTP POST mà AIHook gửi
sent = []
def fake_sender(url, payload, headers): sent.append({"url": url, "payload": payload})

ps = PersonnelStore()
ps.upsert_person("Nam", skills=["báo cáo"], email="nam@ct.vn")  # người
ps.upsert_person("AI-Report", skills=["báo cáo"], kind="ai",
                 ai_hook_url="https://hook.local/ai-report",
                 ai_system_prompt="Bạn là trợ lý soạn báo cáo. Súc tích.",
                 ai_harness="claude-code")
ps.upsert_person("AI-NoURL", skills=["x"], kind="ai")  # AI nhưng chưa có hook url

pr = ProposalStore()
def mkprop(t): return pr.add_proposal("t1", t, "desc", "Zalo:c1", confidence=0.9)

svc = ReviewService(proposal_store=pr, personnel_store=ps, db=FakeDB(),
                    ai_hook=AIHook(sender=fake_sender, callback_base="https://tata.local"))

print("== giao AI-Report (có hook url) ==")
r1 = svc.approve(mkprop("Soạn báo cáo tuần")["id"], assignee="AI-Report", approved_by="t1")
h = r1.get("ai_hook")
check("hook status=fired", h and h["status"] == "fired")
check("POST đúng url", sent and sent[0]["url"] == "https://hook.local/ai-report")
pl = sent[0]["payload"] if sent else {}
check("payload có system_prompt inject", pl.get("system_prompt", "").startswith("Bạn là trợ lý soạn báo cáo"))
check("payload có harness ref", pl.get("harness") == "claude-code")
check("payload có callback_url", "/api/hooks/ai-result/" in (pl.get("callback_url") or ""))
check("payload mang task title", pl.get("task", {}).get("title") == "Soạn báo cáo tuần")

print("== giao người (Nam) → KHÔNG fire hook ==")
r2 = svc.approve(mkprop("Việc cho người")["id"], assignee="Nam", approved_by="t1")
check("không có ai_hook", r2.get("ai_hook") is None)
check("không phát sinh POST mới", len(sent) == 1)

print("== giao AI nhưng chưa có hook url → dry-run ==")
r3 = svc.approve(mkprop("Việc AI chưa cấu hình")["id"], assignee="AI-NoURL", approved_by="t1")
check("hook dry-run", r3["ai_hook"]["status"] == "dry-run")
check("dry-run vẫn dựng payload", r3["ai_hook"]["payload"]["assignee"] == "AI-NoURL")
check("không POST khi dry-run", len(sent) == 1)

print("\n" + ("✅ PHASE 5 PASS" if ok else "❌ PHASE 5 FAIL"))
sys.exit(0 if ok else 1)
