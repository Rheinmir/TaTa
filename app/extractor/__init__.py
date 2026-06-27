"""TaTa extractor — Phase 2: AI trích 'việc giao rõ ràng' từ batch hội thoại.

Lõi 'không bắt sai': prompt precision-first + confidence gate + dedup. LLM nằm
sau interface (FakeLLM để test, AzureLiteLLMClient để chạy thật qua Azure/LiteLLM).
Đầu ra: ghi proposal (status='proposed') cho HITL duyệt — KHÔNG tạo task thẳng.
"""
from .llm import LLMClient, FakeLLM, AzureLiteLLMClient
from .extractor import TaskExtractor

__all__ = ["LLMClient", "FakeLLM", "AzureLiteLLMClient", "TaskExtractor"]
