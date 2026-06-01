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

