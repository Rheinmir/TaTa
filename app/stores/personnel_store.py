"""PersonnelStore — kho nhân sự + năng lực + kênh, dùng cho AI match skill.

V2.1 + feedback: dual-store — Notion (mặt cho non-IT sửa) ĐỒNG BỘ với DB quan hệ
(Supabase/Postgres — app query nhanh, deploy server). Một interface, 2 backend.
Bao gồm cả "AI agent" như 1 nhân sự (loại='ai') có hook + system_prompt/harness.
"""
from .base import Store


class PersonnelStore(Store):
    id_prefix = "person"

    def __init__(self, client=None, notion_sync=None):
        super().__init__("tata_personnel", client)
        # notion_sync: đối tượng PersonnelNotionSync (tuỳ chọn) để đẩy/kéo Notion
        self.notion_sync = notion_sync

    def upsert_person(self, name, skills, kind="human", email=None,
                      zalo_account=None, teams_account=None,
                      ai_hook_url=None, ai_system_prompt=None, ai_harness=None,
                      active=True, person_id=None):
        """Tạo/sửa 1 nhân sự (người hoặc AI). Ghi DB rồi sync Notion (nếu có)."""
        row = {
            "name": name,
            "kind": kind,                       # human | ai
            "skills": skills or [],
            "email": email,
            "zalo_account": zalo_account,
            "teams_account": teams_account,
            "ai_hook_url": ai_hook_url,          # chỉ với kind='ai'
            "ai_system_prompt": ai_system_prompt,
            "ai_harness": ai_harness,            # tham chiếu harness nếu cắm
            "active": active,
        }
        if person_id:
            saved = self.update(person_id, row)
        else:
            saved = self.insert(row)
        if self.notion_sync and saved:
            try:
                self.notion_sync.push(saved)
            except Exception:  # noqa: BLE001 — sync Notion không được chặn ghi DB
                pass
        return saved

    def active_people(self, kind=None):
        rows = [p for p in self.list() if p.get("active")]
        if kind:
            rows = [p for p in rows if p.get("kind") == kind]
        return rows

    def match_by_skills(self, required_skills, kind=None, top=3):
        """Xếp hạng nhân sự theo số skill khớp (đơn giản, để AI prefer gợi ý).

        Trả list (person, score) giảm dần. Logic AI-prefer thật sự (phase 4) có thể
        thay bằng embedding; ở đây là baseline đếm overlap để màn duyệt có placeholder.
        """
        req = {s.lower().strip() for s in (required_skills or [])}
        scored = []
        for p in self.active_people(kind=kind):
            have = {s.lower().strip() for s in (p.get("skills") or [])}
            score = len(req & have)
            if score > 0:
                scored.append((p, score))
        scored.sort(key=lambda t: t[1], reverse=True)
        return scored[:top]
