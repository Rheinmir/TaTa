from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
import time
from app.database import db
from app.cron_scanner import scanner
from app.chat_connector import claim_raw_message, RAW_CLAIMED_MESSAGES, SlackConnector, ZaloConnector, teams_device_connector

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

class RawMessagePush(BaseModel):
    platform: str
    raw_text: str
    sender: str
    channel: str

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

# --- CHAT CONNECTOR ENDPOINTS (Luồng Claim Dữ liệu Thô) ---

@app.get("/api/chat/raw", tags=["Chat Connection"])
def get_raw_messages():
    """Chiếu ra toàn bộ dữ liệu tin nhắn thô vừa crawl/nhận được (Chưa qua AI xử lý)."""
    return RAW_CLAIMED_MESSAGES

@app.post("/api/chat/claim-mock", tags=["Chat Connection"])
def trigger_mock_claims():
    """Mô phỏng đầu nối kết nối lấy dữ liệu thô (Crawl/Receive) từ các kênh chat."""
    # Lấy tin nhắn MS Teams thật hoặc mock từ Teams Connector
    teams_msgs = teams_device_connector.crawl_chat_messages("mock_chat_id")
    
    mock_data = [
        ("Slack", "@Bình làm giúp tôi báo cáo doanh thu tuần trước thứ Sáu nhé.", "Sếp Hoàng", "Slack - #general"),
        ("Zalo", "Ngày mai 9:00 có họp tiến độ nha cả nhà, đừng đi trễ.", "Trần Tuấn (Zalo)", "Zalo Group"),
        ("Self-chat", "Nhắc nhở bản thân: Tìm hiểu cách sử dụng Neo4j Graph DB.", "Tôi (Self)", "Self-chat window")
    ]
    
    # Ghép tin nhắn từ Teams Connector vào
    for tm in teams_msgs:
        mock_data.append(("MS Teams", tm["text"], tm["sender"], tm.get("channel", "MS Teams Chat")))
    
    new_claims = []
    # Chỉ add những tin nhắn chưa trùng text trong danh sách thô
    existing_texts = [m["raw_text"] for m in RAW_CLAIMED_MESSAGES]
    
    for platform, text, sender, channel in mock_data:
        if text not in existing_texts:
            msg = claim_raw_message(platform, text, sender, channel)
            new_claims.append(msg)
            
    return {
        "status": "success",
        "message": f"Kết nối thành công! Đã bắt được {len(new_claims)} tin nhắn thô.",
        "claimed_messages": new_claims
    }

@app.post("/api/chat/push-raw", tags=["Chat Connection"])
def push_raw_message(payload: RawMessagePush):
    """API tiếp nhận tin nhắn thô được đẩy từ các bot cào tự động (Automated RPA/Extension)."""
    existing_texts = [m["raw_text"] for m in RAW_CLAIMED_MESSAGES]
    if payload.raw_text not in existing_texts:
        msg = claim_raw_message(payload.platform, payload.raw_text, payload.sender, payload.channel)
        return {
            "status": "success",
            "message": "Đã đẩy tin nhắn thô vào hàng đợi TaTa thành công!",
            "message_details": msg
        }
    return {
        "status": "ignored",
        "message": "Tin nhắn này đã tồn tại trong danh sách thô."
    }

# --- MS TEAMS DEVICE CODE FLOW ENDPOINTS ---

@app.post("/api/chat/teams/auth-start", tags=["MS Teams Auth"])
def teams_auth_start():
    """Bắt đầu luồng xác thực Device Code cho Teams cá nhân."""
    flow_details = teams_device_connector.start_auth_flow()
    if flow_details:
        return flow_details
    raise HTTPException(status_code=500, detail="Không thể khởi động luồng đăng nhập từ Microsoft")

@app.get("/api/chat/teams/auth-status", tags=["MS Teams Auth"])
def teams_auth_status():
    """Kiểm tra trạng thái đăng nhập thiết bị."""
    status = teams_device_connector.poll_auth_status()
    return status

@app.post("/api/chat/process-claimed/{msg_id}", tags=["Chat Connection"])
def process_claimed_message(msg_id: str):
    """Lấy tin nhắn thô đã claim, chuyển cho AI Extraction Engine để trích xuất thành task."""
    target_msg = None
    for msg in RAW_CLAIMED_MESSAGES:
        if msg["id"] == msg_id:
            target_msg = msg
            break
            
    if not target_msg:
        raise HTTPException(status_code=404, detail="Không tìm thấy tin nhắn thô")
        
    # Gửi qua parser heuristic (Mô phỏng AI Engine)
    parsed = scanner.parse_message_heuristics({
        "text": target_msg["raw_text"],
        "sender": target_msg["sender"],
        "channel": target_msg["channel"]
    })
    
    if not parsed:
        # Nếu tin nhắn chỉ là trò chuyện thường
        return {
            "status": "filtered",
            "message": "AI nhận diện tin nhắn này không chứa nội dung giao việc (Note/FYI). Bỏ qua không lưu DB."
        }
        
    # Lưu vào database hàng đợi trung gian
    saved_task = db.insert_task(parsed)
    
    # Xóa khỏi danh sách tin nhắn thô sau khi đã trích xuất xong
    RAW_CLAIMED_MESSAGES.remove(target_msg)
    
    return {
        "status": "extracted",
        "message": "AI đã trích xuất thành công và đẩy vào Supabase Database Queue!",
        "task": saved_task
    }

# --- TASK MANAGEMENT ENDPOINTS ---

@app.get("/api/tasks", response_model=List[Task], tags=["Tasks"])
def get_tasks():
    """Lấy danh sách task từ Supabase (hoặc Local JSON Queue)."""
    return db.get_tasks()

@app.post("/api/tasks", response_model=Task, tags=["Tasks"])
def create_task(task_in: TaskCreate):
    """Tạo mới task thủ công."""
    task_dict = task_in.dict()
    task_dict["created_at"] = time.time()
    return db.insert_task(task_dict)

@app.post("/api/tasks/{task_id}/sync", tags=["Tasks"])
def sync_task_to_notion(task_id: str):
    """Kích hoạt đồng bộ hóa tác vụ cụ thể lên Notion."""
    success = db.sync_task_to_notion(task_id)
    if success:
        return {"status": "success", "message": f"Task {task_id} successfully synced to Notion."}
    raise HTTPException(status_code=404, detail="Task not found")

@app.post("/api/cron/scan", response_model=List[Task], tags=["System"])
def trigger_cron_scan():
    """Kích hoạt quét lịch sử chat tự động."""
    new_tasks = scanner.run_cron_scan()
    return new_tasks

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
