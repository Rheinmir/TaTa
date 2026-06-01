# TaTa (Team Automated Task Agent)

TaTa là hệ thống quản lý và giao việc tự động qua AI Agent. Hệ thống tự động trích xuất các công việc phát sinh từ các cuộc trò chuyện nhóm, tự động đánh giá mức độ phức tạp và thời hạn để phân bổ, lưu trữ ở vùng đệm trung gian (Supabase) và đồng bộ mượt mà lên Notion dưới dạng dashboard quản lý trực quan.

---

## 🚀 Luồng hoạt động chính (Core Workflows)

1. **Kênh đầu vào (4 Kênh):**
   * **Chat nhóm (Group Chat):** Nhận sự kiện tin nhắn qua Slack, Microsoft Teams, Zalo.
   * **Self-chat:** Kênh chat riêng nơi người dùng nhắn tin trực tiếp để tự giao việc nhanh.
   * **Tạo thủ công (Manual Input):** Tạo task trực tiếp trên Dashboard.
   * **Cron Scanner:** Định kỳ quét tự động lịch sử chat của các tài khoản để thu thập tin nhắn bị bỏ sót.
2. **AI Extraction Engine:** Phân tích ngữ nghĩa tin nhắn, nhận diện người giao (`requester`), người nhận (`assignee`), nội dung công việc, deadline (ngầm định/rõ ràng) và mức độ ưu tiên.
3. **AI Orchestrator (Caveman):** Đánh giá độ phức tạp để phân luồng xử lý (tự xử lý qua nhiều bước hoặc bàn giao cho các Agent chuyên biệt).
4. **Database trung gian (Supabase):** Lưu trữ tạm thời làm hàng đợi (Queue buffer) để phòng tránh rate-limit Notion API và lưu trữ audit logs.
5. **Sync Engine:** Đồng bộ dữ liệu có kiểm soát từ Supabase lên Notion Database.

---

## 🛠 Cấu trúc thư mục (Folder Structure)

```text
TaTa/
├── app/                      # Mã nguồn Backend (Python FastAPI)
│   ├── main.py               # Entrypoint & API Server (health check, webhooks, tasks)
│   ├── database.py           # Kết nối Supabase & Neo4j
│   ├── orchestrator.py       # Bộ điều phối AI Orchestrator
│   ├── sync.py               # Công cụ đồng bộ lên Notion (Sync Engine)
│   └── cron_scanner.py       # Công cụ quét lịch sử chat tự động
├── llmwiki/                  # Thư mục chứa tài liệu wiki & các template tĩnh
│   ├── html/                 # Giao diện Dashboard quản trị trực quan (Vanilla HTML/CSS/JS)
│   │   ├── index.html        # Cấu trúc Dashboard Glassmorphism
│   │   ├── style.css         # Thiết kế giao diện Dark Mode & Hiệu ứng neon
│   │   └── app.js            # Xử lý tương tác & Kết nối API Realtime
├── wiki/                     # Kho tri thức của Agent (Knowledge Base)
│   ├── concepts/             # Các khái niệm hệ thống
│   ├── entities/             # Các thực thể hệ thống
│   └── sources/              # Tài liệu tham khảo & Đặc tả dự án
├── AGENT.md                  # Hướng dẫn quy định phát triển của Agent
├── .env.caveman              # Chứa API Key và Credentials (LLM, Neo4j, Supabase)
└── requirements.txt          # Các thư viện Python cần thiết
```

---

## ⚙️ Hướng dẫn khởi chạy Local (Local Setup Guide)

### 1. Chuẩn bị Môi trường Python
Đảm bảo bạn đã cài đặt Python 3.10+ trên máy.

### 2. Cài đặt các thư viện cần thiết
```bash
pip install -r requirements.txt
```

### 3. Cấu hình biến môi trường
Mở file `.env.caveman` ở root dự án và điền các API Key tương ứng:
```ini
LLM_API_KEY=your_llm_api_key_here
EMBEDDING_API_KEY=your_embedding_api_key_here
GRAPH_DATABASE_PASSWORD=your_neo4j_password_here
VECTOR_DB_PASSWORD=your_supabase_vector_db_password_here
```

### 4. Khởi chạy Backend API Server
Chạy máy chủ FastAPI bằng lệnh:
```bash
uvicorn app.main:app --reload --port 8000
```
API docs sẽ có tại: `http://localhost:8000/docs`  
Endpoint kiểm tra sức khỏe hệ thống: `http://localhost:8000/health`

### 5. Khởi chạy Dashboard Frontend
Mở trực tiếp file `llmwiki/html/index.html` trong bất kỳ trình duyệt web nào, hoặc chạy một local server để xem (ví dụ: dùng extension Live Server của VS Code, hoặc lệnh `python -m http.server` trong thư mục `llmwiki/html/`).

Giao diện Dashboard hỗ trợ:
*   Theo dõi và đồng bộ realtime với API Backend.
*   Cơ chế **tự động fallback về Offline Mode** (lưu trữ mock trong bộ nhớ Client) khi Backend chưa khởi chạy, giúp trải nghiệm giao diện mượt mà không bị gián đoạn.
