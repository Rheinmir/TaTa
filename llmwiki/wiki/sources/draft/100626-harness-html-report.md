# 100626-harness-html-report
**Type:** draft
**Status:** proposed
**Tags:** docs-site-macos, output-report
**Proposed:** 2026-06-10

## What
Báo cáo HTML single-file về toàn bộ nâng cấp harness 10/06/2026, hệ 2 màu legacy (indigo) vs mới (emerald), 3 sơ đồ luồng tương tác kéo-thả.

## Output
- Trang docs macOS-style 6 section: llmwiki là gì, cây thư mục 2 màu, kiến trúc 5 lớp, bảng file thay đổi, 3 luồng làm việc mix cũ/mới, vận hành + checklist kích hoạt
- Sơ đồ SVG draggable: lớp mới bảo vệ tài sản legacy · vòng đời tool call qua hooks · dev-loop với 3 chốt chặn mới · wiki-loop với vòng đo nền
- Preview: `http://localhost:8765/llmwiki/html/100626-harness-report.html`

## Files
| File | Action |
|------|--------|
| `llmwiki/html/100626-harness-report.html` | created |

## Notes
- Invoked via: `/docs-site-macos` skill
- Cặp với proposal implement: [[100626-harness-enforcement-stack]]

## Origin
- **Draft:** `wiki/sources/draft/100626-harness-html-report.md`
- **Commit:** _(filled by verify-before-commit)_
- **Date promoted:** _(filled by verify-before-commit)_
