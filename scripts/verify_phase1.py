"""Verify Phase 1 — lọc kênh 2 chiều + debounce theo hội thoại (offline FakeSource).

Dùng window=60s, clock điều khiển tay (truyền `now` vào harvest).
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
        cur.execute("TRUNCATE tata_ingest_state")
    _c.close()
else:
    os.environ["TATA_STORE_DIR"] = tempfile.mkdtemp(prefix="tata_phase1_")
    os.environ.pop("SUPABASE_URL", None); os.environ.pop("SUPABASE_KEY", None)
    print("[backend] JSON fallback (tempdir)")

from app.ingest import ChannelFilter, Message, FakeSource, IngestPipeline  # noqa: E402

ok = True
def check(label, cond):
    global ok; print(f"  {'✅' if cond else '❌'} {label}"); ok = ok and cond

print("== ChannelFilter (2 chiều) ==")
allow = ChannelFilter("allow", ["Zalo nhóm"])
block = ChannelFilter("block", ["Zalo spam"])
check("allow: nhận 'Zalo nhóm A'", allow.allows("Zalo nhóm A") is True)
check("allow: loại 'Zalo cá nhân'", allow.allows("Zalo cá nhân") is False)
check("block: loại 'Zalo spam'", block.allows("Zalo spam") is False)
check("block: nhận 'Zalo nhóm A'", block.allows("Zalo nhóm A") is True)
check("none: nhận tất cả", ChannelFilter().allows("bất kỳ") is True)

print("== Debounce pipeline (window=60) ==")
T = 1000.0
polls = [
    # poll 1 @ t=1000: A (2 tin), C (1 tin), SPAM (1 tin — sẽ bị block)
    [Message("A", "Zalo nhóm A", "Nam", "làm báo cáo Q2", T, "m1"),
     Message("A", "Zalo nhóm A", "Nam", "trước thứ 6 nhé", T, "m2"),
     Message("C", "Zalo nhóm C", "Hoa", "gửi file thiết kế", T, "m3"),
     Message("SPAM", "Zalo spam", "Bot", "khuyến mãi 90%", T, "m4")],
    # poll 2 @ t=1040: A có thêm 1 tin (vẫn đang nói)
    [Message("A", "Zalo nhóm A", "An", "ok em làm", 1040.0, "m5")],
]
src = FakeSource(polls)
pipe = IngestPipeline(src, ChannelFilter("block", ["Zalo spam"]), tenant_id="user-1", window_seconds=60)

n1 = pipe.poll_and_buffer()
check("poll1 nhận 3 tin (SPAM bị lọc)", n1 == 3)
check("harvest @1030 chưa lắng → 0 batch", len(pipe.harvest(now=1030)) == 0)

pipe.poll_and_buffer()  # poll2: A thêm tin @1040
b = pipe.harvest(now=1110)  # A im từ 1040 (70s≥60), C im từ 1000 → cả 2 lắng
by_conv = {x["conversation_id"]: x for x in b}
check("harvest @1110 → 2 batch (A,C)", len(b) == 2)
check("batch A gộp 3 tin", len(by_conv.get("A", {}).get("messages", [])) == 3)
check("batch C có 1 tin", len(by_conv.get("C", {}).get("messages", [])) == 1)
check("không có batch SPAM", "SPAM" not in by_conv)
check("harvest lại → rỗng (đã xoá pending)", len(pipe.harvest(now=1200)) == 0)

print("\n" + ("✅ PHASE 1 PASS" if ok else "❌ PHASE 1 FAIL"))
sys.exit(0 if ok else 1)
