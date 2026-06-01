import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TaTa.SyncEngine")

class SyncEngine:
    """Động cơ đồng bộ hóa dữ liệu từ Supabase DB lên Notion API."""
    
    def __init__(self):
        logger.info("Khởi tạo Sync Engine kết nối Notion API")
        
    def sync_to_notion(self, task: dict) -> bool:
        """Đẩy dữ liệu theo lô hoặc đơn lẻ lên Notion."""
        logger.info(f"Đang đồng bộ task {task.get('id')} lên Notion...")
        # Giả lập đồng bộ thành công
        logger.info(f"Đã đồng bộ thành công: '{task.get('title')}'")
        return True
