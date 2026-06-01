# Architecture
**Type:** concept
**Tags:** architecture, scaffold

TaTa được xây dựng trên mô hình 7 lớp (Layers) kết hợp hài hòa giữa bộ máy AI trích xuất thông tin thông minh (Python FastAPI & Caveman SDK), cơ sở dữ liệu đồ thị ngữ cảnh (Neo4j) và cơ sở dữ liệu trung gian làm hàng đợi buffer (Supabase PostgreSQL), đồng bộ hóa trực tiếp lên Notion.

## Notes
- Hệ thống hỗ trợ xử lý đa kênh đầu vào qua FastAPI Webhook và tự động quét định kỳ (Cron Scanner).
- Việc chia tách các lớp giúp tăng khả năng chịu tải và chống lỗi khi tương tác với các bên thứ ba như Notion API (tránh rate-limit).
- Liên kết tri thức liên quan:
  - [[AGENT-business]] (mục tiêu và ràng buộc nghiệp vụ).
  - [[AGENT-code]] (đặc tả stack công nghệ và chi tiết sơ đồ kiến trúc).

## Origin
- **Source:** `AGENT-code.md`
- **Commit:** scaffold-init
- **Date:** 2026-06-01
