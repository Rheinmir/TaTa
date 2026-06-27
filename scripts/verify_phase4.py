"""Verify Phase 4 — giao + notify: định tuyến kênh theo người + Notion push (qua approve)."""
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
    os.environ["TATA_STORE_DIR"] = tempfile.mkdtemp(prefix="tata_phase4_")
    os.environ.pop("SUPABASE_URL", None); os.environ.pop("SUPABASE_KEY", None)
    print("[backend] JSON fallback (tempdir)")

from app.stores import PersonnelStore, ProposalStore  # noqa: E402
from app.notify import NotifyService, DryRunChannel  # noqa: E402
from app.review_service import ReviewService  # noqa: E402

ok = True
def check(label, cond):
    global ok; print(f"  {'✅' if cond else '❌'} {label}"); ok = ok and cond


class FakeDB:
    def __init__(self): self.tasks = []
    def insert_task(self, t):
        t = dict(t); t["id"] = f"task-{len(self.tasks)+1}"; self.tasks.append(t); return t

class FakeNotion:
    def __init__(self): self.pushed = []
    def push(self, task): self.pushed.append(task); return {"status": "mock", "task_id": task.get("id")}


ps = PersonnelStore()
ps.upsert_person("Nam", skills=["báo cáo"], email="nam@ct.vn", zalo_account="nam.zalo")   # email+zalo
ps.upsert_person("Tùng", skills=["máy lạnh"], email="tung@ct.vn")                          # email only
ps.upsert_person("AI-Bot", skills=["tổng hợp"], kind="ai", ai_hook_url="https://hook/ai")  # AI

pr = ProposalStore()
def mkprop(title):
    return pr.add_proposal("t1", title, "desc", "Zalo:c1", confidence=0.9)

email_ch = DryRunChannel("email"); zalo_ch = DryRunChannel("zalo"); teams_ch = DryRunChannel("teams")
ns = NotifyService(email=email_ch, zalo=zalo_ch, teams=teams_ch)
notion = FakeNotion(); db = FakeDB()
svc = ReviewService(proposal_store=pr, personnel_store=ps, db=db, notify_service=ns, notion_sync=notion)

print("== giao Nam (email+zalo) ==")
pA = mkprop("Việc cho Nam")
rA = svc.approve(pA["id"], assignee="Nam", approved_by="t1")
chans = {x["channel"] for x in rA["notify"]}
check("notify đúng 2 kênh email+zalo", chans == {"email", "zalo"})
check("KHÔNG gửi teams (Nam ko có)", "teams" not in chans)
check("Notion push được gọi", len(notion.pushed) == 1)
check("DryRun email ghi 1", len(email_ch.sent) == 1 and email_ch.sent[0]["target"] == "nam@ct.vn")
check("DryRun zalo ghi 1", len(zalo_ch.sent) == 1 and zalo_ch.sent[0]["target"] == "nam.zalo")

print("== giao Tùng (email only) ==")
pB = mkprop("Việc cho Tùng")
rB = svc.approve(pB["id"], assignee="Tùng", approved_by="t1")
check("notify chỉ email", {x["channel"] for x in rB["notify"]} == {"email"})
check("zalo không thêm (vẫn 1)", len(zalo_ch.sent) == 1)

print("== giao AI-Bot (kind=ai → hook Phase 5, không notify người) ==")
pC = mkprop("Việc cho AI")
rC = svc.approve(pC["id"], assignee="AI-Bot", approved_by="t1")
check("AI → skip notify người (ai-hook)", rC["notify"][0]["channel"] == "ai-hook")
check("Notion vẫn push cho task AI", len(notion.pushed) == 3)
check("không có email/zalo gửi cho AI", len(email_ch.sent) == 2 and len(zalo_ch.sent) == 1)

print("\n" + ("✅ PHASE 4 PASS" if ok else "❌ PHASE 4 FAIL"))
sys.exit(0 if ok else 1)
