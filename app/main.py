from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
import time

app = FastAPI(
    title="TaTa API - Team Automated Task Agent",
    description="Backend API and Orchestration Service for TaTa task manager.",
    version="1.0.0"
)

# CORS configuration for frontend dashboard
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TaskCreate(BaseModel):
    title: str
    requester: str
    assignee: Optional[str] = "Unassigned"
    deadline: Optional[str] = None
    priority: Optional[str] = "Medium"
    source: str
    status: Optional[str] = "Pending Review"

class Task(TaskCreate):
    id: str
    created_at: float
    synced_to_notion: bool = False

# In-memory mock storage for the scaffold
mock_tasks: List[Task] = [
    Task(
        id="task-101",
        title="Viết tài liệu thiết kế hệ thống TaTa",
        requester="Nguyễn Văn A",
        assignee="Trần Thị B",
        deadline="2026-06-05 17:00",
        priority="High",
        source="Slack - #general",
        status="Synced",
        created_at=time.time() - 3600,
        synced_to_notion=True
    ),
    Task(
        id="task-102",
        title="Setup database Supabase làm hàng đợi (Queue)",
        requester="Trần Thị B",
        assignee="Nguyễn Văn A",
        deadline="2026-06-03 12:00",
        priority="High",
        source="Self-chat",
        status="Pending Review",
        created_at=time.time() - 1800,
        synced_to_notion=False
    ),
    Task(
        id="task-103",
        title="Nghiên cứu API Microsoft Teams Graph để nhận tin nhắn realtime",
        requester="Phạm Văn C",
        assignee="Trần Thị B",
        deadline="2026-06-10 18:00",
        priority="Medium",
        source="MS Teams - #tech",
        status="Pending Review",
        created_at=time.time() - 600,
        synced_to_notion=False
    )
]

@app.get("/health", tags=["System"])
def health_check():
    """Endpoint kiểm tra sức khỏe hệ thống."""
    return {
        "status": "healthy",
        "service": "TaTa API",
        "timestamp": time.time(),
        "database_connected": True,
        "notion_sync_active": True
    }

@app.get("/api/tasks", response_model=List[Task], tags=["Tasks"])
def get_tasks():
    """Lấy danh sách task trong hàng đợi Supabase."""
    return mock_tasks

@app.post("/api/tasks", response_model=Task, tags=["Tasks"])
def create_task(task_in: TaskCreate):
    """Tạo mới task (kênh manual hoặc nhận từ webhook)."""
    new_task = Task(
        id=f"task-{int(time.time())}",
        title=task_in.title,
        requester=task_in.requester,
        assignee=task_in.assignee,
        deadline=task_in.deadline,
        priority=task_in.priority,
        source=task_in.source,
        status=task_in.status or "Pending Review",
        created_at=time.time(),
        synced_to_notion=False
    )
    mock_tasks.append(new_task)
    return new_task

@app.post("/api/tasks/{task_id}/sync", tags=["Tasks"])
def sync_task_to_notion(task_id: str):
    """Trigger đồng bộ thủ công task lên Notion."""
    for task in mock_tasks:
        if task.id == task_id:
            task.synced_to_notion = True
            task.status = "Synced"
            return {"status": "success", "message": f"Task {task_id} successfully synced to Notion."}
    raise HTTPException(status_code=404, detail="Task not found")

@app.post("/webhook/chat", tags=["Webhooks"])
def chat_webhook(payload: dict):
    """Webhook tiếp nhận tin nhắn chat từ Slack/Teams/Zalo để AI trích xuất."""
    # Giả lập AI trích xuất tin nhắn
    message_text = payload.get("text", "")
    sender = payload.get("sender", "Unknown")
    channel = payload.get("channel", "General Chat")
    
    # Ở phiên bản tiếp theo, AI Extraction Engine sẽ xử lý logic ở đây
    # Ví dụ: "giao việc cho B làm báo cáo trước thứ 6"
    return {
        "status": "received",
        "message": f"Message received from {sender} in {channel}.",
        "ai_processing": "Message sent to Extraction Engine queue."
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
