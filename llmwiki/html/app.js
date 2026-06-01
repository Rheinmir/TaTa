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

// Cron History Scanner connecting to Backend API
btnCronScan.addEventListener('click', async () => {
    btnCronScan.disabled = true;
    scanFeedback.className = "feedback-msg info";
    scanFeedback.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> Đang tự động quét lịch sử chat của tài khoản...`;
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/cron/scan`, {
            method: 'POST'
        });
        
        if (!response.ok) throw new Error('Cron scan failed');
        
        const newTasks = await response.json();
        
        if (newTasks.length > 0) {
            // Update global task list
            await fetchTasks();
            scanFeedback.className = "feedback-msg success";
            scanFeedback.innerHTML = `<i class="fa-solid fa-check"></i> Đã quét xong! AI phát hiện thêm ${newTasks.length} task mới và đẩy vào database.`;
            showToast(`AI đã tự động trích xuất thêm ${newTasks.length} công việc mới!`, 'success');
        } else {
            scanFeedback.className = "feedback-msg success";
            scanFeedback.innerHTML = `<i class="fa-solid fa-check"></i> Quét hoàn tất! Không phát hiện task mới nào chưa được ghi nhận.`;
            showToast('Không phát hiện công việc mới.', 'info');
        }
    } catch (error) {
        console.warn('FastAPI backend offline. Simulating local client-side cron scan.', error);
        
        // Dynamic client-side simulation (Fallback)
        setTimeout(() => {
            const newTasksText = [
                "@Bình làm giúp tôi báo cáo doanh thu tuần trước thứ Sáu nhé.",
                "Cần gấp: Anh An cấu hình cổng webhook bảo mật trước 12:00 ngày mai nha."
            ];
            
            const authors = ["Sếp Hoàng", "Lê Thị Thu"];
            const sources = ["Slack - #general", "MS Teams - #security"];
            
            const mockNewTasks = newTasksText.map((text, idx) => {
                let deadline = "Trước thứ Sáu";
                if (idx === 1) deadline = "Trước 12:00 ngày mai";
                
                return {
                    id: `task-cron-mock-${Date.now()}-${idx}`,
                    title: text,
                    requester: authors[idx],
                    assignee: idx === 0 ? "Bình" : "An",
                    deadline: deadline,
                    priority: idx === 0 ? "Medium" : "High",
                    source: sources[idx],
                    status: "Pending Review",
                    created_at: Date.now() / 1000,
                    synced_to_notion: false
                };
            });
            
            // Check duplicates
            const existingTitles = tasks.map(t => t.title);
            const filteredNewTasks = mockNewTasks.filter(t => !existingTitles.includes(t.title));
            
            if (filteredNewTasks.length > 0) {
                tasks = [...tasks, ...filteredNewTasks];
                scanFeedback.className = "feedback-msg success";
                scanFeedback.innerHTML = `<i class="fa-solid fa-check"></i> [Offline] AI phát hiện thêm ${filteredNewTasks.length} task mới từ chat.`;
                showToast(`[Offline Mode] AI phát hiện ${filteredNewTasks.length} công việc mới!`, 'success');
            } else {
                scanFeedback.className = "feedback-msg success";
                scanFeedback.innerHTML = `<i class="fa-solid fa-check"></i> [Offline] Quét xong. Không có task mới nào.`;
                showToast('Không có công việc mới.', 'info');
            }
            
            btnCronScan.disabled = false;
            renderTasks();
        }, 1500);
        return;
    }
    
    btnCronScan.disabled = false;
    // Clear message feedback after 5 seconds
    setTimeout(() => { scanFeedback.textContent = ''; }, 5000);
});

// Live Chat Crawler Interface & Connector Logic
const btnClaimRaw = document.getElementById('btn-claim-raw');
const rawMessageList = document.getElementById('raw-message-list');
let rawMessages = [];

async function fetchRawMessages() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/chat/raw`);
        if (!response.ok) throw new Error('Failed to fetch raw messages');
        rawMessages = await response.json();
        renderRawMessages();
    } catch (error) {
        console.warn('FastAPI offline. Raw message crawling restricted to simulation.', error);
    }
}

function renderRawMessages() {
    rawMessageList.innerHTML = '';
    
    if (rawMessages.length === 0) {
        rawMessageList.innerHTML = `
            <div style="font-size: 11px; color: var(--text-secondary); text-align: center; padding: 10px;">
                Chưa có dữ liệu thô. Hãy nhấp kết nối để crawl.
            </div>
        `;
        return;
    }
    
    rawMessages.forEach(msg => {
        const item = document.createElement('div');
        item.className = 'raw-message-item';
        
        const platformClass = msg.platform.toLowerCase().replace(' ', '-');
        
        item.innerHTML = `
            <div class="raw-message-info">
                <div class="raw-message-meta">
                    <span class="raw-platform-badge ${platformClass}">${msg.platform}</span>
                    <span>Từ: <strong>${msg.sender}</strong></span>
                </div>
                <div class="raw-message-text">"${msg.raw_text}"</div>
            </div>
            <button class="btn-extract" onclick="extractMessage('${msg.id}')">
                <i class="fa-solid fa-brain"></i> AI Extract
            </button>
        `;
        rawMessageList.appendChild(item);
    });
}

// Connect & Crawl Raw Chat Logs
btnClaimRaw.addEventListener('click', async () => {
    btnClaimRaw.disabled = true;
    btnClaimRaw.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> Đang crawl dữ liệu thô...`;
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/chat/claim-mock`, {
            method: 'POST'
        });
        if (!response.ok) throw new Error('Crawl failed');
        const data = await response.json();
        
        rawMessages = data.claimed_messages;
        showToast(data.message, 'success');
        
        // Fetch raw lists
        await fetchRawMessages();
    } catch (error) {
        // Fallback for offline simulation
        rawMessages = [
            {
                id: `raw-mock-1`,
                platform: "Slack",
                raw_text: "@Bình làm giúp tôi báo cáo doanh thu tuần trước thứ Sáu nhé.",
                sender: "Sếp Hoàng",
                channel: "Slack - #general"
            },
            {
                id: `raw-mock-2`,
                platform: "MS Teams",
                raw_text: "Cần gấp: Anh An cấu hình cổng webhook bảo mật trước 12:00 ngày mai nha.",
                sender: "Lê Thị Thu",
                channel: "MS Teams - #security"
            },
            {
                id: `raw-mock-3`,
                platform: "Zalo",
                raw_text: "Ngày mai 9:00 có họp tiến độ nha cả nhà, đừng đi trễ.",
                sender: "Trần Tuấn (Zalo)",
                channel: "Zalo Group"
            }
        ];
        renderRawMessages();
        showToast('Kết nối thành công! Bắt được 3 tin nhắn thô (Offline Mode)', 'success');
    }
    
    btnClaimRaw.disabled = false;
    btnClaimRaw.innerHTML = `<i class="fa-solid fa-circle-nodes"></i> <span>Kết nối & Crawl tin nhắn thô</span>`;
});

// AI Extract Message & Ingest to Supabase
async function extractMessage(msgId) {
    try {
        const response = await fetch(`${API_BASE_URL}/api/chat/process-claimed/${msgId}`, {
            method: 'POST'
        });
        if (!response.ok) throw new Error('Extraction failed');
        const data = await response.json();
        
        if (data.status === 'filtered') {
            showToast(data.message, 'info');
        } else {
            showToast('AI trích xuất thành công & lưu vào Supabase Queue!', 'success');
        }
        
        // Refresh both lists
        await fetchRawMessages();
        await fetchTasks();
    } catch (error) {
        // Offline Fallback simulation
        const target = rawMessages.find(m => m.id === msgId);
        if (!target) return;
        
        // Heuristic extraction simulation
        if (target.platform === 'Zalo') {
            showToast('AI Lọc thành công: Tin nhắn không chứa task thực tế, bỏ qua!', 'info');
        } else {
            const isHigh = target.raw_text.includes('Cần gấp');
            const parsedMock = {
                id: `task-mock-extracted-${Date.now()}`,
                title: target.raw_text.replace(/@\w+/g, '').replace('Cần gấp: ', '').trim(),
                requester: target.sender,
                assignee: target.platform === 'Slack' ? 'Bình' : 'An',
                deadline: target.platform === 'Slack' ? 'Trước thứ Sáu' : 'Trước 12:00 ngày mai',
                priority: isHigh ? 'High' : 'Medium',
                source: target.platform,
                status: "Pending Review",
                created_at: Date.now() / 1000,
                synced_to_notion: false
            };
            
            tasks.push(parsedMock);
            showToast('AI trích xuất thành công (Offline Mode)!', 'success');
        }
        
        // Remove from raw
        rawMessages = rawMessages.filter(m => m.id !== msgId);
        renderRawMessages();
        renderTasks();
    }
}

// MS Teams Device Code Flow Client-side Logic
const btnTeamsAuth = document.getElementById('btn-teams-auth');
const teamsAuthCard = document.getElementById('teams-auth-card');
const teamsAuthLink = document.getElementById('teams-auth-link');
const teamsAuthCode = document.getElementById('teams-auth-code');
const teamsAuthStatus = document.getElementById('teams-auth-status');
let teamsPollInterval = null;

btnTeamsAuth.addEventListener('click', async () => {
    btnTeamsAuth.disabled = true;
    btnTeamsAuth.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> Khởi tạo luồng...`;
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/chat/teams/auth-start`, {
            method: 'POST'
        });
        if (!response.ok) throw new Error('Start flow failed');
        
        const data = await response.json();
        
        // Show auth instructions card
        teamsAuthCard.style.display = 'block';
        teamsAuthLink.href = data.verification_uri;
        teamsAuthLink.textContent = data.verification_uri;
        teamsAuthCode.textContent = data.user_code;
        teamsAuthStatus.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> Đang chờ xác thực trên trình duyệt...`;
        
        // Start polling AD for token
        if (teamsPollInterval) clearInterval(teamsPollInterval);
        teamsPollInterval = setInterval(async () => {
            try {
                const pollRes = await fetch(`${API_BASE_URL}/api/chat/teams/auth-status`);
                const pollData = await pollRes.json();
                
                if (pollData.status === 'success') {
                    clearInterval(teamsPollInterval);
                    teamsAuthStatus.className = 'feedback-msg success';
                    teamsAuthStatus.innerHTML = `<i class="fa-solid fa-circle-check"></i> ${pollData.message}`;
                    showToast(pollData.message, 'success');
                    
                    // Hide auth card after 3 seconds
                    setTimeout(() => {
                        teamsAuthCard.style.display = 'none';
                        btnTeamsAuth.innerHTML = `<i class="fa-solid fa-circle-check"></i> <span>Teams Đã Liên Kết</span>`;
                    }, 3000);
                } else {
                    teamsAuthStatus.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> ${pollData.message}`;
                }
            } catch (pollErr) {
                console.error('Error polling auth status:', pollErr);
            }
        }, 3000);
        
    } catch (error) {
        console.warn('FastAPI offline. Simulating Teams Device Code Auth Flow.', error);
        
        // Simulation mode
        teamsAuthCard.style.display = 'block';
        teamsAuthLink.href = "https://microsoft.com/devicelogin";
        teamsAuthLink.textContent = "https://microsoft.com/devicelogin";
        teamsAuthCode.textContent = "TATA-CODE";
        teamsAuthStatus.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> [Offline] Chờ xác thực mã TATA-CODE...`;
        
        setTimeout(() => {
            teamsAuthStatus.innerHTML = `<i class="fa-solid fa-circle-check"></i> [Offline] Đăng nhập Teams cá nhân thành công!`;
            showToast('[Offline Mode] Đăng nhập Teams cá nhân thành công!', 'success');
            
            setTimeout(() => {
                teamsAuthCard.style.display = 'none';
                btnTeamsAuth.innerHTML = `<i class="fa-solid fa-circle-check"></i> <span>Teams Đã Liên Kết</span>`;
            }, 3000);
        }, 6000);
    }
    
    btnTeamsAuth.disabled = false;
    btnTeamsAuth.innerHTML = `<i class="fa-solid fa-key"></i> <span>Bắt đầu liên kết tài khoản</span>`;
});

// Initial load
window.addEventListener('DOMContentLoaded', () => {
    fetchTasks();
    fetchRawMessages();
    // Poll API status every 10 seconds to check if FastAPI server has started
    setInterval(() => {
        fetchTasks();
        fetchRawMessages();
    }, 10000);
});
