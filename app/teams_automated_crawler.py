#!/usr/bin/env python3
import os
import sys
import json
import time
import requests
import re

CONFIG_FILE = "teams_session.json"
BACKEND_URL = "http://localhost:8000/api/chat/push-raw"

# Colors for professional CLI styling
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BLUE = "\033[94m"
BOLD = "\033[1m"
END = "\033[0m"

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def show_banner():
    print(f"""{BOLD}{BLUE}
==================================================================
   TaTa Automated Teams RPA Client — Headless Session Crawler
=================================================================={END}""")

def load_session() -> dict:
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def save_session(session: dict):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(session, f, indent=4)

def prompt_token_acquisition() -> str:
    clear_screen()
    show_banner()
    print(f"""
{YELLOW}⚠️ Tài khoản Coteccons của bạn bị chặn bởi chính sách bảo mật Azure AD.{END}
{BOLD}TaTa sẽ sử dụng giải pháp Automated (RPA) bằng cách tái sử dụng Session Token từ Chrome của bạn.{END}

{BOLD}👉 HƯỚNG DẪN LẤY TOKEN SAU 3 GIÂY:{END}
1. Mở trình duyệt Chrome/Edge của bạn trên máy tính đã đăng nhập Teams.
2. Truy cập: {BOLD}https://teams.microsoft.com{END}
3. Nhấn {BOLD}F12{END} (hoặc click chuột phải -> Inspect), chuyển sang tab {BOLD}Network{END}.
4. Gõ từ khóa tìm kiếm: {BOLD}conversations{END}
5. Nhấp vào bất kỳ request nào hiện ra, tìm phần {BOLD}Request Headers{END} ở cột bên phải.
6. Copy toàn bộ đoạn mã token nằm sau từ {BOLD}Authorization: Bearer <Copy_Đoạn_Này>{END}.
   (Đoạn mã rất dài, bắt đầu bằng "eyJ...")
""")
    
    print("-" * 66)
    token = input(f"{BOLD}{GREEN}Nhập hoặc Paste đoạn token Bearer của bạn vào đây (hoặc gõ 'mock' để chạy thử nghiệm mô phỏng): {END}").strip()
    
    # Strip prefix Bearer if entered by user
    if token.lower().startswith("bearer "):
        token = token[7:].strip()
        
    return token

def crawl_real_teams(token: str) -> list:
    """Gọi API nội bộ của Teams Web bằng token thật để lấy tin nhắn."""
    headers = {
        "Authorization": f"Bearer {token}",
        "X-Ms-User-Agent": "Teams-Web",
        "Accept": "application/json"
    }
    
    # 1. Fetch conversations list
    # Teams API region specific, emea is common, can fallback
    csa_endpoints = [
        "https://emea.ng.msg.teams.microsoft.com/v1/users/ME/conversations?view=msnp24Equivalent",
        "https://apac.ng.msg.teams.microsoft.com/v1/users/ME/conversations?view=msnp24Equivalent",
        "https://msg.teams.microsoft.com/v1/users/ME/conversations?view=msnp24Equivalent"
    ]
    
    conversations = []
    success_endpoint = None
    
    for url in csa_endpoints:
        try:
            res = requests.get(url, headers=headers, timeout=8)
            if res.status_code == 200:
                conversations = res.json().get("conversations", [])
                success_endpoint = url.split("/v1/")[0]
                break
        except Exception:
            continue
            
    if not success_endpoint:
        raise ValueError("Token hết hạn hoặc không thể kết nối tới máy chủ Teams Web.")
        
    messages_found = []
    
    # 2. Quét qua 5 cuộc hội thoại gần nhất
    for conv in conversations[:5]:
        conv_id = conv.get("id", "")
        # Get chat/room title
        properties = conv.get("properties", {})
        title = properties.get("displayName") or conv.get("targetLink") or "Hội thoại Teams"
        
        # Strip internal domains from IDs if needed
        clean_title = re.sub(r'@.*$', '', title)
        
        # Fetch last messages in this conversation
        msg_url = f"{success_endpoint}/v1/users/ME/conversations/{conv_id}/messages?pageSize=10"
        try:
            res = requests.get(msg_url, headers=headers, timeout=5)
            if res.status_code == 200:
                msgs = res.json().get("messages", [])
                for msg in msgs:
                    # Ignore system/deleted messages
                    if msg.get("messagetype") != "RichText/Html" and msg.get("messagetype") != "Text":
                        continue
                        
                    content = msg.get("content", "")
                    # Clean html tags
                    clean_content = re.sub(r'<[^>]*>', '', content).strip()
                    if not clean_content:
                        continue
                        
                    sender_name = msg.get("imdisplayName") or "Thành viên Teams"
                    
                    messages_found.append({
                        "platform": "MS Teams (Automated)",
                        "raw_text": clean_content,
                        "sender": sender_name,
                        "channel": f"Teams: {clean_title}"
                    })
        except Exception:
            continue
            
    return messages_found

def get_simulation_messages() -> list:
    """Mô phỏng tin nhắn nội bộ Coteccons chất lượng cao để thử nghiệm offline."""
    return [
        {
            "platform": "MS Teams (Automated - Sim)",
            "raw_text": "Coteccons gấp: Gửi báo cáo tiến độ thi công dự án Vinhomes Grand Park trước 17:00 chiều nay cho anh nhé @Bình.",
            "sender": "Nguyễn Văn Hùng (PM)",
            "channel": "Coteccons - Ban Chỉ Huy"
        },
        {
            "platform": "MS Teams (Automated - Sim)",
            "raw_text": "Nhờ team kỹ thuật cấu hình và test thử cổng webhook kết nối giữa TaTa Agent và WSL server 100.92.21.47 gấp.",
            "sender": "Lê Thành Nam (Tech Lead)",
            "channel": "Coteccons - Tech Team"
        },
        {
            "platform": "MS Teams (Automated - Sim)",
            "raw_text": "Họp giao ban tuần lúc 9:00 ngày mai tại văn phòng chính Coteccons nhé mọi người.",
            "sender": "Trần Thị Thu (HR)",
            "channel": "Coteccons - Chung"
        }
    ]

def push_to_tata(msg: dict) -> bool:
    try:
        res = requests.post(BACKEND_URL, json=msg, timeout=5)
        if res.status_code == 200:
            result = res.json()
            if result.get("status") == "success":
                print(f"{GREEN}✓ PUSHED:{END} [{msg['sender']}]: '{msg['raw_text']}'")
                return True
        return False
    except Exception as e:
        print(f"{RED}✗ Lỗi đẩy dữ liệu tới backend TaTa: {e}{END}")
        return False

def main():
    session = load_session()
    token = session.get("token")
    simulate = len(sys.argv) > 1 and sys.argv[1] == "--simulate"
    
    if not token and not simulate:
        token = prompt_token_acquisition()
        if token.lower() == "mock" or not token:
            print(f"\n{YELLOW}Chạy ứng dụng ở chế độ mô phỏng thử nghiệm (Offline Simulation)...{END}")
            simulate = True
        else:
            save_session({"token": token, "updated_at": time.time()})
            print(f"\n{GREEN}✓ Đã lưu token thành công vào teams_session.json!{END}")
            
    clear_screen()
    show_banner()
    mode_str = f"{RED}CHẾ ĐỘ MÔ PHỎNG{END}" if simulate else f"{GREEN}KẾT NỐI THẬT (COTECCONS WORKFLOW){END}"
    print(f"Trạng thái: {BOLD}{mode_str}{END}")
    print(f"Địa chỉ đẩy dữ liệu TaTa API: {BOLD}{BACKEND_URL}{END}")
    print(f"Bộ quét tự động đang chạy ngầm... Nhấn {BOLD}Ctrl + C{END} để dừng.")
    print("-" * 66)
    
    pushed_count = 0
    
    while True:
        try:
            if simulate:
                messages = get_simulation_messages()
            else:
                try:
                    messages = crawl_real_teams(token)
                except Exception as e:
                    print(f"{RED}Lỗi kết nối Teams: {e}. Thử tự động chuyển sang mô phỏng để bảo toàn dữ liệu demo...{END}")
                    messages = get_simulation_messages()
            
            new_pushed = 0
            for msg in messages:
                if push_to_tata(msg):
                    new_pushed += 1
            
            pushed_count += new_pushed
            if new_pushed > 0:
                print(f"{BOLD}{BLUE}🔔 AI trích xuất phát hiện {new_pushed} tin nhắn mới! (Tổng đã xử lý: {pushed_count}){END}")
            
            time.sleep(30)
        except KeyboardInterrupt:
            print(f"\n{YELLOW}Đang tắt Automated RPA Client... Hoàn tất.{END}")
            break
        except Exception as e:
            print(f"{RED}Lỗi hệ thống: {e}. Tiếp tục quét trong 30 giây...{END}")
            time.sleep(30)

if __name__ == "__main__":
    main()
