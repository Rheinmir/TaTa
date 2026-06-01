# Technical Stack & Architecture
**Type:** source
**Tags:** architecture, tech-stack, system-design

Tài liệu đặc tả kiến trúc kỹ thuật và stack công nghệ của hệ thống TaTa (Team Automated Task Agent).

## Notes
* **Tech Stack:** Python 3.10+, Supabase, Neo4j Graph DB, Vector DB, Notion API, Slack Events API, MS Teams Graph API, Zalo Webhook.
* **Kiến trúc chính:**
  * **AI Extraction Engine:** Sử dụng LLM để phân tích ngữ nghĩa tin nhắn.
  * **AI Orchestrator (Caveman):** Điều phối các workflow phức tạp.
  * **Queue & Audit Log (Supabase):** Bộ đệm trung gian lưu logs và tránh rate limit.
  * **Sync Engine:** Đồng bộ hóa dữ liệu từ Supabase lên Notion.

## Origin
- **Source:** AGENT-code.md
- **Commit:** Initial
- **Date:** 2026-06-01
