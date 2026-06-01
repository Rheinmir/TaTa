import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TaTa.Orchestrator")

class AIOrchestrator:
    """AI Orchestrator để đánh giá và phân phối công việc cho agent/orchestrator workflow."""
    
    def __init__(self):
        logger.info("Khởi tạo AI Orchestrator")
        
    def process_extracted_task(self, task_data: dict) -> dict:
        """Đánh giá độ phức tạp của task và phân luồng xử lý."""
        logger.info(f"Đang phân tích task: {task_data.get('title')}")
        deadline = task_data.get("deadline")
        
        # Logic đánh giá độ phức tạp ban đầu
        if "báo cáo" in task_data.get("title", "").lower() or "thiết kế" in task_data.get("title", "").lower():
            decision = "Orchestrator (Multi-step Workflow)"
        else:
            decision = "AI Agent (Automation/Script)"
            
        logger.info(f"AI Quyết định phân luồng: {decision}")
        return {
            "task_id": task_data.get("id"),
            "assigned_route": decision,
            "complexity": "High" if decision == "Orchestrator" else "Low"
        }
