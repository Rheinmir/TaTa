"""NotifyService — định tuyến thông báo giao việc theo kênh người đó đăng ký.

person (từ PersonnelStore): email / zalo_account / teams_account → gửi qua kênh tương ứng.
Trả list kết quả từng kênh. AI agent (kind='ai') KHÔNG notify ở đây — đi qua hook (Phase 5).
"""
import logging
from .channels import EmailSMTPChannel, ZaloBridgeChannel, TeamsGraphChannel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TaTa.Notify.Service")


def _format(task):
    subject = f"[TaTa] Bạn được giao việc: {task.get('title')}"
    body = (
        f"Việc: {task.get('title')}\n"
        f"Mức ưu tiên: {task.get('priority','Medium')}\n"
        f"Hạn: {task.get('deadline') or 'chưa đặt'}\n"
        f"Nguồn: {task.get('source','')}\n"
        f"— Tự động từ TaTa (AI trích & giao việc)."
    )
    return subject, body


class NotifyService:
    def __init__(self, email=None, zalo=None, teams=None):
        self.email = email or EmailSMTPChannel()
        self.zalo = zalo or ZaloBridgeChannel()
        self.teams = teams or TeamsGraphChannel()

    def notify_assignment(self, task, person):
        if not person:
            return []
        if person.get("kind") == "ai":
            return [{"channel": "ai-hook", "status": "skip", "detail": "AI → Phase 5 hook"}]
        subject, body = _format(task)
        results = []
        if person.get("email"):
            results.append(self.email.send(person["email"], subject, body))
        if person.get("zalo_account"):
            results.append(self.zalo.send(person["zalo_account"], subject, body))
        if person.get("teams_account"):
            results.append(self.teams.send(person["teams_account"], subject, body))
        logger.info("Notify '%s' qua %d kênh", person.get("name"), len(results))
        return results
