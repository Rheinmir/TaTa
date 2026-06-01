# CONTEXT
Trước khi viết app, phải kiểm tra Caveman đã sẵn sàng chưa.

# PHẢI LÀM
1. CHECK Caveman có chưa: `pip show caveman` hoặc `python -c "import caveman"`.
   - Lệnh lỗi (pip/python không có): DỪNG. Báo lỗi, yêu cầu kiểm tra Python environment. Đợi người dùng gõ "tiếp tục" rồi CHẠY LẠI — không được bỏ qua.
   - Caveman CHƯA cài: DỪNG. Nói: "⚠️ Caveman chưa cài. Chạy `pip install caveman` rồi gõ 'tiếp tục'." Đợi "tiếp tục" rồi CHẠY LẠI — không được bỏ qua.
   - Caveman ĐÃ cài: tiếp bước 2.

2. Test kết nối ngay — khởi tạo Caveman client, gọi ping/health để xác nhận Neo4j và Supabase liên lạc được. Caveman có thể lưu credentials sẵn trong bộ nhớ dù env vars có vẻ trống.
   - Thành công: nói "✅ Caveman MCP kết nối thành công." rồi qua bước 04. Đừng chặn vì env vars thiếu.
   - Thất bại: tiếp bước 3.

3. Kết nối fail — kiểm tra từng cái: `LLM_API_KEY`, `GRAPH_DATABASE_PASSWORD`, `VECTOR_DB_PASSWORD`:
   - Kiểm tra system/shell env vars trước.
   - Không có → kiểm tra file `.env.caveman` (không có file = coi như thiếu).
   - Báo chính xác cái nào thiếu, mỗi cái nối với dịch vụ gì (LLM / Neo4j / Supabase).
   - Hiện lỗi kết nối gốc cùng các biến thiếu.
   - DỪNG. Đợi "tiếp tục" rồi CHẠY LẠI từ bước 2 — không được nhảy thẳng đến thành công.

# LÀM ĐI
Chạy logic trên ngay. Kiểm tra trạng thái cấu trúc và hành động theo kết quả.
