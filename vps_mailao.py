import os
import sys
import time
import json
import threading
from concurrent.futures import ThreadPoolExecutor

# Import runner cốt lõi của hệ thống
try:
    from playwright_runner import run_playwright_profile
except ImportError as e:
    print(f"❌ Lỗi: {e}")
    print("❌ Vui lòng đảm bảo đã cài đặt đầy đủ thư viện (pip install playwright requests) và đặt file đúng thư mục.")
    sys.exit(1)

class DummyMonitor:
    """Mock Monitor để in log ra terminal thay vì gửi lên Telegram"""
    def __init__(self):
        self.profiles = {}

    def upsert(self, pid, pname=None, **kwargs):
        if pid not in self.profiles:
            self.profiles[pid] = {}
        if pname:
            self.profiles[pid]['name'] = pname
        for k, v in kwargs.items():
            self.profiles[pid][k] = v
            
    def set_status(self, pid, status): pass
    def add_log(self, pid, msg):
        # In log trực tiếp ra màn hình console của VPS
        print(f"[{pid}] {msg}")

def load_sys_config():
    if os.path.exists("config.json"):
        with open("config.json", "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def main():
    print("==================================================")
    print("       🚀 BOT REG CLONE (MAIL ẢO) CHO VPS        ")
    print("==================================================")
    
    try:
        thread_count = int(input("👉 Nhập số luồng chạy đồng thời (VD: 5): ").strip())
        total_accounts = int(input("👉 Nhập tổng số lượng tài khoản cần tạo (VD: 200): ").strip())
    except ValueError:
        print("❌ Lỗi: Số luồng và số lượng tài khoản phải là số nguyên!")
        input("Nhấn Enter để thoát...")
        return

    proxy_file = input("👉 Nhập tên file proxy (Mặc định là proxy.txt, ấn Enter để dùng mặc định): ").strip()
    if not proxy_file:
        proxy_file = "proxy.txt"
        
    proxies = []
    if os.path.exists(proxy_file):
        with open(proxy_file, "r", encoding="utf-8") as f:
            proxies = [line.strip() for line in f if line.strip()]
        print(f"✅ Đã tải {len(proxies)} proxy từ {proxy_file}")
    else:
        print(f"⚠️ Cảnh báo: Không tìm thấy file '{proxy_file}'. Hệ thống sẽ chạy KHÔNG DÙNG PROXY (IP gốc)!")
        confirm = input("Tiếp tục chạy bằng IP gốc? (y/n): ")
        if confirm.lower() != 'y':
            return

    # Thiết lập cấu hình chuyên dụng cho Mail Ảo
    config = load_sys_config()
    config['reg_mode'] = 'reg_mail_ao'
    config['shared_state'] = {}
    
    stop_event = threading.Event()
    monitor = DummyMonitor()
    
    # File lưu kết quả
    output_file = os.path.join(os.getcwd(), "account.txt")

    print(f"\n🔥 Bắt đầu chạy {total_accounts} tài khoản trên {thread_count} luồng...")
    print(f"💾 Nick Live sẽ được tự động lưu dồn vào: {output_file}\n")
    print("Lưu ý: Bấm Ctrl+C để dừng ngang quá trình chạy bất cứ lúc nào.")
    print("--------------------------------------------------\n")
    
    completed = 0
    lock = threading.Lock()

    def task_wrapper(i):
        nonlocal completed
        if stop_event.is_set(): return
        
        pname = f"Clone_{i+1}"
        proxy = proxies[i % len(proxies)] if proxies else ""
        pid = f"vps_{i}"
        
        try:
            # Gọi thẳng core của Playwright
            success, err = run_playwright_profile(pid, pname, proxy, "vps", monitor, config, stop_event, bot=None, output_file=output_file)
        except Exception as e:
            print(f"[{pid}] ❌ Lỗi ngoại lệ: {e}")
            
        with lock:
            completed += 1
            print(f"\n🟢 ---> Đã hoàn tất xử lý {completed}/{total_accounts} tài khoản. <--- 🟢\n")

    try:
        # Sử dụng ThreadPoolExecutor để quản lý luồng hiệu quả
        with ThreadPoolExecutor(max_workers=thread_count) as executor:
            for i in range(total_accounts):
                executor.submit(task_wrapper, i)
                time.sleep(5) # Delay 5s chờ mở mỗi luồng
    except KeyboardInterrupt:
        print("\n🛑 Nhận lệnh Ctrl+C từ người dùng! Đang hủy các trình duyệt, vui lòng chờ vài giây...")
        stop_event.set()
        
        # Kill sạch chrome nếu bị dừng ngang (giống bên Telegram)
        try:
            import subprocess
            cmd = 'wmic process where "name=\'chrome.exe\'" get processid,commandline'
            out = subprocess.check_output(cmd, shell=True).decode('utf-8', errors='ignore')
            for line in out.splitlines():
                if 'profiles\\vps_' in line and 'chrome.exe' in line:
                    parts = line.strip().split()
                    if parts:
                        process_id = parts[-1]
                        if process_id.isdigit():
                            subprocess.run(f'taskkill /F /PID {process_id} /T', shell=True, capture_output=True)
        except: pass
        
    print("\n==================================================")
    print("🎉 HOÀN THÀNH TOÀN BỘ QUÁ TRÌNH CHẠY!")
    print(f"👉 Hãy kiểm tra file {output_file} để lấy thành quả nhé.")
    print("==================================================")

if __name__ == "__main__":
    main()
