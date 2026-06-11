# 100626-harness-tour
**Type:** draft
**Status:** implemented — chờ verify-before-commit promote

## Agent Task Assignment
| Task | Agent | Status |
|------|-------|--------|
| Tầng 1 auto-smoke trong installer (+ fix errexit nuốt exit 2) | Claude (main) | done |
| Tầng 2 tour.sh — test 5/5 cảnh pass, sandbox tự dọn | Claude (main) | done |
| Tầng 3 skill /harness-tour (global + template) | Claude (main) | done |
| Điểm chạm: new-project-setup + guide HTML section Tour | Claude (main) | done |
| Sync rheinmir/setup@orca (e5b85a6) | Claude (main) | done |
**Tags:** harness, tour, onboarding, dx
**Proposed:** 2026-06-10
**Sequence diagram (hoạt họa):** [html/100626-harness-tour-seq.html](../../../html/100626-harness-tour-seq.html)

## Plan — 3 tầng trải nghiệm "hệ thống này làm gì"
- [ ] Task 1 — Tầng 1: auto-smoke trong `install-harness.sh` — cuối install chạy 3 check máy (R1/R2/R5 phải BỊ CHẶN), in bảng ✓, mời chạy tour. <1s, không tạo file rác
- [ ] Task 2 — Tầng 2: `harness/scripts/tour.sh` — dựng sandbox /tmp, diễn 5 cảnh (R1, R2, R5, R3 index lệch, audit JSONL tự ghi), tự dọn sạch. Chạy được trong CI
- [ ] Task 3 — Tầng 3: skill `harness-tour` — Claude tự diễn 3 kịch bản trên project thật trong phiên sống (bị deny raw/, bị ép thêm Origin, bị Stop hook giữ), tường thuật từng rule, tự dọn demo
- [ ] Task 4 — Điểm chạm: new-project-setup thêm 1 dòng mời; guide HTML thêm section Tour
- [ ] Task 5 — Sync tất cả lên rheinmir/setup@orca

## Files sẽ tạo/sửa
| File | Action | Lý do |
|------|--------|-------|
| `harness/scripts/install-harness.sh` | modify | tầng 1 auto-smoke |
| `harness/scripts/tour.sh` | create | tầng 2 máy diễn kịch |
| `llmwiki/skills/utils/harness-tour.md` + `~/.claude/skills/harness-tour/SKILL.md` | create | tầng 3 tour trong phiên thật |
| `~/.claude/skills/new-project-setup/SKILL.md` | modify | 1 dòng mời |
| `llmwiki/html/100626-harness-install-guide.html` | modify | section Tour |
| `rheinmir/setup@orca` | push | template có đủ tour |

## Risks
- Tour tầng 3 chạy trên project thật → mọi cảnh phải tự dọn (xóa file demo + row index) và tuyệt đối không đụng file có sẵn
- Auto-smoke phải phân biệt "validator chặn đúng" (PASS) vs "validator lỗi/không chạy" (FAIL)

## Origin
- Đề xuất + duyệt trong session 2026-06-10, tiếp nối [[100626-harness-install-migrate]]
