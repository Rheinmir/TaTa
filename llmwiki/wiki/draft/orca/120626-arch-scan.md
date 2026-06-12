# 120626-arch-scan
**Type:** draft
**Status:** implemented — chờ verify-before-commit promote
**Tags:** harness, arch-scan, enforcement
**Proposed:** 2026-06-12
**Sequence diagram (hoạt họa):** [html/120626-arch-scan-seq.html](../../../html/120626-arch-scan-seq.html)

## Plan
- [ ] Task 1: `harness/scripts/arch-scan.py` — quét 4 loại xung đột văn-bản-vs-luật (flag bị classifier chặn, path wiki vi phạm R5, path skill stale, file wiki root ngoài allowlist); 0 token; exit 2 khi có finding, `--warn-only` cho cron
- [ ] Task 2: Wire vào `.pre-commit-config.yaml` (quét llmwiki/ trong repo mỗi commit) + test pass/fail
- [ ] Task 3: Sync template `rheinmir/setup@orca`

## Agent Task Assignment
| Task | Agent (CLI) | Lý do chọn | Status |
|------|------------|-----------|--------|
| Task 1 — scanner | Claude (main) | regex + false-positive handling từ audit vừa làm | done |
| Task 2 — wire + test | Claude (main) | đụng enforcement layer | done |
| Task 3 — sync | Claude (main) | cần SSH push | done |

## Files sẽ tạo/sửa
| File | Action | Lý do |
|------|--------|-------|
| `harness/scripts/arch-scan.py` | create | scanner định kỳ |
| `.pre-commit-config.yaml` | modify | gate mỗi commit |

## Risks
- False positive substring (llmwiki/raw → wiki/raw): xử lý bằng lookbehind, kèm allowlist dòng cảnh báo chứa từ "KHÔNG dùng"

## Origin
- Audit 2026-06-12 bắt 3 lỗi thật bằng tay → đóng gói thành scanner chạy định kỳ
