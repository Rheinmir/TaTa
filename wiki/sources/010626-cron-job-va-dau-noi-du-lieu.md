# Proposal: Cron Job & Data Connection Setup
**Type:** source
**Tags:** proposal, cron-job, supabase, database, queue

Đề xuất thiết lập hệ thống quét lịch sử chat tự động (Cron Scanner) và đầu nối lưu trữ dữ liệu trung gian (Supabase Database Queue) làm bước xử lý đầu tiên cho hệ thống TaTa.

## 1. Mục tiêu (Purpose)
*   **Tự động hóa phát hiện công việc:** Hiện thực hóa tính năng quét lịch sử hội thoại nhóm/cá nhân để tự động sinh task bằng AI.
*   **Đảm bảo lưu trữ tin cậy:** Thiết lập kết nối cơ sở dữ liệu Supabase, tạo bảng hàng đợi (queue buffer) để lưu trữ task trước khi đẩy lên Notion.
*   **Tránh bỏ sót yêu cầu:** Đảm bảo ghi nhận đầy đủ: người yêu cầu (`requester`), nội dung (`title`), deadline, ghi chú (`note`), nguồn tin nhắn (`source`).

## 2. Đặc tả chi tiết (Specifications)

### A. Cron Chat Scanner:
*   Mô phỏng quét lịch sử chat thông qua một cron job chạy định kỳ bằng Python.
*   Trích xuất dữ liệu chat chứa các mẫu câu giao việc/nhờ vả.
*   Chuyển tiếp payload tin nhắn thô sang **AI Extraction Engine** để parse ngữ nghĩa.

### B. Database Queue (Supabase):
*   Thiết lập cấu trúc bảng `tasks_queue` trong PostgreSQL/Supabase:
    ```sql
    CREATE TABLE tasks_queue (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        title TEXT NOT NULL,
        requester TEXT NOT NULL,
        assignee TEXT DEFAULT 'Unassigned',
        deadline TEXT,
        priority TEXT DEFAULT 'Medium',
        source TEXT NOT NULL,
        status TEXT DEFAULT 'Pending Review',
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        synced_to_notion BOOLEAN DEFAULT FALSE,
        audit_log JSONB DEFAULT '[]'::jsonb
    );
    ```
*   Xây dựng module `app/database.py` kết nối trực tiếp đến Supabase client thật sử dụng `supabase-py`.

## 3. Các thành phần bị tác động (Impacted Symbols)
*   `app/cron_scanner.py`: Hiện thực hóa lớp `ChatHistoryScanner` để quét giả lập và sinh tin nhắn.
*   `app/database.py`: Bổ sung thư viện `supabase` và khởi tạo kết nối thật, thêm các hàm CRUD tác vụ: `insert_task`, `get_pending_tasks`, `mark_as_synced`.
*   `app/main.py`: Cập nhật endpoint `/api/tasks` để đọc/ghi từ Supabase thật thay vì mock dữ liệu trong bộ nhớ.

## 4. Kế hoạch triển khai (Implementation Plan)
1.  **Bước 1:** Khởi tạo bảng `tasks_queue` trên Supabase (hoặc giả lập local PostgreSQL).
2.  **Bước 2:** Cài đặt các thư viện `supabase` vào python environment.
3.  **Bước 3:** Hoàn thiện kết nối DB trong `app/database.py`.
4.  **Bước 4:** Xây dựng logic quét và tự sinh task trong `app/cron_scanner.py`.
5.  **Bước 5:** Tích hợp đầu nối và kiểm nghiệm thông qua API `app/main.py`.

## Origin
- **Source:** Draft: wiki/sources/draft/010626-cron-job-va-dau-noi-du-lieu.md
- **Commit:** implement-cron-db
- **Date:** 2026-06-01
