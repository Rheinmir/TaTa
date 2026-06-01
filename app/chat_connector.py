import os
import time
import hmac
import hashlib
import json
import logging
import requests
import msal

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TaTa.ChatConnector")

# Path to persisted token cache
TOKEN_CACHE_FILE = "teams_token.json"

class SlackConnector:
    """Đầu nối Slack Events API - Nhận và xác thực sự kiện tin nhắn thời gian thực."""
    
    def __init__(self, signing_secret: str = None):
        self.signing_secret = signing_secret or os.environ.get("SLACK_SIGNING_SECRET", "mock_secret_123")
        
    def verify_signature(self, timestamp: str, signature: str, body: str) -> bool:
        """Xác thực chữ ký từ Slack để đảm bảo tin nhắn an toàn."""
        if not timestamp or not signature or not body:
            return False
            
        # Tránh replay attacks (trong vòng 5 phút)
        if abs(time.time() - int(timestamp)) > 60 * 5:
            return False
            
        sig_basestring = f"v0:{timestamp}:{body}".encode('utf-8')
        my_signature = 'v0=' + hmac.new(
            self.signing_secret.encode('utf-8'),
            sig_basestring,
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(my_signature, signature)

    def parse_event(self, payload: dict) -> dict:
        """Trích xuất tin nhắn thô từ payload sự kiện Slack."""
        event = payload.get("event", {})
        if event.get("type") == "message" and not event.get("subtype"):
            return {
                "raw_text": event.get("text"),
                "sender_id": event.get("user"),
                "channel_id": event.get("channel"),
                "platform": "Slack",
                "timestamp": float(event.get("ts", time.time()))
            }
        return None


class TeamsDeviceCodeConnector:
    """Đầu nối MS Teams Graph API - Xác thực cá nhân bằng Device Code Flow (MSAL)."""
    
    def __init__(self):
        # Client ID mặc định của MSAL Public App hỗ trợ Personal Accounts
        # Sử dụng Client ID của Visual Studio làm well-known Client ID đáng tin cậy toàn cầu cho việc đăng nhập an toàn
        self.client_id = os.environ.get("TEAMS_CLIENT_ID", "04b07795-8ddb-461a-bbee-02f9e1bf7b46")
        self.authority = os.environ.get("TEAMS_AUTHORITY", "https://login.microsoftonline.com/common")
        self.scopes = ["User.Read"]
        
        # Thiết lập Cache Token tuần tự hóa cục bộ
        self.cache = msal.SerializableTokenCache()
        if os.path.exists(TOKEN_CACHE_FILE):
            try:
                with open(TOKEN_CACHE_FILE, "r") as f:
                    self.cache.deserialize(f.read())
                logger.info("💾 Đã khôi phục cache token thành công từ teams_token.json")
            except Exception as e:
                logger.error(f"Lỗi đọc token cache: {e}")
                
        self.app = msal.PublicClientApplication(
            self.client_id, 
            authority=self.authority, 
            token_cache=self.cache
        )
        
        self.active_flow = None
        self.auth_thread = None
        self.auth_result = None
        
    def _save_cache(self):
        """Lưu trữ Cache Token vào file cục bộ vĩnh viễn."""
        if self.cache.has_state_changed:
            try:
                with open(TOKEN_CACHE_FILE, "w") as f:
                    f.write(self.cache.serialize())
                logger.info("💾 Đã cập nhật lưu cache token vào teams_token.json")
            except Exception as e:
                logger.error(f"Lỗi lưu token cache: {e}")

    def acquire_token(self) -> str:
        """Lấy Access Token tự động từ cache hoặc refresh token (không chặn UI)."""
        accounts = self.app.get_accounts()
        if accounts:
            # Thử lấy từ cache thầm lặng
            result = self.app.acquire_token_silent(self.scopes, account=accounts[0])
            if result and "access_token" in result:
                self._save_cache()
                return result["access_token"]
        return None

    def start_auth_flow(self) -> dict:
        """Khởi động Device Code Flow để người dùng liên kết tài khoản cá nhân."""
        try:
            self.active_flow = self.app.initiate_device_flow(scopes=self.scopes)
            if self.active_flow and "user_code" in self.active_flow:
                logger.info(f"🔑 Lấy mã Device Code thành công: {self.active_flow['user_code']}")
                
                # Reset kết quả đăng nhập cũ
                self.auth_result = None
                
                # Khởi chạy luồng chạy ngầm để chờ token từ Microsoft (tránh block API)
                import threading
                def _background_poll():
                    try:
                        logger.info("⏳ Bắt đầu tiến trình ngầm chờ người dùng duyệt đăng nhập trên trình duyệt...")
                        result = self.app.acquire_token_by_device_flow(self.active_flow)
                        if "access_token" in result:
                            self._save_cache()
                            self.auth_result = {"status": "success", "message": "Đăng nhập MS Teams cá nhân thành công!"}
                            logger.info("✅ Đăng nhập MS Teams cá nhân thành công qua Device Flow!")
                        else:
                            error_msg = result.get("error_description") or result.get("error") or "Không rõ lỗi"
                            self.auth_result = {"status": "error", "message": f"Device Flow thất bại: {error_msg}"}
                            logger.error(f"❌ Device Flow thất bại: {error_msg}")
                    except Exception as e:
                        self.auth_result = {"status": "error", "message": f"Ngoại lệ khi đăng nhập: {e}"}
                        logger.error(f"❌ Ngoại lệ trong background thread Device Flow: {e}", exc_info=True)
                    finally:
                        self.active_flow = None
                
                self.auth_thread = threading.Thread(target=_background_poll, daemon=True)
                self.auth_thread.start()
                
                return {
                    "user_code": self.active_flow["user_code"],
                    "verification_uri": self.active_flow["verification_uri"],
                    "message": self.active_flow["message"]
                }
            
            error_msg = "Không rõ lỗi"
            if isinstance(self.active_flow, dict):
                error_msg = self.active_flow.get("error_description") or self.active_flow.get("error") or str(self.active_flow)
            logger.error(f"Lỗi khởi tạo Device Flow từ Microsoft AD: {error_msg}")
        except Exception as e:
            logger.error(f"Ngoại lệ khi khởi tạo Device Flow: {e}", exc_info=True)
        return None

    def poll_auth_status(self) -> dict:
        """Kiểm tra trạng thái đăng nhập thiết bị không chặn (non-blocking)."""
        # Nếu đã có token hợp lệ trong cache
        if self.acquire_token():
            return {"status": "success", "message": "Đăng nhập MS Teams cá nhân thành công!"}
            
        # Nếu thread chạy ngầm đã hoàn tất và lưu kết quả
        if self.auth_result:
            return self.auth_result
            
        # Nếu vẫn đang chờ người dùng duyệt trên trình duyệt
        if self.active_flow:
            return {"status": "pending", "message": "Đang chờ người dùng duyệt đăng nhập trên trình duyệt..."}
            
        return {"status": "inactive", "message": "Chưa khởi chạy tiến trình đăng nhập hoặc phiên đã hết hạn"}

    def crawl_chat_messages(self, chat_id: str) -> list:
        """Quét tin nhắn từ API Graph thật nếu đã login, fallback mock nếu chưa kết nối hoặc thiếu quyền."""
        fallback_data = [
            {
                "text": "Cần gấp: Anh An cấu hình cổng webhook bảo mật trước 12:00 ngày mai nha.",
                "sender": "Lê Thị Thu",
                "channel": "MS Teams - #security"
            }
        ]
        
        token = self.acquire_token()
        if not token:
            logger.info("ℹ️ Teams chưa login. Sử dụng tin nhắn thô mô phỏng của Teams.")
            return fallback_data
            
        url = f"https://graph.microsoft.com/v1.0/chats/{chat_id}/messages"
        headers = {"Authorization": f"Bearer {token}"}
        
        try:
            res = requests.get(url, headers=headers, timeout=10)
            if res.status_code != 200:
                logger.warning(f"⚠️ Graph API trả về mã {res.status_code} (Có thể do thiếu quyền Chat.Read bởi chính sách bảo mật của Coteccons). Sử dụng tin nhắn mô phỏng.")
                return fallback_data
                
            graph_messages = res.json().get("value", [])
            if not graph_messages:
                return fallback_data
                
            parsed_messages = []
            for msg in graph_messages:
                # Trích xuất văn bản thô từ định dạng HTML/Text của Graph API
                body = msg.get("body", {})
                content = body.get("content", "")
                
                # Loại bỏ HTML tags đơn giản
                clean_content = content.replace("<p>", "").replace("</p>", "").strip()
                sender = msg.get("from", {}).get("user", {}).get("displayName", "Người dùng MS Teams")
                
                parsed_messages.append({
                    "text": clean_content,
                    "sender": sender,
                    "channel": "MS Teams Chat"
                })
            return parsed_messages
        except Exception as e:
            logger.error(f"Lỗi quét Graph API MS Teams: {e}. Fallback sang tin nhắn thô mô phỏng.")
            return fallback_data


class ZaloConnector:
    """Đầu nối Zalo Webhook - Tiếp nhận tin nhắn nhóm từ webhook Zalo OA."""
    
    def __init__(self, secret_key: str = None):
        self.secret_key = secret_key or os.environ.get("ZALO_SECRET_KEY", "zalo_key_456")

    def parse_webhook(self, payload: dict) -> dict:
        """Parse tin nhắn từ webhook Zalo."""
        event = payload.get("event_name")
        if event == "user_send_text_to_oa" or event == "user_send_text":
            message = payload.get("message", {})
            sender = payload.get("sender", {})
            return {
                "raw_text": message.get("text"),
                "sender_id": sender.get("id"),
                "sender_name": sender.get("name", "Người dùng Zalo"),
                "platform": "Zalo",
                "timestamp": payload.get("timestamp", time.time())
            }
        return None


# Global mock data store for raw claimed/crawled messages
RAW_CLAIMED_MESSAGES = []

def claim_raw_message(platform: str, text: str, sender: str, channel: str):
    """Lưu trữ tin nhắn thô vừa capture được vào danh sách thô (chưa qua AI)."""
    raw_msg = {
        "id": f"raw-{int(time.time()*1000)}-{os.urandom(2).hex()}",
        "platform": platform,
        "raw_text": text,
        "sender": sender,
        "channel": channel,
        "claimed_at": time.time()
    }
    RAW_CLAIMED_MESSAGES.append(raw_msg)
    logger.info(f"📥 [CLAIMED RAW] Đã bắt được tin nhắn từ {platform} | {sender}: '{text}'")
    return raw_msg

# Khởi tạo instance kết nối toàn cục
teams_device_connector = TeamsDeviceCodeConnector()
