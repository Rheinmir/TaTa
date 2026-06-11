# 110626-proposal-enforcement
**Type:** draft
**Status:** promoted
**Tags:** harness, R7, propose, enforcement
**Proposed:** 2026-06-11
**Sequence diagram (hoạt họa):** [html/110626-proposal-enforcement-seq.html](../../html/110626-proposal-enforcement-seq.html) — một diagram cho TỪNG task bên dưới

## Plan
- [ ] Task 1: Thêm **R7 proposal-complete** vào `harness/policy.yaml` + cập nhật `recipe.md`
- [ ] Task 2: Viết `harness/validators/proposal_complete.py` — với draft có `## Plan` và `Status: proposed`: (a) bắt buộc bảng `## Agent Task Assignment` ≥1 row, không ô Agent nào trống; (b) link `**Sequence diagram**` trỏ file .html TỒN TẠI; (c) số `diagram-box` trong html ≥ số task trong Plan (mỗi phần việc một diagram)
- [ ] Task 3: Wire R7 vào máy — PostToolUse hook (ghi draft là bị kiểm ngay) + `.pre-commit-config.yaml` (gate commit) + test sandbox đủ nhánh pass/fail
- [ ] Task 4: Sửa 4 file skill (propose ×2, orca-workflow ×2): template propose bắt buộc có bảng Agent Task Assignment NGAY LÚC PROPOSE (Task | Agent/CLI | Status=pending, chọn agent theo bảng chi phí: OpenCode big-pickle $0 cho việc rẻ, Claude cho architectural...) + yêu cầu seq diagram per-task
- [ ] Task 5: Sync toàn bộ lên `rheinmir/setup@orca`

## Agent Task Assignment
| Task | Agent (CLI) | Lý do chọn | Status |
|------|------------|-----------|--------|
| Task 1 — policy + recipe | Claude (main) | sửa file khai báo trung tâm, ít dòng | done |
| Task 2 — validator R7 | Claude (main) | logic parse + edge case, cần test kỹ | done (test 9/9) |
| Task 3 — wire hooks/pre-commit + test | Claude (main) | đụng enforcement layer, rủi ro brick phiên | done |
| Task 4 — sửa 4 skill markdown (merge với DISPATCH BOARD từ session khác) | Claude (main) | text ngắn nhưng là luật gate — không giao agent rẻ | done |
| Task 5 — sync template repo | Claude (main) | cần SSH push | done |

> Không dispatch OpenCode/agy lần này: tổng khối lượng nhỏ, toàn file luật — chi phí điều phối > tiền tiết kiệm.

## Files sẽ tạo/sửa
| File | Action | Lý do |
|------|--------|-------|
| `harness/policy.yaml` | modify | khai báo R7 |
| `harness/validators/proposal_complete.py` | create | máy ép proposal đủ chuẩn |
| `llmwiki/.claude/hooks/post_tool_use.py` | modify | kiểm draft ngay khi ghi |
| `.pre-commit-config.yaml` | modify | gate commit |
| `propose` SKILL ×2, `orca-workflow` ×2 | modify | template mới: Agent table lúc propose + seq per-task |
| `harness/recipe.md` | modify | bảng rule thêm R7 |
| `rheinmir/setup@orca` | push | template repo |

## Risks
- Draft kiểu output-report (không phải plan) không được phép bị bắt oan → validator chỉ enforce khi file CÓ section `## Plan`
- Draft cũ đã implemented: `Status` không còn `proposed` → tự miễn, không retro-fail
- Đếm task bằng `- [ ]` dưới `## Plan` — proposal viết kiểu khác sẽ không bị đếm; ghi rõ format vào skill template

## Origin
- Audit 6 skill ngày 2026-06-11 theo yêu cầu force của user, tiếp nối [[100626-harness-enforcement-stack]]
- **Commit:** a599d54 — harness: dựng lớp enforcement/audit/evals
- **Date promoted:** 2026-06-11
