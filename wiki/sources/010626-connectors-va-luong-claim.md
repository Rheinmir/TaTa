# Proposal: Chat Connectors & Claim Flow Ingestion
**Type:** source
**Tags:** proposal, chat-connector, slack, ms-teams, zalo, claim-flow

Đề xuất xây dựng tầng kết nối thu thập dữ liệu thô (Live Chat Crawler/Claim) từ Slack, Microsoft Teams, Zalo và phân tách quy trình xử lý thành 2 bước trực quan.

## 1. Mục tiêu (Purpose)
*   **Chứng minh khả năng kết nối:** Xây dựng các lớp connector thực tế phục vụ xác thực chữ ký (Slack), lấy token MSAL OAuth (MS Teams Graph API) và phân tích sự kiện webhook (Zalo).
*   **Chiếu trực quan dữ liệu thô (Crawl display):** Đảm bảo tin nhắn thô được hiển thị ngay trước mắt người dùng dưới dạng thô trước khi chuyển qua bất kỳ bước phân tích AI nào.
*   **Phân rã 2 bước:** Tách bạch bước Thu thập dữ liệu (Crawl/Claim) và bước Trích xuất tác vụ bằng AI (AI Ingestion).

## 2. Đặc tả chi tiết (Specifications)

### A. Slack Signature Verification:
*   Sử dụng mã HMAC-SHA256 để kiểm chứng header `X-Slack-Signature` dựa trên timestamp `X-Slack-Request-Timestamp` và signing secret để phòng chống replay attacks.

### B. MS Teams Graph Token API:
*   Acquire Access Token từ Azure Active Directory sử dụng client_credentials flow qua cổng Graph API `/chats/{chat_id}/messages`.

### C. UI/UX Live Chat Crawler:
*   Bổ sung panel "Live Chat Crawler" trên Dashboard hiển thị các tin nhắn thô thu thập được kèm nguồn gốc rõ ràng (Slack, Teams, Zalo).
*   Từng tin nhắn thô có nút "AI Extract" để trigger phân tích heuristics riêng biệt.

## 3. Các thành phần bị tác động (Impacted Symbols)
*   `app/chat_connector.py` (Mới): Hiện thực các connector Slack, Teams, Zalo và bộ đệm thô `RAW_CLAIMED_MESSAGES`.
*   `app/main.py`: Tích hợp các API `/api/chat/raw`, `/api/chat/claim-mock`, và `/api/chat/process-claimed/{msg_id}`.
*   `llmwiki/html/index.html`: Thêm panel điều khiển Live Chat Crawler.
*   `llmwiki/html/app.js`: Kết nối frontend tương tác thời gian thực với cổng claim dữ liệu thô.
*   `llmwiki/html/style.css`: Tạo giao diện thẻ tin nhắn thô cao cấp.

## Origin
- **Source:** Draft: wiki/sources/draft/010626-connectors-va-luong-claim.md
- **Commit:** implement-chat-connectors
- **Date:** 2026-06-01
