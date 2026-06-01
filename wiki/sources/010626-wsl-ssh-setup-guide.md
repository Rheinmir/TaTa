# Hướng dẫn thiết lập SSH kết nối từ xa vào WSL2 qua IP Windows Host (100.92.21.47)
**Type:** source
**Tags:** wsl2, ssh, setup, network, windows

Tài liệu này hướng dẫn chi tiết cách cấu hình SSH Server trên WSL2 và mở cổng kết nối từ máy ngoài thông qua địa chỉ IP của máy Host Windows (`100.92.21.47`).

Do WSL2 chạy dưới dạng máy ảo hypervisor sử dụng card mạng ảo NAT riêng biệt, các máy bên ngoài không thể kết nối trực tiếp đến IP nội bộ của WSL. Có 2 cách để xử lý vấn đề này:

---

## Cấu hình chuẩn bị trên WSL (Làm trước)

Mở terminal WSL của bạn lên và thực hiện các bước sau để cài đặt và cấu hình SSH Server:

### 1. Cài đặt OpenSSH Server
```bash
sudo apt update
sudo apt install -y openssh-server
```

### 2. Cấu hình SSH Daemon (`sshd_config`)
Mở file cấu hình sshd:
```bash
sudo nano /etc/ssh/sshd_config
```
Tìm và sửa đổi/thêm các dòng sau (để tránh xung đột với cổng SSH mặc định của Windows):
```text
Port 2222
ListenAddress 0.0.0.0
PasswordAuthentication yes
PermitRootLogin yes
```
*Nhấn `Ctrl + O` để lưu, `Enter`, và `Ctrl + X` để thoát.*

### 3. Khởi động lại dịch vụ SSH
```bash
sudo service ssh restart
```

---

## PHƯƠNG ÁN 1: Sử dụng WSL Mirrored Networking (Khuyên dùng - Dành cho Windows 11)
*Nếu máy Windows Host đang chạy **Windows 11 (bản cập nhật mới)**, chế độ mạng Mirrored là cách đơn giản và tối ưu nhất để WSL chia sẻ chung card mạng và IP với Windows.*

### 1. Tạo file cấu hình `.wslconfig`
Trên Windows Host, mở PowerShell hoặc Explorer truy cập vào thư mục User Profile (`C:\Users\<Tên_User>\`).
Tạo một file văn bản tên là `.wslconfig` với nội dung sau:
```text
[wsl2]
networkingMode=mirrored
```

### 2. Khởi động lại WSL
Mở PowerShell trên Windows và chạy lệnh để tắt hẳn WSL:
```powershell
wsl --shutdown
```
Mở lại terminal WSL. Giờ đây, dịch vụ SSH lắng nghe trên cổng `2222` của WSL sẽ tự động liên kết trực tiếp với cổng `2222` của IP Windows Host (`100.92.21.47`). Bạn có thể kết nối ngay lập tức!

---

## PHƯƠNG ÁN 2: Cấu hình Port Forwarding cổ điển (Dành cho cả Windows 10 & 11)
*Nếu không dùng được chế độ mạng Mirrored, bạn cần cấu hình Windows Host chuyển tiếp luồng dữ liệu (port forwarding) từ IP Windows sang IP của WSL.*

### 1. Tạo script tự động lấy IP WSL và Port Forwarding
Do IP của WSL2 thay đổi mỗi lần máy tính khởi động lại, cách tốt nhất là tạo một script tự động chạy trên Windows Host qua PowerShell (chạy với quyền Administrator):

Mở PowerShell với quyền **Run as Administrator** và chạy đoạn script sau:

```powershell
# 1. Định nghĩa các cổng kết nối
$ports = @(2222)

# 2. Lấy IP nội bộ hiện tại của WSL2
$wslIp = wsl hostname -I
$wslIp = $wslIp.Trim()
Write-Host "WSL 2 IP Address: $wslIp"

# 3. Tạo các rule chuyển tiếp cổng (PortProxy) trên Windows Host
foreach ($port in $ports) {
    netsh interface portproxy delete v4tov4 listenport=$port listenaddress=0.0.0.0
    netsh interface portproxy add v4tov4 listenport=$port listenaddress=0.0.0.0 connectport=$port connectaddress=$wslIp
    Write-Host "Forwarding port $port to WSL..."
}

# 4. Mở cổng trên Windows Defender Firewall để cho phép máy ngoài truy cập
New-NetFirewallRule -DisplayName "Allow WSL SSH Port 2222" -Direction Inbound -Action Allow -Protocol TCP -LocalPort 2222
```

---

## Kiểm thử kết nối từ máy ngoài

Từ máy tính khác (hoặc server khác trong mạng VPN/Tailscale):

```bash
ssh ubuntu@100.92.21.47 -p 2222
```

Nhập mật khẩu tài khoản WSL của bạn để truy cập trực tiếp!

---

## Tự động kích hoạt SSH khi bật máy Windows
Để không phải gõ `sudo service ssh start` thủ công mỗi lần vào WSL, bạn có thể thiết lập cho dịch vụ tự động chạy:

Trong WSL, cấu hình `sudoers` để không bắt nhập pass khi chạy SSH service:
```bash
sudo visudo
```
Thêm dòng này vào cuối file:
```text
%sudo ALL=NOPASSWD: /usr/sbin/service ssh *
```
Sau đó, bạn có thể kích hoạt dịch vụ tự động bằng cách đặt lệnh này vào file khởi động của bạn hoặc lập lịch Task Scheduler trên Windows.
