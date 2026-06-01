Tôi đã đọc và hiểu rõ cấu trúc của file SVG                              

  ai_task_management_architecture.svg .

  Đây là sơ đồ kiến trúc của Hệ thống giao việc qua AI (AI Task Management

  Architecture) từ nguồn đầu vào đến Notion dashboard, bao gồm 7 tầng/thành

  phần chính sau:

  ### 1. Nguồn đầu vào (Input Sources) - Layer 1

  • Team chat windows: Nhận diện tin nhắn từ Slack, Microsoft Teams, Zalo.

  • Self-chat: Kênh chat riêng nơi người dùng tự giao việc cho mình.

  • Manual input: Tạo task trực tiếp một cách thủ công.

  • Cron scanner: Quét tự động lịch sử chat định kỳ (auto-crawl).

  ### 2. AI Extraction Engine - Layer 2

  • Bộ máy xử lý ngôn ngữ tự nhiên đảm nhận:

      • Phân tích ngữ nghĩa để trích xuất các thông tin: requester (người

      yêu cầu), nội dung công việc, deadline, và assignee gợi ý (người thực

      hiện).

      • Phân loại mức độ ưu tiên và phân biệt tin nhắn thuộc dạng task

      (công việc), note (ghi chú) hay FYI (thông tin tham khảo).

  ### 3. AI Orchestrator - Layer 3

  • Điều phối viên trung tâm thực hiện:

      • Đánh giá công việc và quyết định phân luồng xử lý trực tiếp bởi

      Orchestrator hay bàn giao cho các Agent chuyên biệt.

      • Giải quyết xung đột deadline và phân chia công việc dựa trên tải

      lượng công việc (workload) hiện tại của nhân sự.

  ### 4. Phân luồng xử lý - Layer 4a &amp; 4b

  Sơ đồ rẽ nhánh sau bước Orchestrator thành hai hướng xử lý:

  • Orchestrator tasks: Dành cho các quy trình công việc phức tạp, cần thực

  hiện qua nhiều bước liên tục (multi-step).

  • AI Agents: Dành cho các công việc đơn lẻ, các tác vụ tự động hóa và

  chạy kịch bản (automation, script).

  • Sau đó, cả hai nhánh này đều hội tụ lại và đẩy dữ liệu về cơ sở dữ liệu.

  ### 5. Database trung gian (Intermediate DB) - Layer 5

  • Sử dụng PostgreSQL / Supabase làm nơi lưu trữ với các chức năng:

      • Lưu trữ thông tin task, theo dõi trạng thái (status tracking), lưu

      nhật ký hệ thống (audit log), và làm hàng đợi trung chuyển (queue

      buffer).

      • Kích hoạt Webhook khi có sự thay đổi thông tin (update).

  ### 6. Sync engine - Layer 6

  • Động cơ đồng bộ dữ liệu đảm nhận:

      • Đẩy dữ liệu qua Notion API.

      • Cập nhật theo lô (batch update), xử lý xung đột dữ liệu và quản lý

      hàng đợi thử lại khi gặp lỗi (retry queue).

  ### 7. Notion Dashboard - Layer 7

  • Điểm cuối hiển thị thông tin cho người dùng bao gồm:

      • Bảng công việc (Task board), dòng thời gian (Timeline), chế độ xem

      theo người thực hiện (By assignee), và chế độ xem theo trạng thái

      (Status view).