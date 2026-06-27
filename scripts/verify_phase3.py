"""Verify Phase 3 — ReviewService (HITL): tenant-scope + suggest assignee + approve→task + reject."""
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
    os.environ["TATA_STORE_DIR"] = tempfile.mkdtemp(prefix="tata_phase3_")
    os.environ.pop("SUPABASE_URL", None); os.environ.pop("SUPABASE_KEY", None)
    print("[backend] JSON fallback (tempdir)")

from app.stores import PersonnelStore, ProposalStore  # noqa: E402
from app.review_service import ReviewService  # noqa: E402

ok = True
def check(label, cond):
    global ok; print(f"  {'✅' if cond else '❌'} {label}"); ok = ok and cond


class FakeDB:
    """thay DatabaseConnector để không ghi file thật khi test."""
    def __init__(self): self.tasks = []
    def insert_task(self, t):
        t = dict(t); t["id"] = f"task-{len(self.tasks)+1}"; self.tasks.append(t); return t


# seed nhân sự
ps = PersonnelStore()
ps.upsert_person("Nam", skills=["báo cáo", "tài chính"], email="nam@ct.vn")
ps.upsert_person("Tùng", skills=["máy lạnh", "điện", "cơ sở vật chất"], email="tung@ct.vn")
ps.upsert_person("Hoa", skills=["thiết kế"], email="hoa@ct.vn")

# seed proposals (t1: 2, t2: 1 — test scope)
pr = ProposalStore()
p1 = pr.add_proposal("t1", "Sửa máy lạnh tầng 9", "máy lạnh tầng 9 bị hỏng", "Zalo:conv1",
                     confidence=0.9, priority="High")
p2 = pr.add_proposal("t1", "Làm báo cáo tài chính Q2", "tổng hợp số liệu tài chính", "Zalo:conv1",
                     candidate_assignees=["Nam"], confidence=0.88)
pr.add_proposal("t2", "Việc của tenant khác", "x", "Zalo:conv9", confidence=0.9)

db = FakeDB()
svc = ReviewService(proposal_store=pr, personnel_store=ps, db=db)

print("== tenant-scope ==")
check("t1 có 2 đề xuất pending", len(svc.list_pending("t1")) == 2)
check("t2 chỉ thấy đề xuất của t2 (1)", len(svc.list_pending("t2")) == 1)

print("== suggest assignee (AI prefer skill-match) ==")
s1 = svc.suggest_assignees(p1)
check("máy lạnh → Tùng đứng đầu", s1 and s1[0]["name"] == "Tùng")
s2 = svc.suggest_assignees(p2)
check("báo cáo tài chính + hint → Nam đứng đầu", s2 and s2[0]["name"] == "Nam")
print("     suggest P1:", [(x["name"], x["score"]) for x in s1])
print("     suggest P2:", [(x["name"], x["score"]) for x in s2])

print("== approve → tạo task ==")
res = svc.approve(p1["id"], assignee="Tùng", approved_by="t1", priority="High")
check("task được tạo (FakeDB)", len(db.tasks) == 1 and db.tasks[0]["assignee"] == "Tùng")
check("task giữ title đề xuất", db.tasks[0]["title"] == "Sửa máy lạnh tầng 9")
check("proposal → approved", res["proposal"]["status"] == "approved")
check("pending t1 còn 1 sau approve", len(svc.list_pending("t1")) == 1)

print("== reject ==")
svc.reject(p2["id"], approved_by="t1")
check("proposal → rejected", pr.get(p2["id"])["status"] == "rejected")
check("pending t1 = 0 sau reject", len(svc.list_pending("t1")) == 0)
check("không tạo thêm task khi reject", len(db.tasks) == 1)

print("\n" + ("✅ PHASE 3 PASS" if ok else "❌ PHASE 3 FAIL"))
sys.exit(0 if ok else 1)
