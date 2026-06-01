// API Configuration
const API_BASE_URL = 'http://localhost:8000';

// Global state
let tasks = [];

// DOM Elements
const taskListContainer = document.getElementById('task-list-container');
const taskCountBadge = document.getElementById('task-count');
const taskForm = document.getElementById('task-form');
const btnCronScan = document.getElementById('btn-cron-scan');
const scanFeedback = document.getElementById('scan-feedback');
const apiStatus = document.getElementById('api-status');

// Helper: Toast Notifications
function showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    
    let icon = 'fa-info-circle';
    if (type === 'success') icon = 'fa-check-circle';
    if (type === 'error') icon = 'fa-exclamation-circle';
    
    toast.innerHTML = `
        <i class="fa-solid ${icon}"></i>
        <span>${message}</span>
    `;
    
    container.appendChild(toast);
    
    // Auto-remove after 4 seconds
    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateY(-10px)';
        toast.style.transition = 'all 0.3s ease';
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}

// Fetch tasks from API
async function fetchTasks() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/tasks`);
        if (!response.ok) throw new Error('Failed to fetch tasks');
        tasks = await response.json();
        
        // Update API Status indicator
        apiStatus.classList.add('active');
        renderTasks();
    } catch (error) {
        console.warn('FastAPI backend is offline. Using mock client storage.', error);
        apiStatus.classList.remove('active');
        
        // Fallback mock data if server isn't running
        if (tasks.length === 0) {
            tasks = [
                {
                    id: "task-101",
                    title: "Viết tài liệu thiết kế hệ thống TaTa",
                    requester: "Nguyễn Văn A",
                    assignee: "Trần Thị B",
                    deadline: "2026-06-05 17:00",
                    priority: "High",
                    source: "Slack - #general",
                    status: "Synced",
                    created_at: Date.now() / 1000 - 3600,
                    synced_to_notion: true
                },
                {
                    id: "task-102",
                    title: "Setup database Supabase làm hàng đợi (Queue)",
                    requester: "Trần Thị B",
                    assignee: "Nguyễn Văn A",
                    deadline: "2026-06-03 12:00",
                    priority: "High",
                    source: "Self-chat",
                    status: "Pending Review",
                    created_at: Date.now() / 1000 - 1800,
                    synced_to_notion: false
                },
                {
                    id: "task-103",
                    title: "Nghiên cứu API Microsoft Teams Graph để nhận tin nhắn realtime",
                    requester: "Phạm Văn C",
                    assignee: "Trần Thị B",
                    deadline: "2026-06-10 18:00",
                    priority: "Medium",
                    source: "MS Teams - #tech",
                    status: "Pending Review",
                    created_at: Date.now() / 1000 - 600,
                    synced_to_notion: false
                }
            ];
        }
        renderTasks();
    }
}

// Render task cards
function renderTasks() {
    taskListContainer.innerHTML = '';
    taskCountBadge.textContent = `${tasks.length} task${tasks.length !== 1 ? 's' : ''}`;
    
    if (tasks.length === 0) {
        taskListContainer.innerHTML = `
            <div class="loading-state">
                <i class="fa-solid fa-folder-open"></i> Hàng đợi trống. Hãy thử giao việc!
            </div>
        `;
        return;
    }
    
    // Sort tasks: newest first
    const sortedTasks = [...tasks].sort((a, b) => b.created_at - a.created_at);
    
    sortedTasks.forEach(task => {
        const card = document.createElement('div');
        card.className = `task-card priority-${task.priority.toLowerCase()}`;
        
        const dateStr = new Date(task.created_at * 1000).toLocaleString('vi-VN', {
            hour: '2-digit',
            minute: '2-digit',
            day: '2-digit',
            month: '2-digit'
        });
        
        card.innerHTML = `
            <div class="task-header">
                <span class="task-title">${task.title}</span>
                <span class="task-source">${task.source}</span>
            </div>
            
            <div class="task-details">
                <div class="detail-item">
                    <i class="fa-solid fa-user-plus"></i>
                    <span>Người yêu cầu: <strong>${task.requester}</strong></span>
                </div>
                <div class="detail-item">
                    <i class="fa-solid fa-user-check"></i>
                    <span>Assignee: <strong>${task.assignee || 'Tự động phân phối'}</strong></span>
                </div>
                <div class="detail-item">
                    <i class="fa-solid fa-calendar-clock"></i>
                    <span>Deadline: <strong>${task.deadline || 'Không xác định'}</strong></span>
                </div>
                <div class="detail-item">
                    <i class="fa-solid fa-clock"></i>
                    <span>Tạo lúc: <strong>${dateStr}</strong></span>
                </div>
            </div>
            
            <div class="task-actions">
                <span class="task-status ${task.synced_to_notion ? 'status-synced' : 'status-pending'}">
                    <span class="status-dot"></span>
                    ${task.synced_to_notion ? 'Đã đồng bộ Notion' : 'Chờ kiểm duyệt'}
                </span>
                
                <button class="btn-sync" onclick="syncTask('${task.id}')" ${task.synced_to_notion ? 'disabled' : ''}>
                    <i class="fa-solid fa-rotate"></i>
                    <span>${task.synced_to_notion ? 'Đã sync' : 'Sync lên Notion'}</span>
                </button>
            </div>
        `;
        
        taskListContainer.appendChild(card);
    });
}

// Add task form submission (Self-chat simulation)
taskForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const titleVal = document.getElementById('task-title').value.strip ? document.getElementById('task-title').value.strip() : document.getElementById('task-title').value.trim();
    const priorityVal = document.getElementById('task-priority').value;
    const assigneeVal = document.getElementById('task-assignee').value || 'Nguyễn Văn A (Self)';
    
    if (!titleVal) return;
    
    // Parsing mock deadline & requester from self-chat message
    let deadline = "Không xác định";
    const deadlineMatch = titleVal.match(/trước\s+([^\s,]+(\s+[^\s,]+)*)/i);
    if (deadlineMatch) {
        deadline = deadlineMatch[1];
    }
    
    const taskPayload = {
        title: titleVal,
        requester: "Tôi (Self-chat)",
        assignee: assigneeVal,
        deadline: deadline,
        priority: priorityVal,
        source: "Self-chat",
        status: "Pending Review"
    };
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/tasks`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(taskPayload)
        });
        
        if (!response.ok) throw new Error('Network response not ok');
        const newDbTask = await response.json();
        tasks.push(newDbTask);
        showToast('Trích xuất & đẩy vào Supabase Queue thành công!', 'success');
    } catch (error) {
        // Fallback for offline mode
        const mockNewTask = {
            id: `task-${Date.now()}`,
            ...taskPayload,
            created_at: Date.now() / 1000,
            synced_to_notion: false
        };
        tasks.push(mockNewTask);
        showToast('Đã lưu task mới vào bộ nhớ Client offline.', 'info');
    }
    
    // Clear form & re-render
    document.getElementById('task-title').value = '';
    document.getElementById('task-assignee').value = '';
    renderTasks();
});

// Sync task to Notion
async function syncTask(taskId) {
    try {
        const response = await fetch(`${API_BASE_URL}/api/tasks/${taskId}/sync`, {
            method: 'POST'
        });
        if (!response.ok) throw new Error('Notion sync failed');
        
        // Update local state
        tasks = tasks.map(t => t.id === taskId ? { ...t, synced_to_notion: true, status: "Synced" } : t);
        showToast('Đồng bộ lên Notion thành công!', 'success');
        renderTasks();
    } catch (error) {
        // Fallback for offline mode
        tasks = tasks.map(t => t.id === taskId ? { ...t, synced_to_notion: true, status: "Synced" } : t);
        showToast('Simulated Notion Sync thành công (Offline Mode)', 'success');
        renderTasks();
    }
}

// Cron History Scanner simulation
btnCronScan.addEventListener('click', async () => {
    btnCronScan.disabled = true;
    scanFeedback.className = "feedback-msg info";
    scanFeedback.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> Đang tự động quét lịch sử chat của tài khoản...`;
    
    setTimeout(async () => {
        const newTasksText = [
            "@B hoàn thành file thiết kế UI/UX dashboard trước thứ 6",
            "Nhắc việc: Gửi email spec dự án cho khách hàng trước 15:00 hôm nay"
        ];
        
        const authors = ["Sếp Hoàng", "Đối tác Zalo"];
        const sources = ["Slack - #general", "Zalo - Group Chat"];
        
        const mockNewTasks = newTasksText.map((text, idx) => {
            let deadline = "Trước thứ 6";
            if (idx === 1) deadline = "15:00 hôm nay";
            
            return {
                id: `task-cron-${Date.now()}-${idx}`,
                title: text,
                requester: authors[idx],
                assignee: idx === 0 ? "Trần Thị B" : "Nguyễn Văn A",
                deadline: deadline,
                priority: idx === 0 ? "High" : "Medium",
                source: sources[idx],
                status: "Pending Review",
                created_at: Date.now() / 1000,
                synced_to_notion: false
            };
        });
        
        // Push mock items
        tasks = [...tasks, ...mockNewTasks];
        
        scanFeedback.className = "feedback-msg success";
        scanFeedback.innerHTML = `<i class="fa-solid fa-check"></i> Đã quét xong! AI phát hiện và tự động trích xuất thêm 2 task mới.`;
        showToast('AI đã tự động trích xuất 2 công việc từ lịch sử chat!', 'success');
        
        btnCronScan.disabled = false;
        renderTasks();
        
        // Clear message feedback after 5 seconds
        setTimeout(() => { scanFeedback.textContent = ''; }, 5000);
    }, 2000);
});

// Initial load
window.addEventListener('DOMContentLoaded', () => {
    fetchTasks();
    // Poll API status every 10 seconds to check if FastAPI server has started
    setInterval(fetchTasks, 10000);
});
