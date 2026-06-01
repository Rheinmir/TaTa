# Operation Log

## 2026-06-01 — init — Khởi tạo Kho tri thức (Knowledge Base) ban đầu cho TaTa
- Khởi tạo cấu trúc các thư mục: `wiki/concepts/`, `wiki/entities/`, `wiki/sources/`, `wiki/sources/draft/`.
- Chuyển đổi và phân loại tài liệu khởi động dự án từ root vào wiki: `wiki/sources/AGENT-business.md` và `wiki/sources/AGENT-code.md`.
- Tạo file chỉ mục wiki `wiki/index.md` và ghi nhận nhật ký vận hành ban đầu.

## 2026-06-01 — init — Dựng khung ứng dụng (Scaffold Application) cho TaTa
- Thiết lập khung ứng dụng backend bằng FastAPI (`app/main.py`, `app/database.py`, `app/orchestrator.py`, `app/sync.py`, `app/cron_scanner.py`).
- Cấu hình file phụ thuộc `requirements.txt` và cập nhật tài liệu chạy ứng dụng tại `README.md`.
- Thiết lập giao diện điều khiển (Dashboard) frontend trực quan ứng dụng thiết kế glassmorphic (`html/index.html`, `html/style.css`, `html/app.js`).
- Khởi tạo trang khái niệm wiki `wiki/concepts/Architecture.md` và cập nhật liên kết chỉ mục wiki.

## 2026-06-01 — propose — Khởi chạy /orca-workflow cho Cron Job & Data Connection
- Nhận yêu cầu và tổng hợp ngữ cảnh phát triển tính năng Cron quét lịch sử và kết nối database (Supabase Queue) làm bài xử lý đầu tiên.
- Khởi tạo file proposal nháp tại `wiki/sources/draft/010626-cron-job-va-dau-noi-du-lieu.md`.
- Đăng ký trang proposal mới vào chỉ mục wiki `wiki/index.md` và cập nhật nhật ký.

## 2026-06-01 — init — Hiện thực hóa Cron Job & Kết nối Cơ sở dữ liệu đầu tiên
- Triển khai lớp kết nối `DatabaseConnector` trong `app/database.py` hỗ trợ client Supabase thật kết hợp cơ chế Local JSON database queue fallback (`supabase_mock_db.json`).
- Triển khai bộ quét lịch sử `ChatHistoryScanner` trong `app/cron_scanner.py` sử dụng bộ lọc regex heuristics nhận diện assignees, deadlines, priorities và tự sinh task lưu vào cơ sở dữ liệu.
- Tích hợp api endpoint `/api/cron/scan` và cập nhật toàn bộ API trong `app/main.py` để tương tác trực tiếp với dữ liệu lưu trữ thật.
- Đồng bộ hóa logic trigger cron quét và kết nối API tại Dashboard frontend `html/app.js`.
- Thực hiện chạy thử nghiệm (smoke check) thành công, tự động trích xuất và lưu trữ 2 tác vụ từ chat history.
- Chuyển giao trang proposal tri thức sang nguồn chính thức `wiki/sources/010626-cron-job-va-dau-noi-du-lieu.md`.
## 2026-06-01 — init — Tích hợp tầng Connectors & Luồng Claim dữ liệu thô
- Xây dựng lớp đầu nối `SlackConnector`, `TeamsConnector` và `ZaloConnector` trong `app/chat_connector.py` chứng minh cách kết nối API an toàn để lấy dữ liệu.
- Thiết lập bộ đệm trung gian chứa dữ liệu thô `RAW_CLAIMED_MESSAGES` phục vụ bước phân rã thu thập trước trích xuất sau.
- Tích hợp các API `/api/chat/raw`, `/api/chat/claim-mock` và `/api/chat/process-claimed/{msg_id}` vào `app/main.py`.
- Tải cấu trúc panel điều khiển "Live Chat Crawler (Bắt dữ liệu thô)" lên Dashboard và liên kết kết nối thời gian thực tại `llmwiki/html/index.html`, `llmwiki/html/app.js` và `llmwiki/html/style.css`.
- Đưa file proposal đặc tả kỹ thuật của Connectors lên trang chính thức [wiki/sources/010626-connectors-va-luong-claim.md](file:///Volumes/giatbhSSD%28APFS%29/orca/tata/TaTa/wiki/sources/010626-connectors-va-luong-claim.md) và cập nhật chỉ mục wiki.

## 2026-06-01 — init — Phân công Hiện thực hóa tích hợp MS Teams Graph API
- Khởi chạy luồng nghiên cứu và thiết kế chi tiết kết nối API Microsoft Teams.
- Tạo trang thực thể wiki `wiki/entities/teams_connector.md` mô tả cơ chế xác thực client credentials MSAL OAuth và truy vấn tin nhắn qua Graph API Endpoint.
- Định hướng luồng triển khai thực tế trên môi trường live cho MS Teams.

## 2026-06-01 — fix — Khắc phục lỗi và Tối ưu hóa Luồng Xác thực MS Teams Device Code Flow
- Khắc phục lỗi xác thực AD trên tài khoản cá nhân (AADSTS700016) bằng cách chuyển sang sử dụng Client ID của Visual Studio (`04b07795-8ddb-461a-bbee-02f9e1bf7b46`) và `consumers` authority.
- Thiết kế và triển khai cơ chế polling bất tuần tự (non-blocking) qua background thread độc lập để chờ lấy token mà không gây tắc nghẽn, đóng băng hoặc làm chậm FastAPI main thread.
- Thực hiện chạy thử nghiệm live thành công, lấy được mã đăng nhập Microsoft Live thật (`5PV7RBN8`).
- Cập nhật trang tri thức `wiki/sources/010626-teams-device-code-flow.md` để đồng bộ đặc tả kỹ thuật thực tế.

## 2026-06-01 — feat — Tích hợp Docker và Hiện thực hóa giải pháp Automated RPA & Persistent SSH Bridge
- Thiết kế và triển khai Dockerfile và docker-compose.yml phục vụ triển khai single-port (cổng 8000) chứa cả FastAPI Backend và Static Frontend Dashboard.
- Tạo client cào tự động `app/teams_automated_crawler.py` (RPA) kết nối trực tiếp đến Teams Web để vượt qua các chính sách bảo mật khóa chặt của doanh nghiệp (như Coteccons).
- Thiết lập endpoint tiếp nhận dữ liệu `/api/chat/push-raw` an toàn trên FastAPI backend.
- Soạn thảo tài liệu và giải pháp tự động hóa kết nối SSH vào máy ảo WSL2 vĩnh viễn không cần mật khẩu tại `wiki/sources/010626-persistent-wsl-ssh-bridge.md`.
- Đẩy toàn bộ thay đổi thành công lên GitHub repository để đồng bộ hóa deploy sang máy ảo WSL.
