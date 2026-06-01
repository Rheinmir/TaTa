import os
import json
import uuid
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TaTa.Database")

# Path to the fallback JSON database
DB_FALLBACK_FILE = "supabase_mock_db.json"

def load_env_caveman():
    """Tải cấu hình từ file .env.caveman nếu tồn tại."""
    filepath = ".env.caveman"
    if os.path.exists(filepath):
        with open(filepath, "r") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                parts = line.split("=", 1)
                if len(parts) == 2:
                    os.environ[parts[0].strip()] = parts[1].strip()

# Load env variables on startup
load_env_caveman()

class DatabaseConnector:
    """Quản lý kết nối và tác vụ lưu trữ cho TaTa (Supabase / Local JSON fallback)."""
    
    def __init__(self):
        self.supabase_url = os.environ.get("SUPABASE_URL")
        self.supabase_key = os.environ.get("SUPABASE_KEY")
        self.client = None
        
        # Thử khởi tạo Supabase Client thật
        if self.supabase_url and self.supabase_key:
            try:
                from supabase import create_client
                self.client = create_client(self.supabase_url, self.supabase_key)
                logger.info("✅ Kết nối thành công tới Supabase Client thật!")
            except Exception as e:
                logger.warning(f"⚠️ Không thể khởi tạo Supabase Client ({e}). Chuyển sang chế độ Local JSON Fallback.")
        else:
            logger.info("ℹ️ Thiếu cấu hình Supabase URL/Key. Sử dụng Local JSON Database làm vùng đệm Queue.")
            
        self._init_local_db()

    def _init_local_db(self):
        """Khởi tạo file cơ sở dữ liệu local nếu chưa tồn tại."""
        if not os.path.exists(DB_FALLBACK_FILE):
            with open(DB_FALLBACK_FILE, "w", encoding="utf-8") as f:
                json.dump([], f, ensure_ascii=False, indent=4)

    def _read_local_db(self) -> list:
        """Đọc danh sách task từ local JSON DB."""
        try:
            with open(DB_FALLBACK_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Lỗi đọc local DB: {e}")
            return []

    def _write_local_db(self, data: list):
        """Ghi danh sách task vào local JSON DB."""
        try:
            with open(DB_FALLBACK_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
        except Exception as e:
            logger.error(f"Lỗi ghi local DB: {e}")

    def insert_task(self, task_data: dict) -> dict:
        """Thêm một task mới vào hàng đợi (Queue)."""
        new_task = {
            "id": task_data.get("id") or f"task-{uuid.uuid4().hex[:8]}",
            "title": task_data.get("title"),
            "requester": task_data.get("requester", "Unknown"),
            "assignee": task_data.get("assignee", "Unassigned"),
            "deadline": task_data.get("deadline", "Không xác định"),
            "priority": task_data.get("priority", "Medium"),
            "source": task_data.get("source", "Manual"),
            "status": task_data.get("status", "Pending Review"),
            "created_at": task_data.get("created_at") or time.time(),
            "synced_to_notion": task_data.get("synced_to_notion", False)
        }

        # Nếu có Supabase thật
        if self.client:
            try:
                res = self.client.table("tasks_queue").insert(new_task).execute()
                logger.info(f"✅ Đã lưu task lên Supabase: {new_task['id']}")
                return new_task
            except Exception as e:
                logger.error(f"Lỗi insert Supabase ({e}). Ghi đè vào Local DB.")

        # Fallback ghi vào local JSON DB
        tasks = self._read_local_db()
        tasks.append(new_task)
        self._write_local_db(tasks)
        logger.info(f"📝 Đã lưu task vào Local DB (Fallback Queue): {new_task['id']}")
        return new_task

    def get_tasks(self) -> list:
        """Lấy danh sách toàn bộ task trong hàng đợi."""
        if self.client:
            try:
                res = self.client.table("tasks_queue").select("*").execute()
                return res.data
            except Exception as e:
                logger.error(f"Lỗi đọc Supabase ({e}). Sử dụng Local DB.")
        
        return self._read_local_db()

    def sync_task_to_notion(self, task_id: str) -> bool:
        """Đồng bộ task lên Notion (Cập nhật trạng thái synced trong DB)."""
        if self.client:
            try:
                self.client.table("tasks_queue").update({"synced_to_notion": True, "status": "Synced"}).eq("id", task_id).execute()
                logger.info(f"✅ Đã cập nhật trạng thái Synced lên Supabase cho task: {task_id}")
                return True
            except Exception as e:
                logger.error(f"Lỗi cập nhật Supabase ({e}). Chuyển sang Local DB.")

        tasks = self._read_local_db()
        updated = False
        for task in tasks:
            if task["id"] == task_id:
                task["synced_to_notion"] = True
                task["status"] = "Synced"
                updated = True
                break
        
        if updated:
            self._write_local_db(tasks)
            logger.info(f"📝 Đã cập nhật trạng thái Synced vào Local DB cho task: {task_id}")
            return True
        return False

db = DatabaseConnector()
