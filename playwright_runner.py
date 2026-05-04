import os
import time
import threading
import random
from playwright.sync_api import sync_playwright, Playwright
import importlib

def run_playwright_profile(idx, pname, proxy_str, chat_id, monitor, config, stop_event, bot=None, output_file=None):
    timestamp = int(time.time())
    pid = f"PW_{pname.replace(' ', '_')}_{idx}_{timestamp}"
    pid_ref = [pid]
    
    def plog(msg):
        monitor.add_log(pid, msg)
        print(f"[{pname[:10]}] {msg}")

    max_retries = 3
    success = False
    last_error = ""
    for attempt in range(max_retries):
        try:
            if stop_event.is_set():
                plog("⏹ Đã nhận lệnh dừng toàn cục")
                return

            plog(f"⏳ Khởi động Playwright (Lần {attempt+1}/{max_retries})...")
            monitor.upsert(pid, pname, status="Đang mở")
            
            # Khởi tạo thư mục chứa profile
            user_data_dir = os.path.join(os.getcwd(), "profiles", f"{pid}_{attempt}")
            os.makedirs(user_data_dir, exist_ok=True)
            
            # Cấu hình proxy tự nhận diện mọi định dạng (Auto-recognize logic)
            proxy_config = None
            if proxy_str:
                proxy_str = proxy_str.strip()
                protocol = "http"
                if "://" in proxy_str:
                    protocol, proxy_str = proxy_str.split("://", 1)
                
                username = ""
                password = ""
                if "@" in proxy_str:
                    auth, proxy_str = proxy_str.split("@", 1)
                    if ":" in auth:
                        username, password = auth.split(":", 1)
                    else:
                        username = auth
                
                parts = proxy_str.split(':')
                if len(parts) >= 2:
                    ip = parts[0]
                    port = parts[1]
                    proxy_config = {"server": f"{protocol}://{ip}:{port}"}
                    
                    if username and password:
                        proxy_config["username"] = username
                        proxy_config["password"] = password
                    elif len(parts) == 4:
                        proxy_config["username"] = parts[2]
                        proxy_config["password"] = parts[3]

            with sync_playwright() as p:
                # Danh sách 50 thiết bị Android (Samsung, Pixel, Xiaomi, Oppo, Motorola...)
                android_profiles = [
                    {"name": "Galaxy S23 Ultra", "viewport": {"width": 412, "height": 915}, "scale": 3, "ua_model": "SM-S918B"},
                    {"name": "Galaxy S23+", "viewport": {"width": 360, "height": 780}, "scale": 3, "ua_model": "SM-S916B"},
                    {"name": "Galaxy S23", "viewport": {"width": 360, "height": 780}, "scale": 3, "ua_model": "SM-S911B"},
                    {"name": "Galaxy S22 Ultra", "viewport": {"width": 412, "height": 915}, "scale": 3, "ua_model": "SM-S908B"},
                    {"name": "Galaxy S22", "viewport": {"width": 360, "height": 780}, "scale": 3, "ua_model": "SM-S901B"},
                    {"name": "Galaxy S21 Ultra", "viewport": {"width": 384, "height": 854}, "scale": 3.5, "ua_model": "SM-G998B"},
                    {"name": "Galaxy S21", "viewport": {"width": 360, "height": 800}, "scale": 3, "ua_model": "SM-G991B"},
                    {"name": "Galaxy S20 FE", "viewport": {"width": 360, "height": 800}, "scale": 3, "ua_model": "SM-G780F"},
                    {"name": "Galaxy A54", "viewport": {"width": 384, "height": 854}, "scale": 2.5, "ua_model": "SM-A546B"},
                    {"name": "Galaxy A53", "viewport": {"width": 384, "height": 854}, "scale": 2.5, "ua_model": "SM-A536B"},
                    {"name": "Galaxy A34", "viewport": {"width": 384, "height": 854}, "scale": 2.5, "ua_model": "SM-A346B"},
                    {"name": "Galaxy Z Fold 5", "viewport": {"width": 344, "height": 884}, "scale": 3, "ua_model": "SM-F946B"},
                    {"name": "Galaxy Z Flip 5", "viewport": {"width": 412, "height": 1004}, "scale": 3, "ua_model": "SM-F731B"},
                    
                    {"name": "Pixel 8 Pro", "viewport": {"width": 412, "height": 915}, "scale": 3.5, "ua_model": "Pixel 8 Pro"},
                    {"name": "Pixel 8", "viewport": {"width": 412, "height": 915}, "scale": 3, "ua_model": "Pixel 8"},
                    {"name": "Pixel 7 Pro", "viewport": {"width": 412, "height": 915}, "scale": 3.5, "ua_model": "Pixel 7 Pro"},
                    {"name": "Pixel 7", "viewport": {"width": 412, "height": 915}, "scale": 2.75, "ua_model": "Pixel 7"},
                    {"name": "Pixel 7a", "viewport": {"width": 412, "height": 915}, "scale": 2.75, "ua_model": "Pixel 7a"},
                    {"name": "Pixel 6 Pro", "viewport": {"width": 412, "height": 915}, "scale": 3.5, "ua_model": "Pixel 6 Pro"},
                    {"name": "Pixel 6", "viewport": {"width": 412, "height": 915}, "scale": 2.625, "ua_model": "Pixel 6"},
                    {"name": "Pixel 6a", "viewport": {"width": 412, "height": 915}, "scale": 2.625, "ua_model": "Pixel 6a"},
                    
                    {"name": "Xiaomi 13 Pro", "viewport": {"width": 393, "height": 850}, "scale": 3, "ua_model": "2210132G"},
                    {"name": "Xiaomi 13", "viewport": {"width": 393, "height": 850}, "scale": 3, "ua_model": "2211133G"},
                    {"name": "Xiaomi 12T Pro", "viewport": {"width": 393, "height": 850}, "scale": 3, "ua_model": "22081212UG"},
                    {"name": "Redmi Note 12 Pro", "viewport": {"width": 393, "height": 850}, "scale": 2.75, "ua_model": "22101316G"},
                    {"name": "Redmi Note 11", "viewport": {"width": 393, "height": 850}, "scale": 2.75, "ua_model": "2201117TG"},
                    {"name": "Poco X5 Pro", "viewport": {"width": 393, "height": 850}, "scale": 2.75, "ua_model": "22101320G"},
                    
                    {"name": "OnePlus 11", "viewport": {"width": 412, "height": 915}, "scale": 3, "ua_model": "CPH2449"},
                    {"name": "OnePlus 10 Pro", "viewport": {"width": 412, "height": 915}, "scale": 3, "ua_model": "NE2215"},
                    {"name": "Oppo Find X5 Pro", "viewport": {"width": 412, "height": 915}, "scale": 3, "ua_model": "CPH2305"},
                    {"name": "Vivo X90 Pro", "viewport": {"width": 412, "height": 915}, "scale": 3, "ua_model": "V2219"},
                ]
                
                # Bơm thêm các máy phụ tự động cho lên đủ ~50 model
                brands_models = [
                    ("SM-A736B", 384, 854, 2.5), ("SM-M536B", 384, 854, 2.5),
                    ("SM-A235F", 360, 800, 2.5), ("SM-A146B", 360, 800, 2.5),
                    ("CPH2371", 360, 800, 2.5), ("CPH2363", 360, 800, 2.5),
                    ("V2130", 384, 854, 3), ("V2145", 384, 854, 3),
                    ("2203129G", 393, 850, 2.75), ("2201116SG", 393, 850, 2.75),
                    ("Motorola Edge 40", 412, 915, 2.75), ("Moto G73", 384, 854, 2.5),
                    ("SM-A125F", 360, 800, 2), ("SM-G981B", 360, 800, 3),
                    ("SM-G975F", 412, 869, 2.625), ("SM-N986B", 412, 869, 2.625)
                ]
                for model, w, h, s in brands_models:
                    android_profiles.append({"name": model, "viewport": {"width": w, "height": h}, "scale": s, "ua_model": model})

                selected_device = random.choice(android_profiles)
                device_name = selected_device["name"]
                
                if device_name in p.devices:
                    device = p.devices[device_name]
                else:
                    device = {
                        "viewport": selected_device["viewport"],
                        "device_scale_factor": selected_device["scale"],
                        "is_mobile": True,
                        "has_touch": True
                    }
                    
                # Sinh tự động các phiên bản Android và Chrome đa dạng
                android_versions = ["10", "11", "12", "13", "14"]
                chrome_versions = ["114.0.5735.196", "115.0.5790.166", "116.0.5845.163", "117.0.5938.153", "118.0.5993.111", "119.0.6045.163", "120.0.6099.144", "121.0.6167.164", "122.0.6261.90"]
                a_ver = random.choice(android_versions)
                c_ver = random.choice(chrome_versions)
                ua_model = selected_device["ua_model"]
                
                selected_ua = f"Mozilla/5.0 (Linux; Android {a_ver}; {ua_model}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{c_ver} Mobile Safari/537.36"

                # Khởi chạy Context có lưu giữ dữ liệu
                context = p.chromium.launch_persistent_context(
                    user_data_dir=user_data_dir,
                    headless=False,
                    proxy=proxy_config,
                    ignore_https_errors=True,
                    permissions=["clipboard-read", "clipboard-write"],
                    locale=config.get("locale", "vi-VN"),
                    timezone_id=config.get("timezone", "Asia/Ho_Chi_Minh"),
                    viewport=device.get("viewport"),
                    user_agent=selected_ua,
                    device_scale_factor=device.get("device_scale_factor"),
                    is_mobile=device.get("is_mobile"),
                    has_touch=device.get("has_touch"),
                    args=[
                        "--disable-blink-features=AutomationControlled",
                        "--no-sandbox",
                        "--disable-infobars"
                    ]
                )
                
                # Thêm script lẩn tránh WebDriver
                context.add_init_script("""
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    });
                """)

                monitor.set_status(pid, "Đang chạy")
                plog(f"🌐 Đã mở trình duyệt Playwright")
                
                # Lấy trang web mặc định
                page = context.pages[0] if context.pages else context.new_page()

                # Tải kịch bản tự động hóa (Sử dụng module độc lập cho mỗi luồng để tránh đụng độ biến toàn cục)
                import importlib.util
                import string
                rand_id = ''.join(random.choices(string.ascii_letters, k=6))
                spec = importlib.util.spec_from_file_location(f"browser_script_{rand_id}", "browser_script.py")
                browser_script = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(browser_script)
                
                # Tiêm các biến toàn cục
                browser_script.log = plog
                browser_script.monitor = monitor
                browser_script.pid = pid
                browser_script.stop_event = stop_event
                browser_script.fb_name_lang = config.get("fb_lang", "Tiếng Việt (Không dấu)")
                
                use_phone = config.get("use_phone_seed", True)
                browser_script.phone_prefix = config.get("phone_prefix", "0987") if use_phone else ""
                
                browser_script.api_dongvan = config.get("api_dongvan", "")
                browser_script.api_gmail = config.get("api_gmail", "")
                browser_script.api_shopmailmmo = config.get("api_shopmailmmo", "")
                browser_script.api_autosms = config.get("api_autosms", "")
                browser_script.dv_account = config.get("dv_account", "1")
                browser_script.reg_mode = config.get("reg_mode", "shopmail")
                browser_script.shared_state = config.get("shared_state", {})
                
                browser_script.selected_ua = selected_ua
                browser_script.device_name = device_name
                
                # Chạy kịch bản
                browser_script.run(page)
                
                # Hoàn thành
                monitor.set_status(pid, "Hoàn thành")
                
                # Xử lý kết quả đăng ký thành công
                profile_data = monitor.profiles.get(pid, {})
                if profile_data.get('uid'):
                    pwd = profile_data.get('passwd', 'k999999')
                    twofa_display = profile_data.get('twofa', '')
                    cookie_display = profile_data.get('cookie', '')
                    mail_display = profile_data.get('mail', '')
                    
                    # Định dạng: UID | Pass | 2FA | Mail | Cookie
                    # Nếu thiếu trường nào thì để trống trường đó nhưng vẫn giữ đúng số lượng dấu |
                    final_out = f"{profile_data['uid']}|{pwd}|{twofa_display}|{mail_display}|{cookie_display}"
                        
                    if bot and chat_id:
                        # import html
                        # final_out_escaped = html.escape(final_out)
                        # success_msg = f"🎉 <b>ĐĂNG KÝ THÀNH CÔNG {pname}</b>\n\n<code>{final_out_escaped}</code>"
                        # try:
                        #     bot.send_message(chat_id, success_msg, parse_mode="HTML")
                        #     plog("✅ Đã gửi thông tin tài khoản qua Telegram!")
                        # except Exception as e:
                        #     plog(f"⚠️ Không thể gửi tin nhắn Telegram: {e}")
                        #     bot.send_message(chat_id, f"🎉 ĐĂNG KÝ THÀNH CÔNG {pname}\n\n{final_out}")
                        pass
                    
                    plog("✅ Đã có kết quả tài khoản, chuẩn bị lưu vào file...")
                        
                    if output_file:
                        try:
                            with open(output_file, 'a', encoding='utf-8') as f:
                                f.write(f"{final_out}\n")
                        except Exception as e:
                            plog(f"⚠️ Không thể lưu vào file: {e}")
                
                context.close()
                success = True
                break # Thoát vòng lặp retry

        except Exception as ex:
            last_error = str(ex)
            if "StopScript" in str(type(ex)):
                monitor.set_status(pid, "Đã dừng")
                break
                
            if "Checkpoint" in last_error:
                monitor.set_status(pid, "Checkpoint")
                break
                
            plog(f"❌ Lỗi: {ex}")
            if attempt < max_retries - 1:
                monitor.set_status(pid, f"Thử lại ({attempt+2}/{max_retries})")
                time.sleep(3)
            else:
                monitor.set_status(pid, "Lỗi vĩnh viễn")

    return success, last_error
