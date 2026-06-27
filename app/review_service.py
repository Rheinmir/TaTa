"""ReviewService — logic màn duyệt HITL (Phase 3).

list_pending(tenant)            → đề xuất 'proposed' theo tenant-scope
suggest_assignees(proposal)     → AI prefer: xếp hạng nhân sự theo skill khớp text việc
approve(id, assignee, ...)      → tạo task thật (DatabaseConnector) + proposal='approved'
reject(id)                      → proposal='rejected'

Người chốt mới tạo task (V1.2 HITL). Notify + AI-hook là Phase 4/5.
"""
import logging

from app.stores import ProposalStore, PersonnelStore

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TaTa.Review")


class ReviewService:
    def __init__(self, proposal_store=None, personnel_store=None, db=None,
                 notify_service=None, notion_sync=None, ai_hook=None):
        self.proposals = proposal_store or ProposalStore()
        self.personnel = personnel_store or PersonnelStore()
        # db = DatabaseConnector (tạo task). Lazy để tránh vòng import lúc test.
        if db is None:
            from app.database import DatabaseConnector
            db = DatabaseConnector()
        self.db = db
        # Phase 4: notify + Notion (injectable; mặc định real-with-dryrun)
        if notify_service is None:
            from app.notify import NotifyService
            notify_service = NotifyService()
        self.notify = notify_service
        if notion_sync is None:
            from app.notion_sync import TaskNotionSync
            notion_sync = TaskNotionSync()
        self.notion = notion_sync
        if ai_hook is None:
            from app.hooks import AIHook
            ai_hook = AIHook()
        self.ai_hook = ai_hook

    def _find_person(self, name):
        if not name:
            return None
        n = name.strip().lower()
        for p in self.personnel.active_people():
            if (p.get("name") or "").strip().lower() == n:
                return p
        return None

    def list_pending(self, tenant_id):
        return self.proposals.pending_for_tenant(tenant_id)

    def suggest_assignees(self, proposal, top=3):
        """AI prefer: nhân sự có skill xuất hiện trong title+description; ưu tiên hint.

        Trả list {id,name,kind,score,reason}. Đây là placeholder cho ô assignee
        (người duyệt ấn Tab/nút để lấy, hoặc tự nhập người khác).
        """
        text = f"{proposal.get('title','')} {proposal.get('description','')}".lower()
        hints = {h.lower().strip() for h in (proposal.get("candidate_assignees") or []) if h}
        out = []
        for p in self.personnel.active_people():
            skills = [s for s in (p.get("skills") or []) if s and s.lower() in text]
            score = len(skills)
            if (p.get("name") or "").lower() in hints:
                score += 2  # boost nếu chat đã nhắc tên người này
            if score > 0:
                out.append({
                    "id": p.get("id"), "name": p.get("name"), "kind": p.get("kind"),
                    "score": score,
                    "reason": ("khớp skill: " + ", ".join(skills)) if skills else "được nhắc trong chat",
                })
        out.sort(key=lambda x: x["score"], reverse=True)
        return out[:top]

    def approve(self, proposal_id, assignee, approved_by=None,
                description=None, due=None, priority=None):
        """Chốt: tạo task thật + đánh dấu proposal approved. Trả {task, proposal}."""
        prop = self.proposals.get(proposal_id)
        if not prop:
            raise ValueError(f"Không thấy proposal {proposal_id}")
        if prop.get("status") != "proposed":
            raise ValueError(f"Proposal {proposal_id} không ở trạng thái proposed")
        task = self.db.insert_task({
            "title": prop.get("title"),
            "assignee": assignee,
            "deadline": due if due is not None else prop.get("due"),
            "priority": priority or prop.get("priority") or "Medium",
            "source": f"AI-extract:{prop.get('source_ref')}",
            "status": "Assigned",
        })
        self.proposals.approve(proposal_id, assignee=assignee, description=description,
                               due=due, priority=priority, approved_by=approved_by)
        # Phase 4: đẩy Notion + báo người được giao theo kênh đã đăng ký
        person = self._find_person(assignee)
        notion_res = self.notion.push(task)
        notify_res = self.notify.notify_assignment(task, person)
        # Phase 5: assignee là AI → fire webhook hook (thay vì notify người)
        hook_res = None
        if person and person.get("kind") == "ai":
            hook_res = self.ai_hook.fire(task, person)
        logger.info("Chốt proposal %s → task %s cho %s (%d kênh, hook=%s)",
                    proposal_id, task.get("id"), assignee, len(notify_res),
                    hook_res.get("status") if hook_res else "-")
        return {"task": task, "proposal": self.proposals.get(proposal_id),
                "notion": notion_res, "notify": notify_res, "ai_hook": hook_res}

    def reject(self, proposal_id, approved_by=None):
        return self.proposals.reject(proposal_id, approved_by=approved_by)
