"""TaskExtractor — batch hội thoại → đề xuất task (proposal).

Lõi 'không bắt sai':
  1) prompt precision-first (chỉ việc giao rõ ràng)
  2) confidence gate: bỏ việc < ngưỡng (TATA_CONFIDENCE_MIN, mặc định 0.7)
  3) dedup: cùng việc (theo conversation + title) → 1 proposal
Ghi vào ProposalStore (status='proposed'); KHÔNG tạo task — chờ HITL.
"""
import os
import re
import logging

from app.stores import ProposalStore
from .prompt import SYSTEM, build_user_prompt
from .llm import parse_tasks

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TaTa.Extractor")

CONF_MIN = float(os.environ.get("TATA_CONFIDENCE_MIN", "0.7"))


def _slug(s):
    s = (s or "").lower().strip()
    s = re.sub(r"\s+", "-", s)
    s = re.sub(r"[^\w\-à-ỹ]", "", s, flags=re.UNICODE)
    return s[:60]


class TaskExtractor:
    def __init__(self, llm, proposal_store=None, conf_min=CONF_MIN):
        self.llm = llm
        self.proposals = proposal_store or ProposalStore()
        self.conf_min = conf_min

    def extract(self, batch):
        """batch = {tenant_id, conversation_id, channel, messages:[{sender,text,ts}]}.

        Trả dict thống kê: {created:[proposal...], dropped_low:int, dropped_dedup:int}.
        """
        tenant_id = batch["tenant_id"]
        conv = batch.get("conversation_id")
        channel = batch.get("channel")
        user_prompt = build_user_prompt(channel, batch.get("messages") or [])

        raw = self.llm.complete(SYSTEM, user_prompt)
        tasks = parse_tasks(raw)

        created, low, dedup = [], 0, 0
        for t in tasks:
            if not isinstance(t, dict):
                continue
            title = (t.get("title") or "").strip()
            if not title:
                continue
            try:
                conf = float(t.get("confidence", 0))
            except (TypeError, ValueError):
                conf = 0.0
            if conf < self.conf_min:                 # confidence gate
                low += 1
                continue
            dkey = f"{conv}:{_slug(title)}"
            if self.proposals.exists_dedup(tenant_id, dkey):  # dedup
                dedup += 1
                continue
            hint = t.get("assignee_hint")
            p = self.proposals.add_proposal(
                tenant_id=tenant_id,
                title=title,
                description=(t.get("description") or "").strip(),
                source_ref=f"{channel}:{conv}",
                candidate_assignees=[hint] if hint else [],
                confidence=conf,
                reason=t.get("reason") or t.get("source_quote") or "",
                due=t.get("due"),
                priority=t.get("priority") or "Medium",
                channel=channel,
                dedup_key=dkey,
            )
            created.append(p)

        logger.info("Extract conv=%s: %d việc → %d tạo, %d loại(thấp), %d loại(trùng)",
                    conv, len(tasks), len(created), low, dedup)
        return {"created": created, "dropped_low": low, "dropped_dedup": dedup}
