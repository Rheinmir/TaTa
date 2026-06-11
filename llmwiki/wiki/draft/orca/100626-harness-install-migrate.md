# 100626-harness-install-migrate
**Type:** draft
**Status:** implemented — chờ verify-before-commit promote

## Agent Task Assignment
| Task | Agent | Status |
|------|-------|--------|
| install-harness.sh (new/migrate, merge settings, baseline audit) | Claude (main) | done |
| Test sandbox 2 mode + vòng trả nợ + hook-merge vào event user có sẵn | Claude (main) | done |
| Update skill new-project-setup + join-project | Claude (main) | done |
| Sync harness/ + .claude/ + L2 + skills → rheinmir/setup@orca (9030992) | Claude (main) | done |
| HTML hướng dẫn lệnh + 2 sequence diagram | Claude (main) | done |
**Tags:** harness, install, migrate, orca-workflow
**Proposed:** 2026-06-10
**Sequence diagram (hoạt họa):** [html/100626-harness-install-guide.html](../../../html/100626-harness-install-guide.html) — kiêm file hướng dẫn lệnh cho 2 trường hợp

## Plan
- [ ] Task 1: Viết `harness/scripts/install-harness.sh` — idempotent, tự detect install mới vs migrate (`llmwiki/` đã tồn tại chưa), fallback clone template khi thiếu file nguồn, baseline-audit trước khi bật chặn
- [ ] Task 2: Test script cả 2 mode trong sandbox /tmp (new + migrate có nợ wiki cũ)
- [ ] Task 3: Update skill `new-project-setup` (thêm bước cài harness + smoke check) và `join-project` (note đọc harness)
- [ ] Task 4: Sync `harness/` + `llmwiki/.claude/` + `.pre-commit-config.yaml` + skills lên `rheinmir/setup@orca`
- [ ] Task 5: HTML hướng dẫn: lệnh phải chạy cho 2 trường hợp + sequence diagram luồng đi

## Files sẽ tạo/sửa
| File | Action | Lý do |
|------|--------|-------|
| `harness/scripts/install-harness.sh` | create | 1 lệnh cho cả install lẫn migrate |
| `~/.claude/skills/new-project-setup/SKILL.md` | modify | bước cài harness sau pull template |
| `~/.claude/skills/join-project/SKILL.md` | modify | note kiểm tra harness (read-only) |
| `rheinmir/setup@orca` | push | template repo có đủ máy móc enforcement |
| `llmwiki/html/100626-harness-install-guide.html` | create | hướng dẫn lệnh + luồng (deliverable user yêu cầu) |

## Risks
- Merge settings.json của project có sẵn: phải merge key, không ghi đè — backup trước
- Migrate bật Stop hook ngay sẽ block oan vì nợ wiki cũ → script chỉ audit + cảnh báo, KHÔNG tự bật khi còn nợ

## Origin
- Thảo luận + approve trong session 2026-06-10, tiếp nối [[100626-harness-enforcement-stack]]
