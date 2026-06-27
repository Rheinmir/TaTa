"""AIHook — fire webhook giao task cho AI agent.

Payload gồm: task, system_prompt (từ profile AI, có thể override), harness ref, assignee,
callback_url (để AI POST kết quả về). Có ai_hook_url → POST thật; không → dry-run.
sender injectable để test (callable(url, payload, headers) -> dict).
"""
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TaTa.Hook.AI")


class AIHook:
    def __init__(self, sender=None, callback_base=None):
        self.sender = sender              # callable(url, payload, headers) -> dict (None → requests)
        self.callback_base = callback_base or os.environ.get("TATA_CALLBACK_BASE")

    def _payload(self, task, person, system_prompt_override=None):
        cb = (f"{self.callback_base.rstrip('/')}/api/hooks/ai-result/{task.get('id')}"
              if self.callback_base else None)
        return {
            "task": {
                "id": task.get("id"),
                "title": task.get("title"),
                "priority": task.get("priority"),
                "due": task.get("deadline"),
                "source": task.get("source"),
            },
            "assignee": person.get("name"),
            "system_prompt": system_prompt_override or person.get("ai_system_prompt"),
            "harness": person.get("ai_harness"),
            "callback_url": cb,
        }

    def fire(self, task, person, system_prompt_override=None):
        if not person or person.get("kind") != "ai":
            return {"status": "skip", "detail": "assignee không phải AI"}
        url = person.get("ai_hook_url")
        payload = self._payload(task, person, system_prompt_override)
        if not url:
            logger.info("…(dry-run AI hook) task '%s' → AI '%s' (chưa có ai_hook_url)",
                        task.get("title"), person.get("name"))
            return {"status": "dry-run", "payload": payload}
        headers = {"Content-Type": "application/json"}
        try:
            if self.sender:
                self.sender(url, payload, headers)
            else:
                import requests
                requests.post(url, json=payload, headers=headers, timeout=20).raise_for_status()
            logger.info("Fired AI hook → %s cho task '%s'", url, task.get("title"))
            return {"status": "fired", "url": url, "payload": payload}
        except Exception as e:  # noqa: BLE001
            logger.warning("AI hook lỗi: %s", e)
            return {"status": "error", "detail": str(e), "payload": payload}
