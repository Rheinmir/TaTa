"""ProposalStore — hàng đợi ĐỀ XUẤT task (chưa phải task).

V1.2 (HITL) + V2.4: AI ghi proposal (status='proposed') kèm confidence + nguồn;
người duyệt ở dashboard chốt → status='approved' (rồi tạo task) hoặc 'rejected'.
Đề xuất ≠ task: chưa đụng Notion cho tới khi chốt.
"""
from .base import Store

STATUS_PROPOSED = "proposed"
STATUS_APPROVED = "approved"
STATUS_REJECTED = "rejected"


class ProposalStore(Store):
    id_prefix = "prop"

    def __init__(self, client=None):
        super().__init__("tata_proposals", client)

    def add_proposal(self, tenant_id, title, description, source_ref,
                     candidate_assignees=None, confidence=0.0, reason="",
                     due=None, priority="Medium", channel=None, dedup_key=None):
        return self.insert({
            "tenant_id": tenant_id,            # thuộc user/bridge nào (scope duyệt)
            "title": title,
            "description": description,
            "source_ref": source_ref,          # link/msg id về chat gốc
            "channel": channel,
            "candidate_assignees": candidate_assignees or [],
            "confidence": confidence,
            "reason": reason,                  # vì sao AI nghĩ đây là việc
            "due": due,
            "priority": priority,
            "dedup_key": dedup_key,            # chống trùng (cùng việc nhắc nhiều lần)
            "status": STATUS_PROPOSED,
        })

    def pending_for_tenant(self, tenant_id):
        return self.list(tenant_id=tenant_id, status=STATUS_PROPOSED)

    def exists_dedup(self, tenant_id, dedup_key):
        if not dedup_key:
            return False
        return any(p.get("dedup_key") == dedup_key for p in self.list(tenant_id=tenant_id))

    def approve(self, proposal_id, assignee, description=None, due=None, priority=None, approved_by=None):
        patch = {"status": STATUS_APPROVED, "assignee": assignee, "approved_by": approved_by}
        if description is not None:
            patch["description"] = description
        if due is not None:
            patch["due"] = due
        if priority is not None:
            patch["priority"] = priority
        return self.update(proposal_id, patch)

    def reject(self, proposal_id, approved_by=None):
        return self.update(proposal_id, {"status": STATUS_REJECTED, "approved_by": approved_by})
