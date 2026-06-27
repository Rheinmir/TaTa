"""TaTa stores — tầng lưu trữ trừu tượng hoá (adapter) cho AI trích & giao việc.

Mỗi store có 1 interface chung, 2 backend: Supabase (nếu có SUPABASE_URL/KEY)
hoặc local-JSON fallback (dev/offline). Đổi DB khi deploy server chỉ cần thay
backend trong base.Store — logic phía trên không đổi. Cùng triết lý với
app/database.py:DatabaseConnector (đã có sẵn).
"""
from .base import Store
from .tenant_store import TenantStore
from .personnel_store import PersonnelStore
from .proposal_store import ProposalStore

__all__ = ["Store", "TenantStore", "PersonnelStore", "ProposalStore"]
