import logging
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TaTa.CronScanner")

class ChatHistoryScanner:
    """Cron Job quét lịch sử chat của tài khoản để tự sinh task."""
    
    def __init__(self):
        logger.info("Khởi tạo Chat History Scanner")
        
    def scan_channels(self) -> list:
        """Quét các phòng chat được cấu hình."""
        logger.info("Đang bắt đầu quét lịch sử chat...")
        time.sleep(0.5)
        # Giả lập phát hiện tin nhắn nhờ vả
        mock_detected = [
            {
                "text": "@A nhờ viết báo cáo phân tích đối thủ cạnh tranh trước thứ 6",
                "sender": "Sếp Nguyễn",
                "channel": "Slack - #general"
            }
        ]
        logger.info(f"Phát hiện {len(mock_detected)} tin nhắn giao việc tiềm năng.")
        return mock_detected
