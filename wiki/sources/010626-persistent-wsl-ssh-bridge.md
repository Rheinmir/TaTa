# Giải pháp tự động hóa kết nối SSH WSL2 vĩnh viễn (Persistent WSL2 SSH Bridge)
**Type:** source
**Tags:** wsl2, ssh, automation, windows, persistence

Tài liệu này cung cấp giải pháp tự động hóa hoàn toàn luồng kết nối SSH từ máy ngoài vào WSL2 mỗi khi máy Windows khởi động, giúp bạn kết nối tức thời, không cần gõ mật khẩu và không cần thao tác thủ công.

---

## 1. Thiết lập Đăng nhập không cần mật khẩu (SSH Key Authentication)
*Tránh việc phải gõ mật khẩu `712002` mỗi lần kết nối.*

### Bước A: Sinh SSH Key trên máy Mac của bạn (Nếu chưa có)
Mở terminal trên máy Mac và chạy:
```bash
ssh-keygen -t rsa -b 4096 -C "mac-to-wsl"
```
*(Nhấn `Enter` liên tục để bỏ qua passphrase).*

### Bước B: Copy Public Key vào WSL2
Chạy lệnh sau để chuyển khóa công khai sang WSL (thay bằng IP thật):
```bash
ssh-copy-id -i ~/.ssh/id_rsa.pub -p 2222 ubuntu@100.92.21.47
```
*(Nhập mật khẩu `712002` lần cuối cùng. Từ nay về sau, bạn chỉ cần gõ `ssh ubuntu@100.92.21.47 -p 2222` là vào thẳng).*

---

## 2. Tự động hóa Khởi động SSH Service & Port Forwarding trên Windows
*Giải quyết triệt để vấn đề IP WSL2 bị thay đổi mỗi khi reboot và dịch vụ SSH tự tắt.*

Chúng ta sẽ tạo một Task Scheduler trên Windows để mỗi khi bật máy, Windows sẽ tự động lấy IP mới nhất của WSL, cấu hình PortProxy và bật SSH Service của WSL chạy ngầm.

### Bước A: Tạo script PowerShell tự động hóa (`wsl-ssh-bridge.ps1`)
Lưu đoạn script sau vào một thư mục trên Windows (ví dụ: `C:\Scripts\wsl-ssh-bridge.ps1`):

```powershell
# 1. Khởi động dịch vụ SSH bên trong WSL2 dưới quyền root
wsl.exe -u root -e service ssh start

# 2. Lấy IP động hiện tại của WSL2
$wslIp = wsl.exe hostname -I
$wslIp = $wslIp.Trim()

# 3. Cập nhật PortProxy cho cổng SSH 2222 và Web Port 8000
netsh interface portproxy delete v4tov4 listenport=2222 listenaddress=0.0.0.0
netsh interface portproxy add v4tov4 listenport=2222 listenaddress=0.0.0.0 connectport=2222 connectaddress=$wslIp

netsh interface portproxy delete v4tov4 listenport=8000 listenaddress=0.0.0.0
netsh interface portproxy add v4tov4 listenport=8000 listenaddress=0.0.0.0 connectport=8000 connectaddress=$wslIp

# 4. Đảm bảo Firewall đã mở các cổng này
New-NetFirewallRule -DisplayName "Allow WSL SSH Port 2222" -Direction Inbound -Action Allow -Protocol TCP -LocalPort 2222 -ErrorAction SilentlyContinue
New-NetFirewallRule -DisplayName "Allow TaTa Docker Port 8000" -Direction Inbound -Action Allow -Protocol TCP -LocalPort 8000 -ErrorAction SilentlyContinue
```

### Bước B: Đăng ký Tác vụ tự động chạy cùng Windows (Task Scheduler)
Để script trên tự chạy ẩn với quyền Administrator mỗi khi bật máy:

1. Mở **PowerShell (Run as Administrator)** trên máy Windows Host.
2. Chạy lệnh sau để đăng ký một Task Scheduler chạy ngầm vĩnh viễn:
```powershell
$action = New-ScheduledTaskAction -Execute 'PowerShell.exe' -Argument '-NoProfile -WindowStyle Hidden -File C:\Scripts\wsl-ssh-bridge.ps1'
$trigger = New-ScheduledTaskTrigger -AtLogOn
$principal = New-ScheduledTaskPrincipal -UserId "NT AUTHORITY\SYSTEM" -LogonType ServiceAccount -RunLevel Highest
Register-ScheduledTask -TaskName "WSL-SSH-Bridge" -Action $action -Trigger $trigger -Principal $principal -Description "Tự động kết nối SSH và Web Port từ ngoài vào WSL2 khi Windows khởi động."
```

---

## Kết quả đạt được
Từ nay về sau:
1. Bạn **bật máy Windows lên** $\rightarrow$ Tác vụ ngầm tự động lấy IP WSL2, thông cổng tường lửa, bật dịch vụ SSH.
2. Bạn **đứng từ máy Mac** gõ: `ssh ubuntu@100.92.21.47 -p 2222` $\rightarrow$ Vào thẳng Terminal WSL lập tức, không hỏi mật khẩu!
3. Bạn mở trình duyệt trên Mac truy cập `http://100.92.21.47:8000` $\rightarrow$ Load thẳng Dashboard tức thời!
