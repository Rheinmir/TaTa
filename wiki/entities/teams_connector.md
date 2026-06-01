# Teams Connector Entity
**Type:** entity
**Tags:** ms-teams, ms-graph-api, connector, auth

Đầu nối kỹ thuật tích hợp với Microsoft Teams thông qua Microsoft Graph API và thư viện MSAL Python.

## Notes
- **Cơ chế xác thực:** Sử dụng Client Credentials Grant Flow (OAuth 2.0) thông qua Azure Active Directory để lấy Graph Access Token.
- **API Endpoints:**
  - **Lấy Token:** `https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token`
  - **Lấy tin nhắn Chat:** `https://graph.microsoft.com/v1.0/chats/{chat_id}/messages`
  - **Lấy tin nhắn Channel:** `https://graph.microsoft.com/v1.0/teams/{team_id}/channels/{channel_id}/messages`
- **Tích hợp trong TaTa:** `TeamsConnector` định kỳ quét (cào) các tin nhắn chưa xử lý trong phòng chat được chỉ định, lưu tin nhắn thô thu được vào hàng đợi thô `RAW_CLAIMED_MESSAGES` qua API `/api/chat/raw`.

## Origin
- **Source:** app/chat_connector.py
- **Commit:** implement-chat-connectors
- **Date:** 2026-06-01
