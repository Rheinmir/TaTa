import time
import logging
import re
from app.database import db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TaTa.CronScanner")

# Mock chat history dataset to scan
MOCK_CHAT_HISTORY = [
    {
        "text": "@Bình làm giúp tôi báo cáo doanh thu tuần trước thứ Sáu nhé.",
        "sender": "Sếp Hoàng",
        "channel": "Slack - #general",
        "timestamp": time.time() - 3600
    },
    {
        "text": "FYI: Hôm nay trời đẹp quá, tối đi nhậu không cả nhà?",
        "sender": "Nguyễn Văn Nam",
        "channel": "Zalo - Ăn Chơi",
        "timestamp": time.time() - 3000
    },
    {
        "text": "Cần gấp: Anh An cấu hình cổng webhook bảo mật trước 12:00 ngày mai nha.",
        "sender": "Lê Thị Thu",
        "channel": "MS Teams - #security",
        "timestamp": time.time() - 2400
    },
    {
        "text": "Note lại: Tài liệu kỹ thuật dự án để ở đây nha https://docs.tata.io",
        "sender": "Trần Tuấn",
        "channel": "Slack - #tech",
        "timestamp": time.time() - 1200
    }
]

class ChatHistoryScanner:
    """Cron Job tự động quét lịch sử chat của tài khoản và tự sinh task qua phân tích AI."""
    
    def __init__(self):
        logger.info("🤖 Khởi chạy bộ quét tự động Chat History Scanner...")

    def parse_message_heuristics(self, message: dict) -> dict:
        """Bộ phân tích cú pháp dự phòng (Heuristic Parsing Engine).
        
        Tự động trích xuất cấu trúc task khi thiếu LLM API Key.
        """
        text = message.get("text", "")
        sender = message.get("sender", "Unknown")
        channel = message.get("channel", "Unknown")
        
        # Nhận diện các tin nhắn chứa từ khóa giao việc
        task_keywords = ["làm giúp", "cần gấp", "nhờ", "yêu cầu", "deadline", "trước", "phải xong"]
        is_task = any(kw in text.lower() for kw in task_keywords)
        
        if not is_task:
            return None
            
        logger.info(f"✨ Phát hiện tin nhắn giao việc tiềm năng từ {sender}: '{text}'")
        
        # Trích xuất người nhận (Assignee) dạng @Name
        assignee_match = re.search(r"@([^\s]+)", text)
        assignee = assignee_match.group(1) if assignee_match else "Unassigned"
        
        # Trích xuất deadline (Ví dụ: trước thứ sáu, trước 12:00...)
        deadline_match = re.search(r"(trước\s+[^\s,]+(\s+[^\s,]+){0,3})", text, re.IGNORECASE)
        deadline = deadline_match.group(1) if deadline_match else "Không xác định"
        
        # Đánh giá mức độ ưu tiên
        priority = "Medium"
        if "cần gấp" in text.lower() or "khẩn cấp" in text.lower() or "ngay" in text.lower():
            priority = "High"
        elif "fyi" in text.lower() or "note" in text.lower():
            priority = "Low"
            
        # Làm sạch nội dung task
        clean_title = text.replace(f"@{assignee}", "").strip()
        
        return {
            "title": clean_title,
            "requester": sender,
            "assignee": assignee,
            "deadline": deadline,
            "priority": priority,
            "source": channel,
            "status": "Pending Review",
            "created_at": time.time()
        }

    def run_cron_scan(self) -> list:
        """Thực hiện quét toàn bộ lịch sử chat và tự sinh task đẩy vào DB trung gian."""
        logger.info("🔍 Đang quét lịch sử chat của toàn bộ tài khoản...")
        new_tasks = []
        
        # Đọc dữ liệu chat hiện tại trong db để tránh trùng lặp
        existing_titles = [t["title"] for t in db.get_tasks()]
        
        for msg in MOCK_CHAT_HISTORY:
            parsed_task = self.parse_message_heuristics(msg)
            if parsed_task:
                # Tránh trùng lặp task đã tồn tại
                if parsed_task["title"] in existing_titles:
                    logger.info(f"⏭️ Task '{parsed_task['title']}' đã tồn tại trong hàng đợi. Bỏ qua.")
                    continue
                    
                # Thêm vào cơ sở dữ liệu
                saved_task = db.insert_task(parsed_task)
                new_tasks.append(saved_task)
                
        logger.info(f"🎉 Quét hoàn tất! Đã trích xuất và đẩy thành công {len(new_tasks)} task mới vào Supabase Queue.")
        return new_tasks

# Khởi tạo toàn cục scanner
scanner = ChatHistoryScanner()

if __name__ == "__main__":
    scanner.run_cron_scan()
