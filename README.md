# TaTa
Team Automated Task Agent
Luồng hoạt động chính:

Input sources — 4 kênh đầu vào: chat nhóm (Slack/Teams/Zalo), self-chat (user nhắn cho chính mình), tạo task thủ công, và cron job tự động quét lịch sử chat toàn bộ tài khoản.
AI Extraction Engine — đây là trái tim: parse ngữ nghĩa, nhận dạng ai đang nhờ ai, nội dung yêu cầu là gì, deadline ngầm định hay rõ ràng, mức độ ưu tiên. Phân biệt được "task cần làm" với "FYI / note thông tin".
AI Orchestrator — nhận task đã được trích xuất, đánh giá độ phức tạp rồi quyết định: tự xử lý workflow nhiều bước (orchestrator), hay delegate cho agent chuyên biệt (automation đơn lẻ, script, API call).
Database trung gian — buffer quan trọng, không nên push thẳng lên Notion. Lưu full audit log, track status, làm queue nếu Notion API rate-limit. Supabase là lựa chọn tốt vì có realtime webhook built-in.
Sync engine → Notion — push có kiểm soát: batch update, retry khi fail, resolve conflict khi cùng lúc có nhiều update.

Một số điểm kỹ thuật cần lưu ý khi build:
Phần cron scanner cần được thiết kế cẩn thận — không phải scrape liên tục mà nên dùng webhook/event từ các platform (Slack Events API, Teams Graph API) để phát hiện message mới theo real-time thay vì poll. Việc phân biệt "được nhờ vả" vs "đang nhờ người khác" trong chat cần prompt engineering tốt kèm context về các thành viên trong team.
