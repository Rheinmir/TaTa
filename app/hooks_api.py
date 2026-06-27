"""Hooks API — callback cho AI agent POST kết quả về sau khi làm xong task (Phase 5).

POST /api/hooks/ai-result/{task_id}  body {status, result}
MVP: ghi log + nhận; cập nhật task chi tiết để mở rộng sau.
"""
import logging
from typing import Optional
from fastapi import APIRouter
from pydantic import BaseModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TaTa.HooksAPI")

router = APIRouter(prefix="/api/hooks", tags=["AI Hooks"])


class AIResultIn(BaseModel):
    status: Optional[str] = "done"
    result: Optional[str] = None


@router.post("/ai-result/{task_id}")
def ai_result(task_id: str, body: AIResultIn):
    logger.info("AI hook callback: task=%s status=%s result=%s",
                task_id, body.status, (body.result or "")[:120])
    return {"ok": True, "task_id": task_id, "status": body.status}
