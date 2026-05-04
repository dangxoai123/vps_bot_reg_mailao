# ============================================================
#   BROWSER SCRIPT - GPM Login Automation
#   Chỉnh sửa phần "CẤU HÌNH" và "VIẾT SCRIPT CỦA BẠN" bên dưới
# ============================================================

import requests
import os
import time
import json
import random
from datetime import datetime
import pyotp

# ============================================================
#   CẤU HÌNH - Chỉnh sửa tại đây
# ============================================================

GPM_API      = "http://127.0.0.1:19995"
PROFILE_ID   = ""          # ← Dán profile ID vào đây (bắt buộc)
                            #   Lấy từ dashboard hoặc API danh sách profiles
WIN_SCALE    = 0.9          # Tỉ lệ cửa sổ (0.0 - 1.0)
WIN_POS      = "0,0"        # Vị trí cửa sổ "x,y"
WIN_SIZE     = ""           # Kích thước "width,height" (để trống = mặc định)

# ============================================================
#   HÀM TIỆN ÍCH - Không cần chỉnh sửa
# ============================================================

def log(msg: str):
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] {msg}")

def gpm_open(profile_id: str) -> dict:
    """Mở profile GPM, trả về thông tin kết nối."""
    params = {"win_scale": WIN_SCALE}
    if WIN_POS:
        params["win_pos"] = WIN_POS
    if WIN_SIZE:
        params["win_size"] = WIN_SIZE
    url = f"{GPM_API}/api/v3/profiles/start/{profile_id}"
    r = requests.get(url, params=params, timeout=60)
    return r.json()

def gpm_close(profile_id: str):
    """Đóng profile GPM."""
    url = f"{GPM_API}/api/v3/profiles/close/{profile_id}"
    r = requests.get(url, timeout=30)
    return r.json()

def connect_browser(remote_addr: str, driver_path: str, browser_location: str):
    """Kết nối Selenium vào browser đang chạy."""
    options = Options()
    options.add_experimental_option("debuggerAddress", remote_addr)
    options.binary_location = browser_location
    service = Service(executable_path=driver_path)
    page = webdriver.Chrome(service=service, options=options)
    log(f"✅ Kết nối trình duyệt thành công | {remote_addr}")
    return page

    """Chờ element xuất hiện VÀ HIỂN THỊ rồi trả về."""
    return WebDriverWait(page, timeout).until(
        EC.visibility_of_element_located((by, selector))
    )

def wait_click(page, by, selector, timeout=10):
    """Chờ element có thể click rồi click."""
    el = WebDriverWait(page, timeout).until(
        EC.element_to_be_clickable((by, selector))
    )
    el.click()
    return el

def save_cookies(page, filepath: str):
    """Lưu cookies ra file JSON."""
    cookies = page.context.cookies()
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(cookies, f, indent=2, ensure_ascii=False)
    log(f"🍪 Đã lưu {len(cookies)} cookies → {filepath}")

def load_cookies(page, filepath: str):
    """Nạp cookies từ file JSON vào browser."""
    if not os.path.exists(filepath):
        log(f"⚠ Không tìm thấy file cookies: {filepath}")
        return
    with open(filepath, encoding="utf-8") as f:
        cookies = json.load(f)
    for c in cookies:
        c.pop("sameSite", None)
        try:
            page.add_cookie(c)
        except Exception:
            pass
    log(f"🍪 Đã nạp {len(cookies)} cookies từ {filepath}")

def screenshot(page, filename: str = ""):
    """Chụp màn hình, lưu vào thư mục screenshots/."""
    os.makedirs("screenshots", exist_ok=True)
    if not filename:
        filename = datetime.now().strftime("screenshot_%Y%m%d_%H%M%S.png")
    path = os.path.join("screenshots", filename)
    page.save_screenshot(path)
    log(f"📸 Đã lưu: {path}")
    return path

# ============================================================
#   TẠO TÊN RANDOM
# ============================================================
def generate_random_name(lang="Tiếng Việt (Không dấu)"):
    if "Anh" in lang:
        first_names = ["James", "John", "Robert", "Michael", "William", "David", "Richard", "Charles", "Joseph", "Thomas", "Mary", "Patricia", "Jennifer", "Linda", "Elizabeth", "Barbara", "Susan", "Jessica", "Sarah", "Karen"]
        last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin"]
        # Trả về: Họ (Last), Tên (First)
        return random.choice(last_names), random.choice(first_names)
    else:
        # Tiếng Việt không dấu
        first_names = ["Nguyen", "Tran", "Le", "Pham", "Hoang", "Huynh", "Phan", "Vu", "Vo", "Dang", "Bui", "Do", "Ho", "Ngo", "Duong", "Ly"]
        last_names = ["An", "Anh", "Binh", "Cuong", "Dung", "Dat", "Huy", "Hai", "Hung", "Khai", "Long", "Nam", "Phuc", "Quan", "Son", "Tai", "Tuan", "Thang", "Truong", "Vinh", "Hoa", "Lan", "Mai", "Lien", "Yen", "Trang", "Nhung", "Oanh"]
        # Trả về: Họ, Tên
        return random.choice(first_names), random.choice(last_names)

# ============================================================
#   KHỞI ĐỘNG - Mở profile và kết nối browser
# ============================================================

def startup():
    if not PROFILE_ID:
        raise ValueError("⛔ Chưa nhập PROFILE_ID! Hãy điền vào phần CẤU HÌNH phía trên.")

    log(f"⏳ Đang mở profile: {PROFILE_ID[:8]}...")
    res = gpm_open(PROFILE_ID)

    if not res.get("success"):
        raise RuntimeError(f"❌ Không mở được profile: {res.get('message', '')}")

    data          = res["data"]
    remote_addr   = data["remote_debugging_address"]
    driver_path   = data["driver_path"]
    browser_loc   = data["browser_location"]

    page = connect_browser(remote_addr, driver_path, browser_loc)
    return page

# ============================================================
#   VIẾT SCRIPT CỦA BẠN TẠI ĐÂY
# ============================================================

def run(page):
    """
    Hàm chính - viết toàn bộ automation tại đây.
    Biến sẵn có:
        page  → Selenium WebDriver
        log()   → In ra console kèm timestamp
        wait()  → Chờ element
        wait_click() → Chờ rồi click
        save_cookies() / load_cookies()
        screenshot()
    """

    while True:
        # Kiểm tra nếu người dùng nhấn Dừng trên dashboard
        if globals().get("stop_event") and stop_event.is_set():
            log("⏹ Đã dừng script theo yêu cầu.")
            break

        try:
            # ── Mở trang Facebook ─────────────────────────
            log("🚀 Bắt đầu / Tải lại script...")
            
            # --- CDP: MÔ PHỎNG THIẾT BỊ THẬT MỨC ĐỘ LÕI CHROMIUM ---
            try:
                client = page.context.new_cdp_session(page)
                
                import random
                ram = random.choice([4, 6, 8])
                cores = random.choice([4, 6, 8])
                battery_level = round(random.uniform(0.25, 0.95), 2)
                charging = random.choice(['true', 'false'])
                log(f"📱 Fake Hardware: {ram}GB RAM, {cores} Cores, Pin {int(battery_level*100)}% ({'Sạc' if charging=='true' else 'Không sạc'})")

                # 1. Bơm thông số ẩn sâu trước khi V8 Javascript Engine khởi tạo
                client.send("Page.addScriptToEvaluateOnNewDocument", {
                    "source": f"""
                        // Xóa cờ báo hiệu tự động hóa
                        Object.defineProperty(navigator, 'webdriver', {{get: () => undefined}});
                        
                        // Fake phần cứng ngẫu nhiên
                        Object.defineProperty(navigator, 'deviceMemory', {{get: () => {ram}}});
                        Object.defineProperty(navigator, 'hardwareConcurrency', {{get: () => {cores}}});
                        
                        // Fake pin (Battery API)
                        const fakeBattery = {{
                            charging: {charging},
                            chargingTime: 0,
                            dischargingTime: Infinity,
                            level: {battery_level},
                            onchargingchange: null,
                            onchargingtimechange: null,
                            ondischargingtimechange: null,
                            onlevelchange: null
                        }};
                        navigator.getBattery = () => Promise.resolve(fakeBattery);
                        
                        // Fake GPU Vendor (Android)
                        const gpus = [
                            {{v: 'Google Inc. (Qualcomm)', r: 'ANGLE (Qualcomm, Adreno (TM) 730, OpenGL 3.2)'}},
                            {{v: 'Google Inc. (ARM)', r: 'ANGLE (ARM, Mali-G710, OpenGL 3.2)'}},
                            {{v: 'Google Inc. (Qualcomm)', r: 'ANGLE (Qualcomm, Adreno (TM) 640, OpenGL 3.2)'}},
                            {{v: 'Google Inc. (Qualcomm)', r: 'ANGLE (Qualcomm, Adreno (TM) 618, OpenGL 3.2)'}},
                            {{v: 'Google Inc. (ARM)', r: 'ANGLE (ARM, Mali-G52, OpenGL 3.2)'}}
                        ];
                        const gpu = gpus[Math.floor(Math.random() * gpus.length)];
                        const getParameter = WebGLRenderingContext.prototype.getParameter;
                        WebGLRenderingContext.prototype.getParameter = function(parameter) {{
                            if (parameter === 37445) return gpu.v; // VENDOR
                            if (parameter === 37446) return gpu.r; // RENDERER
                            return getParameter(parameter);
                        }};
                    """
                })

                # 2. Giả lập Client Hints (Cực kỳ quan trọng để lừa thuật toán AI của FB)
                ua = globals().get("selected_ua", "Mozilla/5.0 (Linux; Android 13; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Mobile Safari/537.36")
                client.send("Network.setUserAgentOverride", {
                    "userAgent": ua,
                    "acceptLanguage": "vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7",
                    "platform": "Linux armv81"
                })

                # 3. Kích hoạt mô phỏng cảm ứng màn hình thật (Mobile Touch)
                client.send("Emulation.setTouchEmulationEnabled", {
                    "enabled": True,
                    "maxTouchPoints": 5
                })
                client.send("Emulation.setEmitTouchEventsForMouse", {
                    "enabled": True,
                    "configuration": "mobile"
                })
                dev_name = globals().get('device_name', 'iPhone')
                log(f"📱 Đã giả lập môi trường {dev_name} (CDP) thành công!")
            except Exception as e:
                log(f"⚠️ Cảnh báo: Không thể khởi tạo CDP giả lập thiết bị - {e}")
            # -----------------------------------------------------------

            log("🌐 Đang chuyển hướng sang m.facebook.com...")
            # Sử dụng domcontentloaded để không bị treo khi proxy tải ảnh/video chậm
            page.goto("https://m.facebook.com", timeout=60000, wait_until="domcontentloaded")

            # Đợi nó tải xong (tối đa 15s), nếu quá hạn vẫn chạy tiếp vì có thể nút bấm đã xuất hiện
            log("📱 Đang chờ trang m.facebook.com tải (tối đa 15s)...")
            try:
                page.wait_for_load_state("load", timeout=15000)
            except:
                log("⚠️ Trang tải chưa hoàn tất 100% nhưng vẫn tiếp tục kiểm tra DOM...")
            log("✅ Trang m.facebook.com đã sẵn sàng!")

            # Đưa cửa sổ lên trên cùng nếu cần
            log(f"📄 Trang hiện tại: {page.title()}")
            

            # ── Thêm code thao tác với Facebook của bạn bên dưới ─────────
            
            # 1. Lấy thông tin từ Dashboard truyền vào
            lang = globals().get("fb_name_lang", "Tiếng Việt (Không dấu)")
            prefix = globals().get("phone_prefix", "0987")
            
            # 2. Tạo tên ngẫu nhiên (Lấy 2 tên: Họ, Tên)
            ho, ten = generate_random_name(lang)
            log(f"👤 Ngôn ngữ chọn: {lang}")
            log(f"👤 Tên tạo ra: Họ='{ho}', Tên='{ten}'")

            # 3. Tạo số điện thoại ngẫu nhiên (Tổng 10 số)
            prefixes = ['0976', '09175', '0374', '0363']
            chosen_prefix = random.choice(prefixes)
            # Tính toán số lượng chữ số còn thiếu để đủ 10 số
            random_digits_count = 10 - len(chosen_prefix)
            random_digits = "".join(str(random.randint(0, 9)) for _ in range(random_digits_count))
            phone_number = f"{chosen_prefix}{random_digits}"
            log(f"📞 SĐT mồi: {phone_number}")

            # 4. Kiểm tra xem đang ở Màn hình nào để bấm nút tương ứng
            # Có 3 trường hợp:
            # - Ở màn hình chính (Có nút "Tạo tài khoản mới")
            # - FB tự chuyển vào màn hình Giới thiệu (Có nút "Bắt đầu")
            # - FB tự chuyển thẳng vào form Điền Tên
            
            xpath_btn_tao_tai_khoan = "//*[text()='Tạo tài khoản mới' or text()='Create New Account' or @data-sigil='m_reg_button']"
            xpath_btn_bat_dau = "//*[text()='Bắt đầu' or text()='Get started']"
            
            # Cuộn sương sương như người thật
            page.mouse.wheel(0, random.randint(100, 300))
            time.sleep(random.uniform(0.5, 1.5))
            
            # --- Xử lý nút "Tạo tài khoản mới" ở Màn hình Đăng Nhập ---
            if page.locator(xpath_btn_tao_tai_khoan).is_visible():
                log("👆 Đang nhấn nút 'Tạo tài khoản mới' (Màn hình Đăng Nhập)...")
                try: 
                    page.locator(xpath_btn_tao_tai_khoan).first.click(timeout=5000)
                except:
                    try: page.locator(xpath_btn_tao_tai_khoan).first.click(force=True, timeout=3000)
                    except: pass
                log("✅ Đã nhấn Tạo tài khoản mới!")
                time.sleep(2) # Chờ load giao diện mới
            else:
                log("⏩ FB đã tự chuyển trang, bỏ qua bước nhấn 'Tạo tài khoản mới' ở Màn hình Đăng Nhập!")
            
            # --- Xử lý nút "Bắt đầu" ở Màn hình Giới Thiệu (Nếu có) ---
            if page.locator(xpath_btn_bat_dau).is_visible():
                log("👆 Đang nhấn nút 'Bắt đầu' (Màn hình Giới Thiệu)...")
                try: 
                    page.locator(xpath_btn_bat_dau).first.click(timeout=5000)
                except:
                    try: page.locator(xpath_btn_bat_dau).first.click(force=True, timeout=3000)
                    except: pass
                log("✅ Đã nhấn Bắt đầu!")
                time.sleep(2)
            else:
                log("⏩ Không thấy màn hình Giới thiệu, có thể FB đã cho thẳng vào form điền Tên!")
            
            log("✅ Xử lý xong phần nút bấm đầu vào! Chuẩn bị điền thông tin...")

            # 5. Điền Họ và Tên
            log("📝 Đang điền Họ và Tên...")
            # Các xpath phổ biến cho form nhập tên FB mobile
            xpath_ho = "//input[@name='lastname' or @aria-label='Họ' or @placeholder='Họ' or @aria-label='Last name' or @placeholder='Last name']"
            xpath_ten = "//input[@name='firstname' or @aria-label='Tên' or @placeholder='Tên' or @aria-label='First name' or @placeholder='First name']"
            
            # Nhập Họ (đợi tối đa 15s)
            input_ho = page.locator(xpath_ho).first
            try: input_ho.fill("")
            except: input_ho.evaluate("node => node.value = ''")
            input_ho.type(ho, delay=random.randint(100, 300))
            
            # Nhập Tên
            input_ten = page.locator(xpath_ten).first
            try: input_ten.fill("")
            except: input_ten.evaluate("node => node.value = ''")
            input_ten.type(ten, delay=random.randint(100, 300))
            
            log("✅ Đã điền xong họ tên!")
            
            # 6. Nhấn nút Tiếp
            log("👆 Đang nhấn nút 'Tiếp'...")
            xpath_tiep = "//*[text()='Tiếp' or text()='Next' or @name='submit']"
            btn_tiep = page.locator(xpath_tiep).first
            try:
                btn_tiep.click(timeout=4000)
            except Exception as e:
                if "Timeout" not in str(e) and "TargetClosed" not in str(e):
                    try: btn_tiep.click(force=True, timeout=3000)
                    except: pass
            log("✅ Đã nhấn Tiếp (Sau khi điền Tên)!")

            # 6.5. Kiểm tra màn hình gợi ý "Chọn tên của bạn" (Có thể có hoặc không)
            log("⏳ Đang kiểm tra xem FB có bắt xác nhận tên không (Đợi tối đa 4s)...")
            try:
                xpath_chon_ten = "//*[contains(text(), 'Chọn tên của bạn') or contains(text(), 'Choose your name')]"
                # Chỉ chờ 4 giây, nếu không có sẽ quăng exception và nhảy xuống except
                WebDriverWait(page, 4).until(EC.presence_of_element_located((By.XPATH, xpath_chon_ten)))
                
                log("⚠️ Phát hiện màn hình bắt Chọn tên! Đang chọn cái đầu tiên...")
                # Chọn radio button đầu tiên
                xpath_first_radio = "(//div[@role='radio'])[1]"
                first_radio = page.locator(xpath_first_radio).first
                try: first_radio.click(timeout=3000)
                except: first_radio.click(force=True, timeout=3000)
                
                log("👆 Đang nhấn nút 'Tiếp' (Sau khi xác nhận tên)...")
                btn_tiep_chon_ten = page.locator(xpath_tiep).first
                try:
                    btn_tiep_chon_ten.click(timeout=4000)
                except Exception as e:
                    if "Timeout" not in str(e) and "TargetClosed" not in str(e):
                        try: btn_tiep_chon_ten.click(force=True, timeout=3000)
                        except: pass
                log("✅ Đã chọn tên xong và đi tiếp!")
                
            except Exception:
                log("⏩ Không bị hỏi Chọn tên, tiếp tục quy trình...")

            # 7. Xử lý màn hình Ngày sinh
            log("⏳ Đang đợi màn hình Ngày sinh...")
            time.sleep(5) # Đợi Facebook chuyển trang/đổi giao diện
            
            log("👆 Đang nhấn nút 'Tiếp' (Ngày sinh - Lần 1)...")
            btn_tiep_ns1 = page.locator(xpath_tiep).first
            try:
                btn_tiep_ns1.click(timeout=4000)
            except Exception as e:
                if "Timeout" not in str(e) and "TargetClosed" not in str(e):
                    try: btn_tiep_ns1.click(force=True, timeout=3000)
                    except: pass
            log("✅ Đã nhấn Tiếp lần 1!")
            
            # Check if it navigated to Age screen by looking for the specific title
            xpath_age_title = "//*[contains(text(), 'bao nhiêu tuổi') or contains(text(), 'How old')]"
            
            # Chờ tối đa 5s xem màn hình Tuổi có xuất hiện không
            try:
                page.locator(xpath_age_title).wait_for(state="visible", timeout=5000)
                log("⏩ Facebook đã tự chuyển trang, bỏ qua nhấn Tiếp lần 2!")
            except:
                # Nếu sau 5s vẫn không thấy tiêu đề Tuổi, chứng tỏ bị kẹt ở Ngày sinh, bấm Tiếp Lần 2
                log("👆 Đang nhấn nút 'Tiếp' (Ngày sinh - Lần 2)...")
                btn_tiep_ns2 = page.locator(xpath_tiep).first
                try:
                    btn_tiep_ns2.click(timeout=4000)
                except Exception as e:
                    if "Timeout" not in str(e) and "TargetClosed" not in str(e):
                        try: btn_tiep_ns2.click(force=True, timeout=3000)
                        except: pass
                log("✅ Đã nhấn Tiếp lần 2!")

            # 8. Xử lý màn hình Tuổi
            log("⏳ Kiểm tra xem FB có yêu cầu nhập Tuổi không...")
            time.sleep(2)
            
            if page.locator(xpath_age_title).count() > 0:
                # FB tự động đưa con trỏ chuột vào ô Nhập Tuổi khi trang vừa load xong
                age = random.randint(20, 50)
                log(f"🎲 Tuổi ngẫu nhiên tạo ra: {age}")
                
                page.keyboard.type(str(age), delay=random.randint(100, 300))
                
                log("👆 Đang nhấn nút 'Tiếp' (Sau khi điền Tuổi)...")
                btn_tiep_age = page.locator(xpath_tiep).first
                try:
                    btn_tiep_age.click(timeout=4000)
                except Exception as e:
                    if "Timeout" not in str(e) and "TargetClosed" not in str(e):
                        try: btn_tiep_age.click(force=True, timeout=3000)
                        except: pass
                log("✅ Đã nhấn Tiếp (Qua màn hình Tuổi)!")
            else:
                log("⏩ Không thấy màn hình Tuổi, FB đã tự động bỏ qua bước này!")
            
            # 9. Xử lý hộp thoại xác nhận (Nhấn OK)
            log("⏳ Đang đợi hộp thoại xác nhận tuổi (nếu có)...")
            xpath_ok = "//*[text()='OK' or text()='Ok' or text()='ok']"
            btn_ok = page.locator(xpath_ok).first
            
            try:
                # Đợi tối đa 4 giây vì Facebook có thể không bắt xác nhận tuổi
                btn_ok.wait_for(state="visible", timeout=4000)
                log("👆 Đang nhấn nút 'OK'...")
                try: btn_ok.click(timeout=1000)
                except: btn_ok.click(force=True, timeout=1000)
                log("✅ Đã nhấn OK!")
            except Exception:
                log("⏩ Không thấy hộp thoại xác nhận tuổi, bỏ qua bước này...")

            # 10. Xử lý màn hình Giới tính
            log("⏳ Đang đợi màn hình Giới tính...")
            
            # Random giới tính
            is_male = random.choice([True, False])
            gender_vi = "Nam" if is_male else "Nữ"
            gender_en = "Male" if is_male else "Female"
            log(f"⚧ Giới tính ngẫu nhiên: {gender_vi}")
            
            # Chọn giới tính
            xpath_gender = f"//div[@role='radio' and (@aria-label='{gender_vi}' or @aria-label='{gender_en}')] | //*[text()='{gender_vi}' or text()='{gender_en}']"
            
            # CHỜ PHẦN TỬ XUẤT HIỆN
            try:
                page.locator(xpath_gender).first.wait_for(state="visible", timeout=15000)
            except:
                raise Exception("Đợi 15s nhưng màn hình Giới tính chưa hiện ra (Có thể kẹt mạng hoặc dính Checkpoint ngầm)")
                
            log(f"👆 Đang chọn giới tính '{gender_vi}'...")
            btn_gender = page.locator(xpath_gender).first
            try:
                btn_gender.click(timeout=4000)
            except Exception as e:
                if "Timeout" not in str(e) and "TargetClosed" not in str(e):
                    try: btn_gender.click(force=True, timeout=3000)
                    except: pass
            log("✅ Đã chọn giới tính!")
            
            # Nhấn Tiếp
            log("👆 Đang nhấn nút 'Tiếp' (Sau khi chọn Giới tính)...")
            btn_tiep_gender = page.locator(xpath_tiep).first
            try:
                btn_tiep_gender.click(timeout=4000)
            except Exception as e:
                if "Timeout" not in str(e) and "TargetClosed" not in str(e):
                    try: btn_tiep_gender.click(force=True, timeout=3000)
                    except: pass
            log("✅ Đã nhấn Tiếp (Qua màn hình Giới tính)!")
            
            # 11. Xử lý màn hình Số di động
            log("⏳ Đang đợi màn hình Số di động (2s)...")
            time.sleep(2)
            
            api_autosms = globals().get("api_autosms", "")
            reg_mode = globals().get("reg_mode", "hotmail")
            autosms_order_id = ""
            
            if reg_mode == "autosms" and api_autosms:
                log("[AutoSMS mode] Dang goi API thue so moi...")
                
                service_id = "facebook"
                country = "us"
                actual_key = api_autosms
                if "|" in api_autosms:
                    parts = api_autosms.split("|")
                    actual_key = parts[0]
                    if len(parts) >= 2:
                        service_id = parts[1]
                    if len(parts) >= 3:
                        country = parts[2]
                
                try:
                    res = requests.get(f"https://autosms.site/api/buy-number/{country}/{service_id}?key={actual_key}", timeout=15).json()
                    if res.get("success"):
                        phone_number = res["data"]["phone"]
                        autosms_order_id = res["data"]["order_id"]
                        log(f"Da thue so AutoSMS: {phone_number} (Ma don: {autosms_order_id})")
                        if monitor and pid:
                            monitor.upsert(pid, mail=phone_number)
                    else:
                        raise Exception(f"AutoSMS loi thue so: {res.get('message')}")
                except Exception as e:
                    raise Exception(f"Loi API AutoSMS: {e}")
            
            if phone_number:
                # CHỜ PHẦN TỬ XUẤT HIỆN
                try:
                    phone_input = page.locator("input[type='tel'], input[name='reg_email__'], input[type='email']").first
                    phone_input.wait_for(state="visible", timeout=15000)
                    log(f"📝 Đang điền Số điện thoại: {phone_number}...")
                    phone_input.fill(phone_number, timeout=5000)
                    log("✅ Đã điền Số di động!")
                except Exception as e:
                    raise Exception(f"Không tìm thấy ô điền Số di động sau 15s: {e}")
                
                # Nhấn Tiếp
                log("👆 Đang nhấn nút 'Tiếp' (Sau khi điền SĐT)...")
                btn_tiep_phone = page.locator(xpath_tiep).first
                try:
                    btn_tiep_phone.click(timeout=4000)
                except Exception as e:
                    if "Timeout" not in str(e) and "TargetClosed" not in str(e):
                        try: btn_tiep_phone.click(force=True, timeout=3000)
                        except: pass
                log("✅ Đã nhấn Tiếp (Qua màn hình Số di động)!")
            else:
                log("⚠️ Không có SĐT mồi. Nếu bạn dùng Email, hãy tự thêm code xử lý đoạn này.")
            
            # 15. Màn hình Chọn phương thức SMS
            log("⏳ Đang xử lý màn hình Xác nhận số di động...")
            time.sleep(2)
            
            xpath_sms_radio = "//*[text()='Gửi mã qua SMS' or contains(text(), 'Send via SMS')]"
            try:
                # Tìm element và chờ tối đa 5 giây để Facebook render xong
                sms_radio = page.locator(xpath_sms_radio).first
                sms_radio.wait_for(state="visible", timeout=5000)
                log("👆 Đang chọn 'Gửi mã qua SMS'...")
                try: sms_radio.click(timeout=3000)
                except: sms_radio.click(force=True, timeout=3000)
                
                # Nhấn Tiếp tục
                xpath_tiep_tuc = "//*[text()='Tiếp tục' or text()='Continue']"
                btn_tiep_tuc = page.locator(xpath_tiep_tuc).first
                btn_tiep_tuc.wait_for(state="visible", timeout=3000)
                log("👆 Đang nhấn 'Tiếp tục' (Gửi SMS)...")
                try:
                    btn_tiep_tuc.click(timeout=4000)
                except Exception as e:
                    if "Timeout" not in str(e) and "TargetClosed" not in str(e):
                        try: btn_tiep_tuc.click(force=True, timeout=3000)
                        except: pass
                log("✅ Đã gửi yêu cầu mã SMS!")
                time.sleep(5)
            except Exception as e:
                log("⚠️ Không thấy màn hình chọn SMS, có thể Facebook đã tự bỏ qua trang này.")

            # 12. Xử lý màn hình Tạo mật khẩu
            log("⏳ Đang đợi màn hình Tạo mật khẩu...")
            
            import string
            # Chỉ chứa chữ hoa, chữ thường và số (không ký tự đặc biệt, không dấu cách)
            chars = string.ascii_letters + string.digits
            password = "".join(random.choice(chars) for _ in range(20))
            log(f"🔑 Mật khẩu ngẫu nhiên: {password}")
            if monitor and pid:
                monitor.upsert(pid, passwd=password)
            
            # CHỜ PHẦN TỬ XUẤT HIỆN
            try:
                pass_input = page.locator("input[type='password'], input[name='reg_passwd__']").first
                pass_input.wait_for(state="visible", timeout=15000)
                pass_input.fill(password, timeout=5000)
                log("✅ Đã điền Mật khẩu!")
            except Exception as e:
                raise Exception(f"Không tìm thấy ô điền Mật Khẩu sau 15s (Có thể FB chặn SĐT mồi hoặc chặn IP!): {e}")
            
            # Nhấn Tiếp
            log("👆 Đang nhấn nút 'Tiếp' (Sau khi điền Mật khẩu)...")
            btn_tiep_pass = page.locator(xpath_tiep).first
            try:
                btn_tiep_pass.click(timeout=4000)
            except Exception as e:
                if "Timeout" not in str(e) and "TargetClosed" not in str(e):
                    try: btn_tiep_pass.click(force=True, timeout=3000)
                    except: pass
            log("✅ Đã nhấn Tiếp (Qua màn hình Tạo mật khẩu)!")

            # 13. Màn hình Lưu thông tin đăng nhập
            log("⏳ Đang đợi màn hình Lưu thông tin...")
            time.sleep(5)
            xpath_luc_khac = "//*[text()='Lúc khác' or text()='Not Now' or text()='Not now']"
            btn_luc_khac = page.locator(xpath_luc_khac).first
            log("👆 Đang nhấn 'Lúc khác'...")
            try:
                btn_luc_khac.click(timeout=4000)
            except Exception as e:
                if "Timeout" not in str(e) and "TargetClosed" not in str(e):
                    try: btn_luc_khac.click(force=True, timeout=3000)
                    except: pass
            log("✅ Đã nhấn Lúc khác!")

            # 14. Màn hình Điều khoản & Chính sách (Tôi đồng ý)
            log("⏳ Đang đợi màn hình Điều khoản (Tối đa 10s)...")
            
            # Kiem tra xem FB co bo qua trang nay ma nhay thang sang SMS khong
            if page.locator("text=/xác nhận số|xác nhận email|gửi mã|nhập mã|không nhận được mã|send code|enter code/i").count() > 0:
                log("⏩ Facebook đã tự bỏ qua màn hình Điều khoản, đi tiếp...")
            else:
                xpath_dong_y = "//*[text()='Tôi đồng ý' or text()='I agree' or text()='I Agree' or text()='TÔI ĐỒNG Ý']"
                btn_dong_y = page.locator(xpath_dong_y).first
                
                try:
                    # Đợi phần tử xuất hiện tối đa 10 giây
                    btn_dong_y.wait_for(state="visible", timeout=10000)
                    log("👆 Đang xử lý vòng lặp 'Tôi đồng ý'...")
                    
                    navigated = False
                    for attempt in range(5): # Tối đa 5 vòng lặp * 5s = 25 giây
                        # 1. Kiểm tra xem đã qua màn hình SMS chưa
                        sms_regex = "text=/xác nhận|gửi mã|nhập mã|không nhận được mã|send code|enter code|xác nhận số|xác nhận email/i"
                        if page.locator(sms_regex).count() > 0 and page.locator(sms_regex).first.is_visible():
                            log("✅ Đã chuyển sang màn hình SMS/Email thành công!")
                            navigated = True
                            break
                            
                        # 2. Kiểm tra xem nút Tôi đồng ý có đang nằm chình ình trên màn hình không
                        import re
                        btn_dong_y_current = page.locator("button, div[role='button'], div.native-text, span").filter(has_text=re.compile(r"^(Tôi đồng ý|I agree)$", re.IGNORECASE))
                        if btn_dong_y_current.count() > 0 and btn_dong_y_current.first.is_visible():
                            log("👆 Phát hiện nút 'Tôi đồng ý', tiến hành nhấn...")
                            try:
                                btn_dong_y_current.first.click(timeout=3000)
                            except Exception as e:
                                if "Timeout" not in str(e) and "TargetClosed" not in str(e):
                                    try: btn_dong_y_current.first.click(force=True, timeout=3000)
                                    except: pass
                        else:
                            log(f"⏳ Nút đang ẩn/đang xoay, tiếp tục chờ 5s... (Vòng lặp {attempt+1}/5)")
                            
                        # 3. Chờ 5 giây rồi vòng lại để kiểm tra
                        time.sleep(5)
                        
                    if not navigated:
                        log("❌ Lỗi: Chờ quá thời gian (25s) nhưng không qua được trang Điều khoản!")
                        raise Exception("lỗi nhấn tôi đồng ý")
                        
                except Exception as e:
                    if str(e) == "lỗi nhấn tôi đồng ý":
                        raise e
                    log(f"❌ Lỗi: Không tìm thấy nút 'Tôi đồng ý' hoặc có sự cố: {e}")
                    raise Exception("Không tìm thấy nút Tôi đồng ý")
                

            # 15. Man hinh Chon phuong thuc SMS hoac Nhap ma SMS
            log("Dang xu ly man hinh Xac nhan/Nhap ma...")
            time.sleep(2)
            
            if reg_mode == "autosms" and autosms_order_id:
                # Da nhap so that, gio cho SMS OTP
                log("[AutoSMS mode] Dang cho SMS OTP tu autosms.site (Toi da 120s)...")
                otp_code = ""
                for _i in range(30):
                    time.sleep(4)
                    try:
                        actual_key = api_autosms.split("|")[0] if "|" in api_autosms else api_autosms
                        _resp = requests.get(f"https://autosms.site/api/orders/{autosms_order_id}?key={actual_key}", timeout=10).json()
                        if _resp.get("success") and _resp.get("data", {}).get("code"):
                            otp_code = _resp["data"]["code"]
                            break
                    except: pass
                
                if otp_code:
                    log(f"Da nhan duoc SMS OTP: {otp_code}")
                    # Dien vao form OTP hien tai
                    xpath_sms_input = "//input[@type='text' or @type='number' or @inputmode='numeric' or @name='n']"
                    try:
                        page.locator(xpath_sms_input).first.fill(otp_code)
                    except:
                        log("⚠️ Khong tim thay o nhap OTP, thu bam gui ma roi nhap lai...")
                        # Thuc te Facebook da gui roi
                    
                    # Nhan Tiep tuc de xac nhan
                    xpath_tiep_tuc = "//*[text()='Tiếp tục' or text()='Continue' or text()='Tiếp' or text()='Xác nhận']"
                    btn_tiep_tuc = page.locator(xpath_tiep_tuc).first
                    try: btn_tiep_tuc.click(timeout=3000)
                    except:
                        try: btn_tiep_tuc.click(force=True, timeout=3000)
                        except: pass
                    log("Da xac nhan SMS OTP!")
                    time.sleep(10) # Chờ chuyển hướng trang
                else:
                    log("AutoSMS timeout, dang huy don hang...")
                    actual_key = api_autosms.split("|")[0] if "|" in api_autosms else api_autosms
                    try: requests.get(f"https://autosms.site/api/cancel/{autosms_order_id}?key={actual_key}", timeout=10)
                    except: pass
                    raise Exception("Khong nhan duoc SMS OTP tu AutoSMS")
            else:
                # Neu chon Email hoac khong co so that
                # Neu co nut SMS radio, nghia la dang o trang 'Chon phuong thuc'
                xpath_sms_radio = "//*[text()='Gửi mã qua SMS' or contains(text(), 'Send via SMS')]"
                radio_elems = page.locator(xpath_sms_radio).all()
                if any(el.is_visible() for el in radio_elems):
                    log("⏳ Đang đợi và chọn 'Gửi mã qua SMS'...")
                    for el in radio_elems:
                        if el.is_visible():
                            try:
                                el.click(timeout=3000)
                            except:
                                try: el.click(force=True, timeout=3000)
                                except: pass
                            break
                    
                    # Nhan Tiep tuc
                    xpath_tiep_tuc = "//*[text()='Tiếp tục' or text()='Continue']"
                    btn_tiep_tuc = page.locator(xpath_tiep_tuc).first
                    log("⏳ Đang đợi nút 'Tiếp tục' (Gửi SMS) (Tối đa 10s)...")
                    try:
                        btn_tiep_tuc.wait_for(state="visible", timeout=10000)
                        log("👆 Đang nhấn 'Tiếp tục'...")
                        try:
                            btn_tiep_tuc.click(timeout=3000)
                        except Exception as e:
                            if "Timeout" not in str(e) and "TargetClosed" not in str(e):
                                try: btn_tiep_tuc.click(force=True, timeout=3000)
                                except: pass
                        log("✅ Đã gửi yêu cầu mã SMS!")
                        time.sleep(5)
                    except Exception:
                        log("⚠️ Không thấy nút Tiếp tục, có thể đã qua trang.")
                
                # 16. Man hinh Nhap ma xac nhan SMS
                # Nhan 'Toi khong nhan duoc ma' de chuyen sang Email
                xpath_ko_nhan_ma = "//*[text()='Tôi không nhận được mã' or contains(text(), 'didn') or contains(text(), 'not get the code')]"
                btn_ko_nhan_ma = page.locator(xpath_ko_nhan_ma).first
                log("⏳ Đang đợi nút 'Tôi không nhận được mã' (Tối đa 10s)...")
                try:
                    btn_ko_nhan_ma.wait_for(state="visible", timeout=10000)
                    log("👆 Đang nhấn 'Tôi không nhận được mã'...")
                    try:
                        btn_ko_nhan_ma.click(timeout=3000)
                    except Exception as e:
                        if "Timeout" not in str(e) and "TargetClosed" not in str(e):
                            try: btn_ko_nhan_ma.click(force=True, timeout=3000)
                            except: pass
                except Exception:
                    log("⚠️ Không tìm thấy nút 'Tôi không nhận được mã', có thể Facebook đã bỏ qua màn hình SMS.")
            
            if not (reg_mode == "autosms" and autosms_order_id):
                # 17. Popup chon phuong thuc thay thu (Neu khong dung AutoSMS)
                log("⏳ Đang đợi popup chọn phương thức xác nhận thay thế (Tối đa 10s)...")
                xpath_xac_nhan_email = "//*[text()='Xác nhận bằng email' or contains(text(), 'Confirm by email')]"
                btn_xac_nhan_email = page.locator(xpath_xac_nhan_email).first
                
                try:
                    btn_xac_nhan_email.wait_for(state="visible", timeout=10000)
                    log("👆 Đang chọn 'Xác nhận bằng email'...")
                    try:
                        btn_xac_nhan_email.click(timeout=3000)
                    except Exception as e:
                        if "Timeout" not in str(e) and "TargetClosed" not in str(e):
                            try: btn_xac_nhan_email.click(force=True, timeout=3000)
                            except: pass
                except Exception:
                    log("⚠️ Quá 10 giây không thấy popup Xác nhận bằng email, có thể FB đã cho nhập email luôn.")
                
                # 18. Man hinh Nhap Email
                log("Dang doi man hinh Nhap email...")
                time.sleep(5)
            
            api_dongvan     = globals().get("api_dongvan", "")
            api_gmail       = globals().get("api_gmail", "")
            api_shopmailmmo = globals().get("api_shopmailmmo", "")
            api_mijcloud    = globals().get("api_mijcloud", "")
            dv_account      = globals().get("dv_account", "1")
            reg_mode        = globals().get("reg_mode", "hotmail")
            shared_state    = globals().get("shared_state", {})
            email = ""
            order_id = ""
            
            if not (reg_mode == "autosms" and autosms_order_id):
                if reg_mode == "gmail" and api_gmail:
                    if shared_state.get("gmail_email") and shared_state.get("gmail_order_id"):
                        email = shared_state["gmail_email"]
                        order_id = shared_state["gmail_order_id"]
                        log(f"[Gmail mode] Tái sử dụng Gmail từ nick trước: {email} (Ma don: {order_id})")
                        if monitor and pid: monitor.upsert(pid, mail=email)
                    else:
                        log("[Gmail mode] Dang goi API lay Gmail tu shopgmail9999...")
                        api_create_url = f"https://api.shopgmail9999.com/api/ApiV2/CreateOrder?apikey={api_gmail}&service=facebook"
                        try:
                            res = requests.get(api_create_url, timeout=15).json()
                            if res.get("status") == "success":
                                email = res["data"]["email"]
                                order_id = res["data"]["orderid"]
                                log(f"Da lay Gmail: {email} (Ma don: {order_id})")
                                shared_state["gmail_email"] = email
                                shared_state["gmail_order_id"] = order_id
                                if monitor and pid:
                                    monitor.upsert(pid, mail=email)
                            else:
                                log(f"Loi API Gmail: {res.get('msg')}")
                        except Exception as e:
                            log(f"Loi ket noi API Gmail: {e}")
                elif reg_mode == "shopmail" and api_shopmailmmo:
                    if shared_state.get("shopmail_email") and shared_state.get("shopmail_order_id"):
                        email = shared_state["shopmail_email"]
                        order_id = shared_state["shopmail_order_id"]
                        log(f"[ShopMailMMO mode] Tái sử dụng Mail từ nick trước: {email} (Ma don: {order_id})")
                        if monitor and pid: monitor.upsert(pid, mail=email)
                    else:
                        log("[ShopMailMMO mode] Dang goi API lay mail tu shopmailmmo.store...")
                        api_create_url = f"https://shopmailmmo.store/v1/orders?service=facebook"
                        try:
                            res = requests.post(api_create_url, headers={'api_key': api_shopmailmmo}, timeout=15)
                            if res.status_code == 200:
                                data = res.json()
                                if data.get("status") == "fail" or not data.get("mail"):
                                    log(f"Loi API ShopMailMMO: {data.get('error', 'Loi khong xac dinh')}")
                                else:
                                    email = data.get("mail")
                                    order_id = data.get("order_id")
                                    log(f"Da lay ShopMailMMO: {email} (Ma don: {order_id})")
                                    shared_state["shopmail_email"] = email
                                    shared_state["shopmail_order_id"] = order_id
                                    if monitor and pid:
                                        monitor.upsert(pid, mail=email)
                            else:
                                msg = res.text
                                try: msg = res.json().get('error', msg)
                                except: pass
                                log(f"Loi API ShopMailMMO: {res.status_code} - {msg}")
                        except Exception as e:
                            log(f"Loi ket noi API ShopMailMMO: {e}")
                elif reg_mode == "mijcloud":
                    api_mijcloud = globals().get("api_mijcloud", "")
                    m_key = api_mijcloud.strip()
                    m_id = "183" # Hardcoded default as per user request
                    log(f"[MijCloud mode] Dang goi API MUA Hotmail (ID: {m_id}) tu MijCloud...")
                    api_buy_url = f"https://mijcloud.com/api/buy_product?action=buyProduct&id={m_id}&amount=1&api_key={m_key}"
                    try:
                        res = requests.get(api_buy_url, timeout=15).json()
                        if res.get("status") == "success":
                            list_data = res.get("data", [])
                            if list_data:
                                parts = list_data[0].split('|')
                                email = parts[0]
                                email_pass = parts[1] if len(parts) > 1 else ""
                                log(f"Da MUA Hotmail MijCloud: {email} (Pass: {email_pass})")
                                if monitor and pid:
                                    monitor.upsert(pid, mail=email)
                            else:
                                log("API MijCloud: Khong co tai khoan tra ve (het hang)")
                        else:
                            log(f"Loi API mua MijCloud: {res.get('msg')}")
                    except Exception as e:
                        log(f"Loi ket noi API MijCloud: {e}")
                elif reg_mode == "hotmail" and api_dongvan:
                    if "|" in api_dongvan:
                        dv_key, dv_acc = api_dongvan.split("|", 1)
                    else:
                        dv_key, dv_acc = api_dongvan, "1"
                    log(f"[Hotmail mode] Dang goi API MUA Hotmail (ID: {dv_acc}) tu dongvanfb...")
                    api_buy_url = f"https://api.dongvanfb.net/user/buy?apikey={dv_key}&account_type={dv_acc}&quantity=1&type=full"
                    try:
                        res = requests.get(api_buy_url, timeout=15).json()
                        if res.get("status") == True:
                            list_data = res.get("data", {}).get("list_data", [])
                            if list_data:
                                parts = list_data[0].split('|')
                                email = parts[0]
                                email_pass = parts[1] if len(parts) > 1 else ""
                                refresh_token = parts[2] if len(parts) > 2 else ""
                                client_id = parts[3] if len(parts) > 3 else ""
                                globals()["dv_refresh_token"] = refresh_token
                                globals()["dv_client_id"] = client_id
                                log(f"Da MUA Hotmail: {email} (Pass: {email_pass})")
                                if monitor and pid:
                                    monitor.upsert(pid, mail=email)
                            else:
                                log("API dongvanfb: Khong co tai khoan tra ve (het hang HotMail)")
                        else:
                            log(f"Loi API mua Hotmail: {res.get('message')}")
                    except Exception as e:
                        log(f"Loi ket noi API dongvanfb: {e}")
                elif reg_mode == "reg_mail_ao":
                    log("[Reg Mail Ảo mode] Dang tao Mail ao ngau nhien tu hunght1890.com...")
                    time.sleep(3) # Delay de mo phong thoi gian load trang giong Gmail API
                    random_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
                    email = f"{random_str}@hunght1890.com"
                    log(f"Da tao Reg Mail Ảo: {email}")
                    if monitor and pid:
                        monitor.upsert(pid, mail=email)
                else:
                    log("Chua nhap API Key. Hay dien API DongvanFB hoac API Gmail vao bang dieu khien!")
                
                if not email:
                    raise Exception("Khong lay duoc Email moi tu API")
                
                # Dien Email
                log(f"📝 Đang nhập Email: {email}...")
                xpath_email_input = "input[type='email'], input[name='email'], input[type='text'], input[name='reg_email__']"
                try:
                    email_input = page.locator(xpath_email_input).last
                    email_input.wait_for(state="visible", timeout=15000)
                    email_input.fill(email, timeout=5000)
                    log("✅ Đã điền Email mới!")
                except Exception as e:
                    raise Exception(f"Không tìm thấy ô nhập Email sau 15s: {e}")
                
                # Nhan Tiep (Cách đặc biệt cho màn hình Email)
                log("⏳ Đang đợi nút 'Tiếp/Thêm' (Gửi email)...")
                try:
                    # Chờ 1 giây để ReactJS kịp nhận diện email vừa gõ xong
                    time.sleep(1)
                    
                    # KIỂM TRA MÀN HÌNH CHỌN PROFILE CỦA META ACCOUNTS CENTER (GIAO DIỆN MỚI FB)
                    try:
                        xpath_profile_cb = "input[type='checkbox'], input[type='radio'], div[role='checkbox'], div[role='radio']"
                        profile_cbs = page.locator(xpath_profile_cb).locator("visible=true")
                        if profile_cbs.count() > 0:
                            cb = profile_cbs.first
                            aria_checked = cb.get_attribute("aria-checked")
                            is_checked = cb.is_checked() if cb.evaluate("el => el.tagName === 'INPUT'") else (aria_checked == "true")
                            
                            if not is_checked:
                                log("⚠️ Phát hiện FB bắt chọn tài khoản liên kết! Đang tick chọn Profile...")
                                try: cb.click(timeout=2000)
                                except: pass
                                
                                time.sleep(1.5)
                                aria_checked_now = cb.get_attribute("aria-checked")
                                is_checked_now = cb.is_checked() if cb.evaluate("el => el.tagName === 'INPUT'") else (aria_checked_now == "true")
                                
                                if not is_checked_now:
                                    try: cb.click(force=True, timeout=2000)
                                    except: pass
                    except Exception:
                        pass
                        
                    # Quét toàn bộ các nút Tiếp/Thêm
                    xpath_tiep_them = "button, div[role='button']"
                    btn_them = page.locator(xpath_tiep_them).filter(has_text=re.compile(r"^(Tiếp|Next|Thêm|Add|Tiếp tục|Continue)$", re.IGNORECASE)).locator("visible=true")
                    btn_them.first.wait_for(state="visible", timeout=10000)
                    
                    log("👆 Đang nhấn 'Tiếp/Thêm'...")
                    try:
                        btn_them.first.click(timeout=3000)
                    except Exception:
                        try: btn_them.first.click(force=True, timeout=3000)
                        except: pass
                        
                    log("✅ Đã click yêu cầu mã Email!")
                except Exception as e:
                    log(f"⚠️ Lỗi khi bấm nút Tiếp/Thêm: {e}")
                
                # 19. Doi ma xac nhan OTP tu API
                log("Dang cho he thong nha ma OTP (Toi da 120s)...")
                otp_code = ""
                
                if reg_mode == "gmail" and api_gmail and order_id:
                    log("[Gmail mode] Dang poll OTP tu shopgmail9999...")
                    _check_url = f"https://api.shopgmail9999.com/api/ApiV2/CheckOtp2?apikey={api_gmail}&orderid={order_id}"
                    for _i in range(30):
                        time.sleep(4)
                        try:
                            _resp = requests.get(_check_url, timeout=10).json()
                            _data = _resp.get("data", {})
                            if _data.get("status") == "success" and _data.get("otp"):
                                raw_otp = str(_data["otp"])
                                import re
                                codes = re.findall(r'\d{5,8}', raw_otp)
                                new_code = None
                                used_otps = shared_state.setdefault("used_otps", [])
                                for c in reversed(codes):
                                    if c not in used_otps:
                                        new_code = c
                                        break
                                if new_code:
                                    otp_code = new_code
                                    used_otps.append(otp_code)
                                    break
                            elif _resp.get("status") == "error" and "pending" not in str(_resp.get("msg", "")).lower():
                                log(f"API Gmail bao loi OTP: {_resp.get('msg')}")
                        except Exception:
                            pass
                            
                elif reg_mode == "shopmail" and api_shopmailmmo and order_id:
                    log("[ShopMailMMO mode] Dang poll OTP tu shopmailmmo.store...")
                    _check_url = f"https://shopmailmmo.store/v1/otp?id={order_id}"
                    for _i in range(30):
                        time.sleep(6) # Delay 6s according to their API docs pattern
                        try:
                            _resp = requests.post(_check_url, headers={'api_key': api_shopmailmmo}, timeout=10)
                            if _resp.status_code == 200:
                                data = _resp.json()
                                otp = data.get("otp")
                                if otp and str(otp).strip():
                                    raw_otp = str(otp)
                                    import re
                                    codes = re.findall(r'\d{5,8}', raw_otp)
                                    new_code = None
                                    used_otps = shared_state.setdefault("used_otps", [])
                                    for c in reversed(codes):
                                        if c not in used_otps:
                                            new_code = c
                                            break
                                    if new_code:
                                        otp_code = new_code
                                        used_otps.append(otp_code)
                                        break
                            elif _resp.status_code not in (500, 502, 503, 504):
                                msg = _resp.inner_text()
                                try: msg = _resp.json().get('error', msg)
                                except: pass
                                log(f"API ShopMailMMO bao loi OTP ({_resp.status_code}): {msg}")
                        except Exception:
                            pass
                            
                elif reg_mode in ["hotmail", "mijcloud"] and api_dongvan and email:
                    _refresh = globals().get("dv_refresh_token", "")
                    _client  = globals().get("dv_client_id", "")
                    
                    if _refresh and _client:
                        log("[Hotmail mode] Dung Graph API DongvanFB de lay OTP...")
                        _payload = {"email": email, "refresh_token": _refresh,
                                   "client_id": _client, "type": "facebook"}
                        for _i in range(30):
                            time.sleep(4)
                            try:
                                _resp = requests.post("https://tools.dongvanfb.net/api/graph_code",
                                                      json=_payload, timeout=10).json()
                                if _resp.get("status") == True and _resp.get("code"):
                                    raw_otp = str(_resp["code"])
                                    import re
                                    codes = re.findall(r'\d{5,8}', raw_otp)
                                    new_code = None
                                    used_otps = shared_state.setdefault("used_otps", [])
                                    for c in reversed(codes):
                                        if c not in used_otps:
                                            new_code = c
                                            break
                                    if new_code:
                                        otp_code = new_code
                                        used_otps.append(otp_code)
                                        break
                            except Exception:
                                pass
                    else:
                        log("[Hotmail mode] Dung get_code_facebook de lay OTP (acc khong co token)...")
                        dv_key = api_dongvan.split("|")[0] if "|" in api_dongvan else api_dongvan
                        _check_url = f"https://api.dongvanfb.net/user/get_code_facebook?apikey={dv_key}&email={email}"
                        for _i in range(30):
                            time.sleep(4)
                            try:
                                _resp = requests.get(_check_url, timeout=10).json()
                                if _resp.get("status") == True and _resp.get("code"):
                                    raw_otp = str(_resp["code"])
                                    import re
                                    codes = re.findall(r'\d{5,8}', raw_otp)
                                    new_code = None
                                    used_otps = shared_state.setdefault("used_otps", [])
                                    for c in reversed(codes):
                                        if c not in used_otps:
                                            new_code = c
                                            break
                                    if new_code:
                                        otp_code = new_code
                                        used_otps.append(otp_code)
                                        break
                            except Exception:
                                pass
                elif reg_mode == "reg_mail_ao" and email:
                    log("[Reg Mail Ảo mode] Dang cho OTP tu hunght1890.com (Toi da 120s)...")
                    _url = f"https://hunght1890.com/{email}"
                    for _i in range(30):
                        time.sleep(4)
                        try:
                            _r = requests.get(_url, timeout=10)
                            if _r.status_code == 200:
                                _data = _r.json()
                                if isinstance(_data, list) and len(_data) > 0:
                                    import re
                                    used_otps = shared_state.setdefault("used_otps", [])
                                    new_code = None
                                    for msg_data in _data:
                                        subject = msg_data.get("subject", "")
                                        body = msg_data.get("body", "")
                                        
                                        # 1. Ưu tiên lấy từ Tiêu đề (FB-xxxx hoặc 5,6 số)
                                        match = re.search(r'FB-(\d{5,6})', subject)
                                        if not match: match = re.search(r'(?<!\d)(\d{5,6})(?!\d)', subject)
                                        
                                        if match:
                                            c = match.group(1)
                                            if c not in used_otps:
                                                new_code = c
                                                break
                                                
                                        # 2. Nếu tiêu đề không có, quét cẩn thận trong body
                                        codes = re.findall(r'FB-(\d{5,6})', body)
                                        if not codes: codes = re.findall(r'(?<!\d)(\d{5,6})(?!\d)', body)
                                        for c in reversed(codes):
                                            if c not in used_otps:
                                                new_code = c
                                                break
                                        if new_code: break
                                    if new_code:
                                        otp_code = new_code
                                        used_otps.append(otp_code)
                                        break
                        except Exception:
                            pass
                else:
                    log("Khong xac dinh duoc nguon OTP. Kiem tra lai reg_mode va API key!")
                    
                if not otp_code:
                    raise Exception("Khong nhan duoc ma OTP sau 120s!")
                    
                log(f"Da nhan OTP: {otp_code}")
                
                # 20. Dien ma xac nhan (OTP)
                log("⏳ Đang đợi màn hình Nhập mã xác nhận (OTP)...")
                
                try:
                    time.sleep(2) # Chờ popup render
                    xpath_otp_input = "input[name='ncode'], input[name='code'], input[type='number'], input[type='text']"
                    otp_input = page.locator(xpath_otp_input).filter(visible=True).last
                    
                    otp_input.wait_for(state="visible", timeout=15000)
                    otp_input.focus()
                    
                    # Thử clear và type từng chữ để React nhận diện
                    try: otp_input.fill("")
                    except: pass
                    otp_input.type(otp_code, delay=random.randint(50, 150))
                    log("✅ Đã điền mã OTP (Locator Last)!")
                except Exception as e:
                    raise Exception(f"Không tìm thấy ô nhập OTP sau 15s: {e}")
                
                # Nhan Tiep tuc
                log("Dang nhan nut 'Tiếp' (Hoan tat OTP)...")
                xpath_tiep_otp = "button, div[role='button']"
                btn_tiep_otp = page.locator(xpath_tiep_otp).filter(has_text=re.compile(r"^(Tiếp|Next|Tiếp tục|Continue|Xác nhận|Confirm|Gửi|Submit)$", re.IGNORECASE)).filter(visible=True)
                try:
                    btn_tiep_otp.last.wait_for(state="visible", timeout=10000)
                    btn_tiep_otp.last.click(timeout=4000)
                except Exception as e:
                    log("⚠️ Không tìm thấy nút Tiếp OTP, gõ Enter để vượt rào...")
                    page.keyboard.press("Enter")
                log("Da xac nhan OTP hoan tat!")
            
            # --- KIEM TRA TRANG THAI SAU KHI DIEN OTP ---
            log("⏳ Đợi Facebook xử lý OTP và chuyển trang (Tối đa 25s)...")
            try:
                current_url_before = page.url
                page.wait_for_url(lambda u: u.split('?')[0] != current_url_before.split('?')[0], timeout=25000)
                log("✅ Facebook đã chuyển trang thành công!")
            except Exception:
                log("⚠️ Quá thời gian chờ chuyển trang (Có thể bị kẹt hoặc chuyển ngầm).")
            
            # Kiem tra SUCCESS truoc (tranh false positive khi DOM con OTP field an)
            is_stuck = False
            try:
                cur_url   = page.url.lower()
                body_text = page.locator("body").inner_text().lower()
                
                success_urls  = ["welcome", "home", "feed", "story", "/profile", "/groups"]
                success_texts = ["chào mừng", "welcome to", "trang chủ", "bạn bè", "news feed", "tin tức"]
                
                if any(s in cur_url for s in success_urls):
                    log("URL chuyen sang trang thanh cong -> OTP duoc chap nhan!")
                elif any(s in body_text for s in success_texts):
                    log("Trang hien thi noi dung thanh cong -> OTP duoc chap nhan!")
                else:
                    try:
                        otp_elem = page.locator(xpath_otp_input).first
                        if otp_elem.is_visible():
                            try:
                                xpath_err = "//*[contains(text(), 'không hợp lệ') or contains(text(), 'invalid') or contains(text(), 'Incorrect') or contains(text(), 'sai') or contains(text(), 'wrong')]"
                                err_elem = page.locator(xpath_err).first
                                if err_elem.is_visible():
                                    is_stuck = True
                                    log(f"Facebook bao ma sai: {err_elem.inner_text()[:80]}")
                            except:
                                is_stuck = True
                    except: pass
            except: pass
            
            if is_stuck:
                log("That bai: Ma OTP sai hoac bi ket o buoc nhap code!")
                if monitor and pid: monitor.set_status(pid, "Loi OTP")
                raise Exception("Ket o man hinh nhap code OTP")
                
            # 2. Kiem tra tai khoan Live hay Checkpoint (Die)
            log("⏳ Kiem tra tai khoan (Live hay Checkpoint)...")
            # Đợi một chút để Facebook render giao diện Checkpoint hoặc Welcome
            time.sleep(3)
            
            current_url = page.url.lower()
            try:
                page_text = page.locator("body").inner_text().lower()
            except:
                page_text = ""
                
            is_die = False
            if "checkpoint" in current_url:
                is_die = True
            else:
                die_keywords = ["vô hiệu hóa", "disabled", "đình chỉ", "suspended", "tải ảnh của bạn lên", "upload a photo", "vi phạm", "tiêu chuẩn cộng đồng"]
                if any(kw in page_text for kw in die_keywords):
                    is_die = True
                    
            if is_die:
                log("THAT BAI: Tai khoan vua tao da bi CHECKPOINT (Die)!")
                if monitor and pid: monitor.set_status(pid, "Checkpoint")
                raise Exception("Tài khoản bị Checkpoint ngay khi tạo")
            else:
                log("THANH CONG: Tai khoan da duoc tao va dang LIVE!")
                
                # Lay Cookie va UID
                cookies = page.context.cookies()
                cookie_str = "; ".join([f"{c['name']}={c['value']}" for c in cookies])
                
                uid = ""
                for c in cookies:
                    if c['name'] == 'c_user':
                        uid = c['value']
                        break
                        
                if monitor and pid: 
                    monitor.set_status(pid, "Live")
                    monitor.upsert(pid, uid=uid, cookie=cookie_str)
                    
                # --- THEM HOTMAIL BAO MAT VAO TAI KHOAN (HARDENING) ---
                if reg_mode in ("autosms", "reg_mail_ao"):
                    log(f"[{reg_mode} mode] Bỏ qua bước bọc Mail bảo mật, chuyển thẳng sang cài 2FA...")
                elif reg_mode in ("gmail", "shopmail"):
                    log("[Gmail/ShopMailMMO mode] Bat dau them Mail bao mat vao Facebook (hunght1890.com)...")
                    try:
                        page.goto("https://accountscenter.facebook.com/personal_info/contact_points")
                        
                        # 1. Click "Them thong tin lien he moi"
                        log("⏳ Đang đợi màn hình Thêm thông tin liên hệ mới...")
                        xpath_add_contact = "//*[contains(text(), 'Thêm thông tin liên hệ mới') or contains(text(), 'Add new contact')]"
                        btn_add_contact = page.locator(xpath_add_contact).first
                        btn_add_contact.wait_for(state="visible", timeout=15000)
                        
                        try:
                            btn_add_contact.click(timeout=4000)
                        except Exception as e:
                            if "Timeout" not in str(e) and "TargetClosed" not in str(e):
                                try: btn_add_contact.click(force=True, timeout=3000)
                                except: pass
                        log("Da click 'Thêm thông tin liên hệ mới'")
                        time.sleep(2)
                        
                        # 2. Click "Them email"
                        xpath_add_email = "//*[contains(text(), 'Thêm email') or contains(text(), 'Add email')]"
                        btn_add_email = page.locator(xpath_add_email).first
                        try:
                            btn_add_email.click(timeout=4000)
                        except Exception as e:
                            if "Timeout" not in str(e) and "TargetClosed" not in str(e):
                                try: btn_add_email.click(force=True, timeout=3000)
                                except: pass
                        log("Da click 'Thêm email'")
                        time.sleep(3)
                        
                        # 3. Tao Mail ao ngau nhien tu hunght1890.com
                        log("Dang tao Mail ao bao mat tu hunght1890.com...")
                        random_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
                        sec_mail = f"{random_str}@hunght1890.com"
                        log(f"Da tao Mail bao mat: {sec_mail}")
                        
                        # 4. Dien Hotmail bao mat vao form Facebook
                        page.evaluate("""
                            (sec_mail) => {
                                var inputs = Array.from(document.querySelectorAll('input')).filter(
                                    i => i.offsetParent !== null && i.type !== 'hidden' && i.type !== 'submit'
                                    && i.type !== 'checkbox' && i.type !== 'radio');
                                if (inputs.length > 0) {
                                    var setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
                                    setter.call(inputs[0], sec_mail);
                                    inputs[0].dispatchEvent(new Event('input', {bubbles: true}));
                                    inputs[0].dispatchEvent(new Event('change', {bubbles: true}));
                                }
                            }
                        """, sec_mail)
                        time.sleep(0.5)
                        try:
                            inp = page.locator("input:not([type=hidden]).first:not([type=submit]):not([type=checkbox]):not([type=radio])")
                            if inp.is_visible():
                                inp.fill(" ")
                                inp.fill(Keys.BACKSPACE)
                        except: pass
                        log("Da dien Mail bao mat vao form Facebook")
                        time.sleep(5)
                        
                        # 5. Tich chon profile Facebook
                        log("⏳ Đang đợi tích chọn profile Facebook...")
                        try:
                            xpath_profile = "input[type='checkbox'], input[type='radio'], div[role='checkbox'], div[role='radio']"
                            profile_cbs = page.locator(xpath_profile).locator("visible=true")
                            if profile_cbs.count() > 0:
                                cb = profile_cbs.first
                                aria_checked = cb.get_attribute("aria-checked")
                                is_checked = cb.is_checked() if cb.evaluate("el => el.tagName === 'INPUT'") else (aria_checked == "true")
                                
                                if not is_checked:
                                    log("👆 Profile chưa được chọn, đang tick chọn...")
                                    try: cb.click(timeout=3000)
                                    except: pass
                                    
                                    time.sleep(1.5)
                                    aria_checked_now = cb.get_attribute("aria-checked")
                                    is_checked_now = cb.is_checked() if cb.evaluate("el => el.tagName === 'INPUT'") else (aria_checked_now == "true")
                                    
                                    if not is_checked_now:
                                        log("⚠️ Chưa tick được, thử force click...")
                                        try: cb.click(force=True, timeout=3000)
                                        except: pass
                                    log("✅ Đã tick chọn profile Facebook")
                                else:
                                    log("✅ Profile đã được chọn sẵn từ trước!")
                        except Exception as _pe:
                            log(f"⚠️ Lỗi xử lý profile: {_pe}")
                        time.sleep(2)
                        
                        # 6. Nhan Tiep
                        log("⏳ Đang đợi nút 'Tiếp' để lưu Mail bảo mật...")
                        xpath_tiep_sec = "//*[contains(text(), 'Tiếp') or contains(text(), 'Next')]//ancestor::div[@role='button'] | //div[@role='button' and (contains(., 'Tiếp') or contains(., 'Next'))] | //span[text()='Tiếp tục' or text()='Tiếp' or text()='Next']"
                        try:
                            btn_tiep_sec = page.locator(xpath_tiep_sec).last
                            btn_tiep_sec.wait_for(state="visible", timeout=10000)
                            try: btn_tiep_sec.click(timeout=3000)
                            except: btn_tiep_sec.click(force=True, timeout=3000)
                            log("✅ Đã nhấn 'Tiếp' để lưu Mail bảo mật")
                        except Exception as e:
                            log(f"⚠️ Không nhấn được Tiếp: {e}")
                        time.sleep(8)
                        
                        # 7. Lay OTP qua hunght1890.com API
                        log("Dang doi OTP bao mat tu hunght1890.com (toi da 120s)...")
                        sec_code = ""
                        _url = f"https://hunght1890.com/{sec_mail}"
                        for _i in range(30):
                            time.sleep(4)
                            try:
                                _r = requests.get(_url, timeout=10)
                                if _r.status_code == 200:
                                    _data = _r.json()
                                    if isinstance(_data, list) and len(_data) > 0:
                                        import re
                                        used_otps = shared_state.setdefault("used_sec_otps", [])
                                        new_code = None
                                        for msg_data in _data:
                                            subject = msg_data.get("subject", "")
                                            body = msg_data.get("body", "")
                                            
                                            match = re.search(r'FB-(\d{5,6})', subject)
                                            if not match: match = re.search(r'(?<!\d)(\d{5,6})(?!\d)', subject)
                                            
                                            if match:
                                                c = match.group(1)
                                                if c not in used_otps:
                                                    new_code = c
                                                    break
                                                    
                                            if not new_code:
                                                codes = re.findall(r'FB-(\d{5,6})', body)
                                                if not codes: codes = re.findall(r'(?<!\d)(\d{5,6})(?!\d)', body)
                                                for c in reversed(codes):
                                                    if c not in used_otps:
                                                        new_code = c
                                                    break
                                            if new_code: break
                                        
                                        if new_code:
                                            sec_code = new_code
                                            used_otps.append(sec_code)
                                            break
                                log(f"Doi OTP bao mat... ({(_i+1)*4}s)")
                            except: pass
                        
                        if not sec_code:
                            raise Exception("Khong nhan duoc OTP bao mat tu hunght1890.com (het 120s)")
                        
                        log(f"Da lay OTP bao mat: {sec_code}")
                        
                        # 8. Dien ma xac nhan
                        xpath_input_code = "//input[@autocomplete='one-time-code' or @inputmode='numeric' or contains(@aria-label, 'mã xác nhận') or contains(@aria-label, 'code')]"
                        input_code = page.locator(xpath_input_code).first
                        input_code.clear()
                        input_code.fill(sec_code)
                        log("Da dien ma xac nhan")
                        time.sleep(2)
                        
                        # 9. Nhan Tiep hoan tat
                        try:
                            btns2 = [el for el in page.locator(xpath_tiep_sec).all() if el.is_visible()]
                            if btns2:
                                btns2[-1].evaluate("node => node.click()")
                                log("Da nhan Tiep hoan tat bao mat")
                        except: log("Khong nhan duoc Tiep lan 2")
                        time.sleep(8)
                        log("Hoan tat them Mail bao mat!")
                        
                        if monitor and pid:
                            monitor.add_log(pid, f"Mail bao mat: {sec_mail}")
                    except Exception as ex:
                        log(f"Loi trong qua trinh them Mail bao mat: {ex}")
                    
                    # ----------------------------------------------------------
                    # XOA GMAIL/SHOPMAIL CU (Chi ap dung che do Gmail/ShopMail)
                    # ----------------------------------------------------------
                    log("Dang mo lai trang Contact Points de xoa Gmail cu...")
                    try:
                        page.goto("https://accountscenter.facebook.com/personal_info/contact_points")
                        time.sleep(6)
                        
                        # Tim email co chu @gmail hoac email shopmail de xoa
                        # Tìm phần tử Gmail (ưu tiên phần tử nằm trong Modal - thường ở cuối DOM)
                        target_domain = "@gmail.com" if reg_mode == "gmail" else email.split("@")[1] if "@" in email else ""
                        try: page.locator(f"//*[contains(text(), '{target_domain}')]").first.wait_for(timeout=5000)
                        except: pass
                        log(f"Da tim thay Email cu ({target_domain}), dang click de xoa...")
                        gmail_elems = page.locator(f"//*[contains(text(), '{target_domain}')]").all()
                        clicked = False
                        for el in reversed(gmail_elems):
                            try:
                                if el.is_visible():
                                    el.click(force=True, timeout=3000)
                                    clicked = True
                                    time.sleep(1)
                                    # Kiểm tra xem đã chuyển sang trang Xóa chưa, nếu chưa click tiếp cha của nó
                                    try:
                                        parent = el.locator("xpath=ancestor::div[@role='button']").first
                                        parent.click(force=True, timeout=3000)
                                    except: pass
                                    break
                            except: pass
                            
                        if not clicked:
                            # Fallback
                            gmail_row = page.locator(f"//div[@role='button' and contains(., '{target_domain}')]").first
                            try: gmail_row.click(force=True, timeout=3000)
                            except: pass
                            
                        time.sleep(3)
                        
                        # Click "Xoa email"
                        xpath_xoa = "//*[contains(text(), 'Xóa email') or contains(text(), 'Xoá email') or contains(text(), 'Delete email')] | //span[contains(text(), 'Xóa') or contains(text(), 'Delete')]"
                        log("Dang click 'Xóa email'...")
                        xoa_elems = page.locator(xpath_xoa).all()
                        for el in reversed(xoa_elems):
                            try:
                                if el.is_visible():
                                    el.click(force=True, timeout=3000)
                                    break
                            except: pass
                        time.sleep(3)
                        
                        # Click Xac nhan xoa neu co
                        xpath_xacnhan_xoa = "//*[text()='Xóa' or text()='Delete' or @aria-label='Xóa' or @aria-label='Delete']"
                        try:
                            btn_xacnhan = page.locator(xpath_xacnhan_xoa).first
                            btn_xacnhan.click(force=True, timeout=3000)
                            time.sleep(5)
                        except: pass
                        log("Da xoa Email cu thanh cong!")
                    except Exception as e:
                        log(f"Khong the xoa Email cu hoac khong tim thay: {e}")

                else:
                    log("[Hotmail mode] Bo qua buoc them mail bao mat vi acc da la Hotmail.")

                # ----------------------------------------------------------
                # THEM 2FA CHUNG CHO CA 2 MODE
                # ----------------------------------------------------------
                log("Dang mo trang de them 2FA...")
                try:
                    page.goto("https://accountscenter.facebook.com/password_and_security/two_factor")
                    
                    # 1. Click vao profile Facebook
                    xpath_profile_2fa = "//*[contains(text(), 'Facebook')]//ancestor::div[@role='button'] | //div[@role='button' and contains(., 'Facebook')]"
                    profile_btn = page.locator(xpath_profile_2fa).first
                    log("⏳ Đang đợi màn hình 2FA và click vào profile Facebook...")
                    try:
                        profile_btn.wait_for(state="visible", timeout=15000)
                        try: profile_btn.click(timeout=3000)
                        except: profile_btn.click(force=True, timeout=3000)
                    except Exception:
                        log("⚠️ Không tìm thấy profile Facebook để bật 2FA, có thể trang tải chậm hoặc layout thay đổi.")
                    
                    # Kiem tra xem co form bat nhap lai mat khong
                    # Thay vì sleep, wait for pass_input hoặc next screen
                    try:
                        xpath_pass_2fa = "//input[@type='password']"
                        pass_input = page.locator(xpath_pass_2fa).first
                        if pass_input.is_visible(timeout=3000):
                            log("FB yeu cau nhap lai mat khau de xac nhan...")
                            pwd_to_use = password if password else "k999999"
                            pass_input.fill(pwd_to_use)
                            try:
                                xpath_tiep_pass = "//*[text()='Tiếp tục' or text()='Tiếp' or text()='Next' or text()='Continue']//ancestor::div[@role='button'] | //div[@role='button' and (contains(., 'Tiếp') or contains(., 'Next'))] | //span[text()='Tiếp tục' or text()='Continue']"
                                btn_pass_tiep = page.locator(xpath_tiep_pass).all()
                                if btn_pass_tiep:
                                    btn_pass_tiep[-1].evaluate("node => node.click()")
                            except: pass
                    except: pass
                    
                    # 2. Chon Ung dung xac thuc -> Nhấn Tiếp tục
                    log("⏳ Đang đợi chọn 'Ứng dụng xác thực'...")
                    xpath_auth_app = "//*[text()='Ứng dụng xác thực' or contains(text(), 'Authenticator app')]//ancestor::div[@role='button'] | //div[@role='radio' and contains(., 'Ứng dụng xác thực')] | //*[text()='Ứng dụng xác thực']"
                    try:
                        auth_app_btn = page.locator(xpath_auth_app).first
                        auth_app_btn.wait_for(state="visible", timeout=15000)
                        try: auth_app_btn.click(timeout=3000)
                        except: auth_app_btn.click(force=True, timeout=3000)
                    except Exception: pass
                    
                    xpath_tiep_tuc_2fa = "//*[text()='Tiếp tục' or text()='Next']//ancestor::div[@role='button'] | //div[@role='button' and contains(., 'Tiếp tục')] | //span[text()='Tiếp tục' or text()='Next']"
                    btn_tiep_2fa = page.locator(xpath_tiep_tuc_2fa).first
                    log("⏳ Đang đợi click 'Tiếp tục' để chọn Ứng dụng xác thực...")
                    try:
                        btn_tiep_2fa.wait_for(state="visible", timeout=10000)
                        try: btn_tiep_2fa.click(timeout=3000)
                        except: btn_tiep_2fa.click(force=True, timeout=3000)
                    except Exception:
                        log("⚠️ Không tìm thấy nút 'Tiếp tục' 2FA.")
                    
                    # Hack de lay noi dung copy vao clipboard
                    page.evaluate("""
                        window._hijacked_2fa = "";
                        var originalWriteText = navigator.clipboard.writeText;
                        navigator.clipboard.writeText = function(text) {
                            window._hijacked_2fa = text;
                            return originalWriteText ? originalWriteText.apply(navigator.clipboard, arguments) : Promise.resolve();
                        };
                    """)
                    
                    # 3. Click 'Sao chep khoa' de lay ma 2FA
                    xpath_copy = "//*[text()='Sao chép khóa' or contains(text(), 'Copy key')]"
                    btn_copy = page.locator(xpath_copy).first
                    log("⏳ Đang đợi nút 'Sao chép khóa'...")
                    try:
                        btn_copy.wait_for(state="visible", timeout=15000)
                        btn_copy.click(force=True, timeout=3000)
                    except: pass
                    # Chờ 1 giây để javascript chạy event clipboard
                    time.sleep(1)
                    
                    # Lay 2FA tu bien toan cuc window da hack
                    twofa_code = ""
                    try:
                        twofa_code = page.evaluate("return window._hijacked_2fa;")
                    except: pass
                    
                    if not twofa_code:
                        # Thu fallback vao DOM bang regex (32 ky tu in hoa hoac so 2-7)
                        try:
                            import re
                            page_text = page.locator("body").text_content()
                            # Tim tat ca cac ma 2FA (32 ky tu) va lay cai cuoi cung
                            matches = re.findall(r'([A-Z0-9]{4}(?:\s?[A-Z0-9]{4}){7})', page_text)
                            if matches:
                                twofa_code = matches[-1].replace(" ", "")
                            else:
                                # Try reading direct from clipboard if permissions granted
                                clip = page.evaluate("navigator.clipboard.readText()")
                                if clip and len(clip.replace(" ", "")) == 32:
                                    twofa_code = clip.replace(" ", "")
                        except: pass

                    if twofa_code:
                        log(f"LAY 2FA THANH CONG: {twofa_code}")
                        # In test nhu yeu cau
                        print("========================================")
                        print(f"MA 2FA LAY DUOC: {twofa_code}")
                        print("========================================")
                        
                        if monitor and pid:
                            # Luu 2FA code vao bang dieu khien neu co truong 2fa
                            try:
                                monitor.upsert(pid, twofa=twofa_code)
                            except: pass
                            
                        # 4. Click tiep de toi man hinh Nhap Ma
                        xpath_tiep_tuc_2fa_2 = "//*[text()='Tiếp' or text()='Tiếp tục' or text()='Next' or contains(text(), 'Nhập mã') or contains(text(), 'Enter code')] | //span[text()='Nhập mã']"
                        try:
                            btns_tiep2 = [el for el in page.locator(xpath_tiep_tuc_2fa_2).all() if el.is_visible()]
                            if btns_tiep2:
                                try: btns_tiep2[-1].click(timeout=3000)
                                except: btns_tiep2[-1].click(force=True, timeout=3000)
                                log("Da click 'Tiếp / Nhập mã' de chuyen sang nhap ma 2FA...")
                            time.sleep(3)
                        except: pass
                        
                        # 5. Lay ma code OTP 2FA bang cach xu ly ngam
                        # Thay vi dung 2fa.live (can mo tab moi, captcha, quang cao phuc tap),
                        # ta se su dung thu vien pyotp hoac api truc tiep de lay ma luon trong background (nhanh va on dinh hon)
                        totp = pyotp.TOTP(twofa_code)
                        current_otp = totp.now()
                        log(f"Ma OTP tuong ung voi khoa 2FA la: {current_otp}")
                        
                        # 6. Nhap ma OTP 2FA vao form FB
                        xpath_input_2fa = "//input[@type='text' or @inputmode='numeric' or @type='number']"
                        input_2fa = page.locator(xpath_input_2fa).first
                        input_2fa.clear()
                        input_2fa.fill(current_otp)
                        log("Da dien code 2FA!")
                        time.sleep(2)
                        
                        # 7. Nhấn Tiếp de hoan tat
                        try:
                            btns_hoantat = [el for el in page.locator(xpath_tiep_tuc_2fa_2).all() if el.is_visible()]
                            if btns_hoantat:
                                try: btns_hoantat[-1].click(timeout=3000)
                                except: btns_hoantat[-1].click(force=True, timeout=3000)
                                log("Da nhan 'Tiếp' de hoan tat xac thuc 2FA!")
                        except: pass
                        time.sleep(5)
                        
                        # Lay thong tin gui cho Telegram
                        try:
                            uid = ""
                            cookie_str = ""
                            cookies = page.context.cookies()
                            cookie_arr = []
                            for c in cookies:
                                if c['name'] == 'c_user':
                                    uid = c['value']
                                cookie_arr.append(f"{c['name']}={c['value']}")
                            cookie_str = "; ".join(cookie_arr)
                            
                            if not uid:
                                log("⚠️ Tài khoản không có UID (Có thể đã bị Checkpoint)")
                                raise Exception("Tài khoản bị Checkpoint ngay khi tạo")
                                
                            log(f"💰 TÀI KHOẢN HOÀN THIỆN: {uid}|{password}|{twofa_code}|{cookie_str}")
                            print(f"💰 TÀI KHOẢN HOÀN THIỆN: {uid}|{password}|{twofa_code}|{cookie_str}")
                            if monitor and pid:
                                monitor.upsert(pid, uid=uid, cookie=cookie_str, twofa=twofa_code)
                        except Exception as e:
                            log(f"Lỗi khi lấy thông tin hoàn thiện: {e}")
                            if "Checkpoint" in str(e): raise e
                        
                    else:
                        log("Khong lay duoc ma 2FA tu DOM/Clipboard!")
                        raise Exception("Khong lay duoc ma 2FA")
                        
                except Exception as e:
                    log(f"Loi khi bat 2FA: {e}")
                    # Neu loi 2FA thi van phai luu output
                    try:
                        uid = ""
                        cookie_str = ""
                        cookies = page.context.cookies()
                        cookie_arr = []
                        for c in cookies:
                            if c['name'] == 'c_user':
                                uid = c['value']
                            cookie_arr.append(f"{c['name']}={c['value']}")
                        cookie_str = "; ".join(cookie_arr)
                        
                        if not uid:
                            log("⚠️ Tài khoản không có UID (Có thể đã bị Checkpoint)")
                            raise Exception("Tài khoản bị Checkpoint ngay khi tạo")
                            
                        log(f"💰 TÀI KHOẢN HOÀN THIỆN: {uid}|{password}|{cookie_str}")
                        print(f"💰 TÀI KHOẢN HOÀN THIỆN: {uid}|{password}|{cookie_str}")
                        if monitor and pid:
                            monitor.upsert(pid, uid=uid, cookie=cookie_str)
                    except Exception as ex:
                        if "Checkpoint" in str(ex): raise ex

            # ----------------------------------------------------------
            log("HOAN THANH TAT CA CHUOI DANG KY!")
            
            # Xóa sạch cookie facebook để tạo môi trường sạch cho nick tiếp theo
            # (Đã bỏ theo yêu cầu: Mỗi lần chạy đều tạo 1 trình duyệt/context mới hoàn toàn nên không cần xóa)
            
            break  # Thanh cong -> Thoat vong lap lam lai
            
        except Exception as e:
            import traceback
            err_msg = traceback.format_exc()
            log(f"Loi tai buoc nao do:\n{err_msg}")
            if monitor and pid:
                monitor.set_status(pid, "Loi/Bi chan")
            raise Exception(str(e))
    # Don dep...
    try:
        if 'profile_id' in locals():
            log(f"Hoan thanh session Playwright cho {profile_id}")
    except: pass

if __name__ == "__main__":
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        log("🚀 Khởi tạo Playwright cục bộ (Fake iOS)")
        
        # Chọn thiết bị iOS
        iphone_13 = p.devices['iPhone 13'].copy()
        iphone_13['user_agent'] = "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4.25 Mobile/XMMAGK Safari/619.25"
        
        # Thiết lập proxy đã cấp
        proxy_config = {
            "server": "http://171.229.255.155:58330",
            "username": "qyhjp_caigh",
            "password": "TYMeRjEh"
        }
        
        # Mở trình duyệt (hiện giao diện)
        browser = p.chromium.launch(headless=False)
        
        # Tạo ngữ cảnh với proxy, timezone, locale và faking iOS chuẩn
        context = browser.new_context(
            **iphone_13,
            locale='vi-VN',
            timezone_id='Asia/Ho_Chi_Minh',
            proxy=proxy_config
        )
        
        # Lẩn tránh phát hiện tự động hóa
        context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """)

        # Cài đặt biến toàn cục mặc định để chạy trực tiếp
        globals()['reg_mode'] = 'shopmail'  # Hoặc 'gmail', 'hotmail'
        globals()['use_phone_seed'] = True
        globals()['phone_prefix'] = '0987'
        globals()['fb_name_lang'] = 'Tiếng Việt (Không dấu)'

        page = context.new_page()
        
        try:
            run(page)
        except Exception as e:
            log(f"Lỗi khi chạy Playwright: {e}")
        finally:
            log("🛑 Script kết thúc, dừng trình duyệt...")
            context.close()
            browser.close()
