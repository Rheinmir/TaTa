"""TaTa hooks — Phase 5: giao task cho AI agent qua webhook.

Khi assignee là nhân sự kind='ai': fire 1 HTTP POST tới ai_hook_url với task payload,
cho phép inject system_prompt và tham chiếu harness (V3b.4). AI tự chạy rồi (tuỳ chọn)
POST kết quả về callback_url.
"""
from .ai_hook import AIHook

__all__ = ["AIHook"]
