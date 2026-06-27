"""TenantStore — đa người dùng (multi-tenant). Mỗi user gắn 1 bridge riêng.

Quyết định phỏng vấn V3b.3: "cho tạo nhiều user mỗi người 1 bridge riêng" →
mỗi user chỉ thấy/duyệt đề xuất từ bridge của mình (review_scope).
"""
from .base import Store


class TenantStore(Store):
    id_prefix = "user"

    def __init__(self, client=None):
        super().__init__("tata_users", client)

    def create_user(self, name, bridge_id, email=None, channels=None, role="reviewer"):
        return self.insert({
            "name": name,
            "bridge_id": bridge_id,          # zca-bridge của user này
            "email": email,
            "channels": channels or [],       # kênh user sở hữu
            "role": role,                     # reviewer | admin
            "active": True,
        })

    def by_bridge(self, bridge_id):
        rows = self.list(bridge_id=bridge_id)
        return rows[0] if rows else None
