# Operation Log

## 2026-06-11 — orca-workflow — proposal-enforcement (R7)
- Audit 6 skill: harness-update/tour/new-project-setup/join-project đạt; nhóm propose CHƯA — rule chỉ là chữ
- R7 proposal-complete: validator mới ép draft chờ duyệt phải có Agent Task Assignment (không ô trống) + seq html tồn tại + diagram-box ≥ số task. Wire vào PostToolUse + pre-commit, test 9/9
- 4 skill propose/orca-workflow cập nhật template (merge với DISPATCH BOARD do session khác thêm); phát hiện npx skills đã symlink hóa ~/.claude/skills → sửa tại ~/.agents/skills
- Sync rheinmir/setup@orca

> Từ 2026-06-10: dòng log phiên làm việc được **máy tự sinh** (SessionEnd hook đọc `.claude/audit/*.jsonl`) — không nhờ model nhớ. Chi tiết đầy đủ nằm trong JSONL audit.

## 2026-06-10 — skill — harness-update
- Skill mới /harness-update: case B (migrate llmwiki cũ) + case C (update bản mới) thành 1 lệnh gọi — Claude tự chạy installer, tự backfill nợ (Origin từ git log, sửa index), lặp tối đa 3 vòng, báo cáo 4 ý
- Installer cũng đã vá: ghi settings.json ở project ROOT để hooks load khi mở session tại root
- join-project giờ gợi ý /harness-update khi thấy harness MISSING; guide HTML thêm "cách lười"
- Sync rheinmir/setup@orca

## 2026-06-10 — orca-workflow — harness-tour
- Tour 3 tầng: auto-smoke cuối installer (3 rule BỊ CHẶN ✓), tour.sh diễn 5 cảnh sandbox tự dọn, skill /harness-tour cho Claude tự diễn trên project thật
- Sync rheinmir/setup@orca commit e5b85a6

## 2026-06-10 — orca-workflow — harness-install-migrate
- install-harness.sh: 1 lệnh, tự detect new/migrate, merge settings.json, baseline audit (rc=3 khi có nợ)
- Sync harness L0–L4 + hooks + L2 + skills lên rheinmir/setup@orca (commit 9030992)
- Skill update: new-project-setup (bước cài harness), join-project (check harness, read-only)
- Hướng dẫn: llmwiki/html/100626-harness-install-guide.html

## 2026-06-10 — propose-pair — sequence diagram cho gate
- Nâng cấp quy trình propose: từ nay propose = CẶP md (chi tiết) + html (sequence diagram hoạt họa) để duyệt ở USER GATE
- Sửa skill: skills/dev-loop/propose.md, skills/orchestrate/orca-workflow.md, ~/.claude/skills/orca-workflow/SKILL.md
- Demo: llmwiki/html/100626-harness-enforcement-stack-seq.html (3 luồng: ghi wiki, commit, kết thúc phiên)

## 2026-06-10 — docs-site-macos — harness-html-report
- Sinh báo cáo HTML 2 màu (legacy indigo / mới emerald): llmwiki/html/100626-harness-report.html

## 2026-06-10 — orca-workflow — harness-enforcement-stack
- Implement harness 5 lớp vendor-agnostic (proposal: draft/orca/100626-harness-enforcement-stack.md)
- Tạo: harness/{recipe.md, policy.yaml, validators/×4, scripts/wiki-health.py, evals/promptfooconfig.yaml}
- Tạo: llmwiki/.claude/{settings.json, hooks/×5}, .pre-commit-config.yaml (repo root)
- Test: 19/19 pass. Từ nay log phiên do SessionEnd hook tự sinh.

## 2026-04-28 — init — Knowledge Base initialized
- Created folder structure: concepts/, entities/, sources/, sources/draft/
- Created wiki/index.md, wiki/log.md
- Created AGENT.md

## 2026-06-11 — install-harness — mode=migrate
- Cài harness L0–L4 (validators, hooks, pre-commit, wiki-health, evals)

## 2026-06-11 — install-harness — mode=migrate
- Cài harness L0–L4 (validators, hooks, pre-commit, wiki-health, evals)
