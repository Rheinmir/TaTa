# Business Specifications & Goals
**Type:** source
**Tags:** business, specification, goals

Tài liệu đặc tả nghiệp vụ, mục tiêu và các ràng buộc của hệ thống TaTa (Team Automated Task Agent) dựa trên yêu cầu từ người dùng.

## Notes
* **Hệ thống hỗ trợ giao việc thông minh:** Hỗ trợ giao việc qua các cửa sổ chat nhóm (team). Người dùng có thể giao việc và gán deadline để AI tự động đánh giá, từ đó quyết định assign (ủy quyền) cho Orchestrator (điều phối đa nhiệm) hay AI Agent chuyên biệt.
* **Tự động quét lịch sử chat để sinh task:** Tích hợp tính năng cron chạy định kỳ để quét toàn bộ dữ liệu chat của tài khoản người sử dụng, tự động phát hiện khi có người nhờ vả, trích xuất và lưu lại người yêu cầu, nội dung công việc, deadline, các ghi chú liên quan, v.v.
* **Kênh self-chat cá nhân:** Hỗ trợ người dùng tự chat với bản thân để tự giao việc một cách nhanh chóng.
* **Đồng bộ hóa lên Notion qua DB trung gian:** Dữ liệu sau khi trích xuất sẽ được tự động đẩy vào database trung gian (Supabase) làm vùng đệm, sau đó tiến hành push đồng bộ lên Notion để làm dashboard quản lý.

## Origin
- **Source:** Trực tiếp từ người dùng & AGENT-business.md
- **Commit:** Initial
- **Date:** 2026-06-01
