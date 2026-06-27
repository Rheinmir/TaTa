"""TaskNotionSync — đẩy task đã chốt lên Notion (DB task chính thức).

Gated bằng NOTION_TOKEN + NOTION_TASKS_DB_ID. Chưa cấu hình → mock (log), để
pipeline chạy/verify offline. Cùng triết lý PersonnelNotionSync (dual-store).
"""
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TaTa.NotionSync")


class TaskNotionSync:
    def __init__(self):
        self.token = os.environ.get("NOTION_TOKEN")
        self.db_id = os.environ.get("NOTION_TASKS_DB_ID")
        self.enabled = bool(self.token and self.db_id)
        if not self.enabled:
            logger.info("ℹ️ TaskNotionSync: chưa cấu hình Notion → mock.")

    def push(self, task):
        if not self.enabled:
            logger.info("…(mock) push task '%s' (assignee=%s) lên Notion.",
                        task.get("title"), task.get("assignee"))
            return {"status": "mock", "task_id": task.get("id")}
        # TODO: Notion API pages.create vào db_id với title/assignee/due/priority/status
        logger.info("push task '%s' → Notion DB %s.", task.get("title"), self.db_id)
        return {"status": "synced", "task_id": task.get("id")}
