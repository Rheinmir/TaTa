# Chat Connectors Integration Guide
**Type:** source
**Tags:** integration, guide, slack, ms-teams, zalo, api-setup

Hướng dẫn chi tiết từng bước (Step-by-step) cấu hình kết nối API của Slack Events, Microsoft Teams Graph, và Zalo OA để thu thập dữ liệu tin nhắn thô về hệ thống TaTa.

---

## 1. Microsoft Teams Graph API Integration Guide

### Bước 1: Đăng ký Ứng dụng trên Azure AD
1.  Truy cập [Azure Portal](https://portal.azure.com/) bằng tài khoản quản trị.
2.  Tìm và chọn **Microsoft Entra ID** (trước đây là Azure Active Directory).
3.  Chọn **App registrations** ở menu bên trái $\rightarrow$ Click **New registration**.
4.  Nhập tên ứng dụng (ví dụ: `TaTa Connector App`) $\rightarrow$ Click **Register**.
5.  Ghi lại các thông số:
    *   **Application (client) ID**
    *   **Directory (tenant) ID**

### Bước 2: Tạo Client Secret
1.  Chọn **Certificates & secrets** ở menu bên trái $\rightarrow$ Click **New client secret**.
2.  Nhập mô tả và thời gian hết hạn $\rightarrow$ Click **Add**.
3.  **QUAN TRỌNG:** Copy lại giá trị **Value** của secret ngay lập tức (nó sẽ bị ẩn sau khi rời trang).

### Bước 3: Cấu hình Quyền hạn (API Permissions)
1.  Chọn **API permissions** $\rightarrow$ Click **Add a permission**.
2.  Chọn **Microsoft Graph** $\rightarrow$ Chọn **Application permissions** (Quyền chạy ngầm của ứng dụng).
3.  Tìm và check các quyền sau:
    *   `Chat.Read.All` (Đọc toàn bộ phòng chat nhóm/cá nhân).
    *   `ChannelMessage.Read.All` (Đọc tin nhắn trong các kênh).
4.  Click **Add permissions**.
5.  Click **Grant admin consent for <tên_tenant>** để phê duyệt quyền cấp cao.

### Bước 4: Khai báo Credentials
Mở file `.env.caveman` và điền:
```ini
TEAMS_TENANT_ID=directory_tenant_id_cua_ban
TEAMS_CLIENT_ID=application_client_id_cua_ban
TEAMS_CLIENT_SECRET=client_secret_value_cua_ban
```

---

## 2. Slack Events API Integration Guide

### Bước 1: Khởi tạo Ứng dụng Slack
1.  Truy cập [Slack API Portal](https://api.slack.com/apps) $\rightarrow$ Click **Create New App** $\rightarrow$ Chọn **From scratch**.
2.  Đặt tên ứng dụng và chọn Workspace làm việc $\rightarrow$ Click **Create App**.

### Bước 2: Kích hoạt Webhook & Sự kiện (Events)
1.  Chọn **Event Subscriptions** ở menu bên trái $\rightarrow$ Bật **Enable Events** sang **On**.
2.  Tại ô **Request URL**, nhập địa chỉ webhook FastAPI của bạn (ví dụ: `https://your-domain.ngrok-free.app/webhook/chat`). Slack sẽ gửi payload test và xác thực URL tự động.
3.  Tại phần **Subscribe to bot events**, nhấp **Add Bot User Event** và chọn các sự kiện tin nhắn:
    *   `message.channels` (Tin nhắn trong kênh công khai).
    *   `message.groups` (Tin nhắn trong nhóm riêng tư).
    *   `message.im` (Tin nhắn Direct Message - phục vụ self-chat).
4.  Click **Save Changes**.

### Bước 3: Cấp quyền Scope & Lấy Secrets
1.  Chọn **OAuth & Permissions** ở menu bên trái.
2.  Kiểm tra phần **Scopes** xem đã có đủ `channels:history`, `groups:history`, `im:history`, `mpim:history` chưa.
3.  Click **Install to Workspace** ở trên cùng để cài app vào Slack Workspace của bạn. Ghi lại **Bot User OAuth Token** (bắt đầu bằng `xoxb-`).
4.  Chọn **Basic Information** ở menu bên trái $\rightarrow$ Tìm mục **App Credentials** $\rightarrow$ Copy lại **Signing Secret**.

### Bước 4: Khai báo Credentials
Mở file `.env.caveman` và điền:
```ini
SLACK_SIGNING_SECRET=slack_signing_secret_cua_ban
SLACK_BOT_TOKEN=slack_bot_oauth_token_cua_ban
```

---

## 3. Zalo OA (Official Account) Integration Guide

### Bước 1: Khởi tạo App trên Zalo Developer
1.  Truy cập [Zalo Developers](https://developers.zalo.me/) $\rightarrow$ Đăng nhập $\rightarrow$ Chọn **Thêm ứng dụng mới**.
2.  Liên kết ứng dụng với Official Account (OA) quản trị của team bạn.

### Bước 2: Cấu hình Webhook nhận tin nhắn
1.  Tại trang quản trị App Zalo, chọn mục **Webhook** $\rightarrow$ Bật **On**.
2.  Điền URL webhook FastAPI của bạn (ví dụ: `https://your-domain.ngrok-free.app/webhook/chat`).
3.  Bật đăng ký các sự kiện nhận tin nhắn thô:
    *   `user_send_text` (Người dùng gửi tin nhắn text thông thường).
    *   `user_send_text_to_oa` (Người dùng nhắn cho OA).

### Bước 3: Lấy API Credentials
1.  Chọn mục **Cài đặt** $\rightarrow$ Copy lại **Secret Key** của ứng dụng.
2.  Lấy Access Token của OA tại trang quản trị Access Token Helper để phục vụ các cuộc gọi API chủ động.

### Bước 4: Khai báo Credentials
Mở file `.env.caveman` và điền:
```ini
ZALO_SECRET_KEY=zalo_secret_key_cua_ban
ZALO_ACCESS_TOKEN=zalo_oa_access_token_cua_ban
```

---

## Origin
- **Source:** Trực tiếp từ tài liệu kỹ thuật của Slack, MS Graph, Zalo & orca-workflow
- **Commit:** document-connector-guides
- **Date:** 2026-06-01
