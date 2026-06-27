"""Verify Phase 0 — CRUD round-trip cho 3 store (chạy trên JSON fallback, không cần Supabase).

Dùng thư mục tạm để không đụng data thật. Mô phỏng luồng:
user→bridge, nhân sự (human+AI) match skill, proposal proposed→approved.
"""
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
        cur.execute("TRUNCATE tata_users, tata_personnel, tata_proposals")  # lần chạy sạch
    _c.close()
else:
    # ép JSON fallback vào thư mục tạm
    os.environ["TATA_STORE_DIR"] = tempfile.mkdtemp(prefix="tata_phase0_")
    os.environ.pop("SUPABASE_URL", None)
    os.environ.pop("SUPABASE_KEY", None)
    print("[backend] JSON fallback (tempdir)")

from app.stores import TenantStore, PersonnelStore, ProposalStore  # noqa: E402
from app.stores.personnel_sync import PersonnelNotionSync  # noqa: E402
from app.stores.proposal_store import STATUS_APPROVED  # noqa: E402

ok = True
def check(label, cond):
    global ok
    print(f"  {'✅' if cond else '❌'} {label}")
    ok = ok and cond

print("== TenantStore ==")
ts = TenantStore()
u = ts.create_user("An (PM)", bridge_id="bridge-an", email="an@ct.vn", channels=["Zalo nhóm A"])
check("tạo user có id", bool(u.get("id")))
check("tìm theo bridge", ts.by_bridge("bridge-an") is not None)

print("== PersonnelStore (dual-store + match skill) ==")
ps = PersonnelStore(notion_sync=PersonnelNotionSync())
ps.upsert_person("Nam", skills=["báo cáo", "excel", "tài chính"], email="nam@ct.vn", zalo_account="nam.z")
ps.upsert_person("Hoa", skills=["thiết kế", "canva"], email="hoa@ct.vn")
ps.upsert_person("AI-Report", skills=["báo cáo", "tổng hợp"], kind="ai",
                 ai_hook_url="https://hook.local/ai-report", ai_system_prompt="Bạn là trợ lý báo cáo.")
check("3 nhân sự active", len(ps.active_people()) == 3)
check("lọc kind=ai", len(ps.active_people(kind="ai")) == 1)
ranked = ps.match_by_skills(["báo cáo", "tài chính"])
check("match skill trả ứng viên", len(ranked) >= 1)
check("Nam đứng đầu (2 skill khớp)", ranked and ranked[0][0]["name"] == "Nam")
print("     top match:", [(p["name"], s) for p, s in ranked])

print("== ProposalStore (proposed → approved, dedup) ==")
pr = ProposalStore()
p1 = pr.add_proposal(tenant_id=u["id"], title="Làm báo cáo tài chính Q2",
                     description="Gửi trước thứ 6", source_ref="zalo:msg:7972",
                     candidate_assignees=["Nam"], confidence=0.82,
                     reason="có người nhận + hành động + mốc thời gian", due="2026-06-27",
                     priority="High", channel="Zalo nhóm A", dedup_key="bao-cao-q2")
check("tạo proposal status=proposed", p1.get("status") == "proposed")
check("dedup phát hiện trùng", pr.exists_dedup(u["id"], "bao-cao-q2") is True)
check("pending theo tenant = 1", len(pr.pending_for_tenant(u["id"])) == 1)
appr = pr.approve(p1["id"], assignee="Nam", approved_by=u["id"], priority="High")
check("approve → status=approved", appr.get("status") == STATUS_APPROVED)
check("approve gán assignee", appr.get("assignee") == "Nam")
check("hết pending sau approve", len(pr.pending_for_tenant(u["id"])) == 0)

print("\n" + ("✅ PHASE 0 PASS" if ok else "❌ PHASE 0 FAIL"))
sys.exit(0 if ok else 1)
