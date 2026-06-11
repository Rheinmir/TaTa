# 100626-harness-enforcement-stack
**Type:** draft
**Status:** promoted
**Tags:** harness, enforcement, observability, evals
**Proposed:** 2026-06-10
**Implemented:** 2026-06-10
**Sequence diagram (hoạt họa):** [html/100626-harness-enforcement-stack-seq.html](../../html/100626-harness-enforcement-stack-seq.html) — luồng code đi qua hooks/validators/pre-commit, xem khi duyệt gate

## Agent Task Assignment
| Task | Agent | Status |
|------|-------|--------|
| Crawl GitHub verify giải pháp (3 track) | Claude (main, WebSearch trực tiếp) | done |
| Task 0 recipe.md · Task 1 policy.yaml · Task 2 validators | Claude (main) | done |
| Task 3 L1 Claude Code adapter · Task 4 pre-commit · Task 5 audit | Claude (main) | done |
| Task 6 wiki-health · Task 7 promptfoo config | Claude (main) | done |
| Task 8 PoC statewright | — | deferred |
| Test suite 19 case validators + hooks end-to-end | Claude (main) | done (19/19 pass) |

## Bối cảnh

llmwiki đã có process + knowledge nhưng thiếu 3 lớp harness: enforcement bằng máy, observability, evals. Đã crawl GitHub trực tiếp (10/06/2026) để verify giải pháp. Tiêu chí: chạy ngầm, 0 slash command mới, ưu tiên script 0-token; LLM chỉ dùng ở eval định kỳ.

**Yêu cầu bổ sung:** kiến trúc phải vendor-agnostic — dùng được cho các hệ thống/CLI khác (Codex, OpenCode, Gemini CLI, Cursor...). Logic enforcement nằm trong script độc lập; mỗi vendor chỉ là một adapter mỏng. Kèm một file **recipe kiến trúc** để khi cần là cook ra bản vendor mới ngay.

## Kiến trúc 5 lớp (vendor-agnostic)

```
L0 POLICY      policy.yaml — các bất biến (R1..R6), thuần khai báo, không dính vendor
L1 SESSION     adapter mỏng theo vendor (Claude hooks / OpenCode plugin / Codex config)
               → đều gọi chung validators/ (Python, đọc JSON từ stdin, exit 2 = block)
L2 REPO        pre-commit/lefthook — backstop 100% vendor-neutral, agent nào edit cũng bị chặn
L3 AUDIT       transcript/hook parser per vendor + ccusage (bản thân nó đã multi-vendor)
L4 EVALS       wiki-health script (vendor-neutral) + promptfoo (đổi provider là đổi vendor)
```

Điểm chốt: **~80% công sức nằm ở validators + L2 + L4 — dùng lại nguyên xi cho mọi vendor.** Chỉ L1 wiring và L3 parser là khác nhau, và đó chính là phần recipe mô tả cách cook.

## Kết quả crawl (verified 10/06/2026)

| Tool | Stars | Trạng thái | Vai trò |
|------|-------|-----------|---------|
| [ccusage](https://github.com/ryoppippi/ccusage) | 15.9k | v20.0.9 — release 09/06/2026 | Cost/token tracking, hỗ trợ cả Claude Code + Codex + OpenCode + Gemini CLI (khớp setup Orca đa agent) |
| [awesome-harness-engineering](https://github.com/ai-boost/awesome-harness-engineering) | 1.8k | active | Checklist 12 primitive của harness — dùng làm khung chấm điểm llmwiki |
| [statewright](https://github.com/statewright/statewright) | mới (HN trending) | active, Rust, Apache 2.0 | State-machine guardrail: khóa tool theo phase (plan = read-only, implement = edit, test = test-only). Map thẳng vào wiki-loop/dev-loop. Deterministic, không LLM |
| [dwarvesf/claude-guardrails](https://github.com/dwarvesf/claude-guardrails) | 22 | v0.3.8 — 04/2026 | Bộ deny rules + hooks cài bằng `npx`, merge vào settings.json có backup |
| [disler/claude-code-hooks-mastery](https://github.com/disler/claude-code-hooks-mastery) | ~2k+ | active, đủ 13 hook events | Pattern nguồn cho hooks tự viết |
| [obey](https://github.com/Lexxes-Projects/obey) | mới | active | Viết rule bằng ngôn ngữ tự nhiên → enforce qua 17 lifecycle hooks |
| [promptfoo](https://www.promptfoo.dev/docs/guides/evaluate-coding-agents/) | ~9k+ | `anthropic:claude-agent-sdk` là provider chính thức | Golden-question eval; assertion deterministic trước, llm-rubric sau, có cost threshold |
| pre-commit / lefthook / lychee / markdownlint-cli2 | 13k+/7k/3k/5k | chuẩn de-facto | Backstop git-level, 0 token |

## Plan

- [ ] Task 0 — **Recipe kiến trúc (deliverable trung tâm)**: viết `harness/recipe.md` — mô tả 5 lớp, contract của validator (input JSON `{file_path, tool_name, content}` qua stdin, exit 0/2), bảng mapping enforcement-point per vendor (Claude Code hooks ↔ OpenCode plugin ↔ Codex ↔ Gemini CLI ↔ Cursor), và quy trình 4 bước "cook bản vendor mới": (1) viết adapter L1 gọi validators, (2) trỏ parser L3 vào transcript format của vendor, (3) đổi provider promptfoo, (4) L0/L2/L4 giữ nguyên
- [ ] Task 1 — **L0 Policy**: `harness/policy.yaml` khai báo R1..R6 (no-write-raw, origin-required, index-sync, log-append, folder-structure, verify-before-commit) — vendor-free
- [ ] Task 2 — **Validators dùng chung (0 token)**: `harness/validators/*.py` — mỗi rule một script đọc JSON stdin, exit 2 + stderr khi vi phạm. KHÔNG chứa code đặc thù vendor
- [ ] Task 3 — **L1 adapter cho Claude Code (vendor đầu tiên)**: `.claude/settings.json` với `permissions.deny` (raw/) + hooks PreToolUse/PostToolUse/Stop chỉ làm nhiệm vụ wire stdin → validators
- [ ] Task 4 — **L2 git backstop (vendor-neutral)**: `.pre-commit-config.yaml` gọi lại đúng validators + markdownlint custom rule + lychee --offline — agent nào commit cũng bị gate
- [ ] Task 5 — **L3 Audit**: hook JSONL audit (PostToolUse/Stop/SessionEnd append `.claude/audit/*.jsonl`), script sinh log.md từ JSONL; cài ccusage statusline (ccusage tự multi-vendor sẵn)
- [ ] Task 6 — **L4 Evals tĩnh (0 token)**: `harness/scripts/wiki-health.py` — broken wikilink, orphan, index coverage, stale; cron + CSV trend — vendor-neutral
- [ ] Task 7 — **L4 Evals LLM (có phí, định kỳ)**: promptfoo, 15-20 golden questions, assertion deterministic + cost threshold, weekly (~$1-5/tuần); provider = `anthropic:claude-agent-sdk`, đổi vendor chỉ đổi block `providers:`
- [ ] Task 8 — **(Đánh giá thêm, chưa cài)**: PoC statewright — bản thân nó đã cross-vendor (Claude Code/Codex/Cursor/opencode) nên là ứng viên thay L1 nếu muốn 1 engine cho mọi CLI

## Files sẽ tạo/sửa

| File | Action | Lý do |
|------|--------|-------|
| `harness/recipe.md` | create | **recipe kiến trúc — tài liệu cook bản vendor mới** |
| `harness/policy.yaml` | create | L0 — bất biến khai báo, vendor-free |
| `harness/validators/*.py` (~5 file) | create | logic enforcement dùng chung mọi vendor |
| `llmwiki/.claude/settings.json` | create/modify | L1 adapter Claude Code (deny + hook wiring) |
| `llmwiki/.claude/hooks/*.py` (3 file mỏng) | create | chỉ wire stdin → validators |
| `llmwiki/.pre-commit-config.yaml` | create | L2 backstop vendor-neutral |
| `harness/scripts/wiki-health.py` | create | L4 evals tĩnh |
| `harness/evals/promptfooconfig.yaml` | create | L4 golden questions, đổi provider = đổi vendor |
| `llmwiki/wiki/log.md` | modify | sinh tự động từ JSONL audit |
| `harness/harness.md` | modify | append kiến trúc 5 lớp + checklist 12 primitive |

## Cân bằng chi phí

- Slash command mới: **0** — tất cả chạy ngầm qua hooks/cron/git
- Token: hooks + scripts = **0 token**; chỉ promptfoo weekly tốn ~$1-5/tuần (tắt được)
- Hook chạy mỗi tool call nhưng là Python local nên không tốn API

## Risks

- Không phải vendor nào cũng có blocking hook tương đương PreToolUse (khả năng chặn realtime khác nhau) → với vendor yếu, L2 (git backstop) trở thành gate cứng duy nhất — recipe phải ghi rõ mức enforcement đạt được per vendor
- Stop hook quá chặt có thể khóa phiên khi làm việc ngoài wiki → cần scope check chỉ khi có file wiki thay đổi
- PostToolUse exit 2 lặp vô hạn nếu Claude không sửa được → cần max-retry/bypass flag
- statewright còn mới (chưa nhiều sao), có managed cloud tier → chỉ PoC, không phụ thuộc
- ccusage cost là ước tính theo pricing công khai (notional với gói Max)

## Origin

- Crawl trực tiếp GitHub/web ngày 2026-06-10 từ session chính (3 subagent trước đó bị chặn web, kết quả training-data chỉ dùng làm khung)
- **Commit:** a599d54 — harness: dựng lớp enforcement/audit/evals
- **Date promoted:** 2026-06-11
