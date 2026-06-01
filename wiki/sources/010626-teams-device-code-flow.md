# Proposal: MS Teams Device Code Flow OAuth2 Integration
**Type:** source
**Tags:** proposal, ms-teams, msal, device-code-flow, graph-api

Đề xuất hiện thực hóa luồng xác thực mã thiết bị (Device Code Flow) tích hợp Microsoft Teams cá nhân (Personal Account) vào hệ thống TaTa.

## 1. Mục tiêu (Purpose)
*   **Hỗ trợ tài khoản cá nhân:** Bỏ qua sự phụ thuộc vào quyền Tenant Admin của doanh nghiệp, cho phép người dùng cá nhân tự kết nối.
*   **Duy trì trạng thái kết nối vĩnh viễn (Token Persistence):** Lưu trữ Refresh Token cục bộ để tự động cập nhật Access Token chạy nền mà không bắt người dùng đăng nhập lại nhiều lần.
*   **Trải nghiệm người dùng trực quan:** Thiết lập giao diện điều khiển giúp người dùng lấy mã đăng nhập trực tiếp trên Dashboard, nhấp liên kết và xác thực trực quan.

### A. MSAL Device Code Flow trong Python:
*   Sử dụng `msal.PublicClientApplication` với Client ID đáng tin cậy toàn cầu của Visual Studio (`04b07795-8ddb-461a-bbee-02f9e1bf7b46`) để hỗ trợ tài khoản Microsoft cá nhân (Personal Accounts) mà không cần đăng ký ứng dụng trong Azure AD cá nhân.
*   Khởi chạy luồng lấy mã đăng nhập:
    ```python
    flow = app.initiate_device_flow(scopes=["Chat.Read", "User.Read"])
    # Trả về: user_code (mã), verification_uri (link đăng nhập)
    ```
*   **Luồng xử lý bất đồng bộ (Non-blocking):** Nhằm tránh chặn FastAPI main thread khi thực hiện `acquire_token_by_device_flow` (vốn là hàm block liên tục poll máy chủ), hệ thống khởi chạy một background thread độc lập để chờ người dùng login.
*   Lưu cache token vào file `teams_token.json` để tự động hóa tái xác thực bằng refresh token.

### B. Graph API Message Crawling:
*   Gọi endpoint `GET https://graph.microsoft.com/v1.0/me/chats` lấy danh sách phòng chat.
*   Gọi endpoint `GET https://graph.microsoft.com/v1.0/chats/{chat_id}/messages` để quét dữ liệu tin nhắn thô.

### C. FastAPI Endpoints & UI:
*   `POST /api/chat/teams/auth-start`: Kích hoạt và trả về thông tin link + mã thiết bị đăng nhập, đồng thời khởi chạy background polling thread.
*   `GET /api/chat/teams/auth-status`: API non-blocking trả về trạng thái hiện tại tức thời (`pending`, `success`, `inactive`, `error`) để frontend poll an toàn.
*   **UI Integration:** Hiển thị popup hoặc panel nhập mã sang trọng trên Dashboard.

## 3. Các thành phần bị tác động (Impacted Symbols)
*   `app/chat_connector.py`: Triển khai lớp `TeamsDeviceCodeConnector` và tích hợp lưu trữ `teams_token.json`.
*   `app/main.py`: Thêm các endpoint quản trị xác thực tương tác `/api/chat/teams/*`.
*   `llmwiki/html/index.html` & `llmwiki/html/app.js`: Tích hợp giao diện hiển thị mã xác thực Teams.

## Origin
- **Source:** Draft: wiki/sources/draft/010626-teams-device-code-flow.md
- **Commit:** implement-teams-device-flow
- **Date:** 2026-06-01
