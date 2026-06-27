"""PersonnelNotionSync — đồng bộ kho nhân sự DB ↔ Notion (dual-store).

Notion là mặt cho non-IT sửa; DB quan hệ là nguồn app query. Bản này là interface
+ impl mock (giống app/sync.py:SyncEngine hiện tại). Cắm Notion API thật ở Phase 4
bằng cách điền NOTION_TOKEN + NOTION_PERSONNEL_DB_ID và hiện thực push()/pull().
"""
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TaTa.PersonnelSync")


class PersonnelNotionSync:
    def __init__(self):
        self.token = os.environ.get("NOTION_TOKEN")
        self.db_id = os.environ.get("NOTION_PERSONNEL_DB_ID")
        self.enabled = bool(self.token and self.db_id)
        if not self.enabled:
            logger.info("ℹ️ PersonnelSync: chưa cấu hình Notion (NOTION_TOKEN/DB_ID) → mock.")

    def push(self, person):
        """Đẩy 1 nhân sự lên Notion (upsert theo id)."""
        if not self.enabled:
            logger.info("…(mock) push nhân sự '%s' lên Notion.", person.get("name"))
            return True
        # TODO Phase 4: gọi Notion API thật (pages.create/update vào db_id)
        logger.info("push nhân sự '%s' → Notion DB %s.", person.get("name"), self.db_id)
        return True

    def pull(self):
        """Kéo danh sách nhân sự từ Notion về (để đồng bộ vào DB)."""
        if not self.enabled:
            logger.info("…(mock) pull nhân sự từ Notion (rỗng).")
            return []
        # TODO Phase 4: query Notion db_id → list dict chuẩn hoá theo schema personnel
        return []
