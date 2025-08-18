from selenium import webdriver
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time, random
import re

so_chuong = 100

# ======== Hàm chia văn bản nhỏ hơn 500 ký tự ========
def split_text(text, max_length=3000):
    sentences = re.split(r'(?<=[.!?…])\s+', text)
    chunks, current = [], ""
    for s in sentences:
        if len(current) + len(s) <= max_length:
            current += s + " "
        else:
            chunks.append(current.strip())
            current = s + " "
    if current:
        chunks.append(current.strip())
    return chunks

# ======== Đọc file văn bản, chia đoạn ========
def prepare_chunks(file_path):
    with open(file_path, encoding="utf-8") as f:
        raw_text = f.read()
    return split_text(raw_text)

# --- Cấu hình trình duyệt ---
options = Options()
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
url = "https://ttsmaker.com/vn"
driver.get(url)
time.sleep(random.uniform(3, 8))
# --- Chọn ngôn ngữ ---
# select_element = Select(driver.find_element(By.ID, "RadioUserSelectAnnouncerID101002"))
# select_element.select_by_value("vi-VN")
# time.sleep(1)

chon_giong_doc = driver.find_element(By.ID, "RadioUserSelectAnnouncerID101002")
chon_giong_doc.click()
time.sleep(random.uniform(3, 8))

chuong=1
while 1 <= so_chuong:
    file_path = f"Z:/audio truyen/em-gai-cuu-voi/{chuong}.txt"
    danh_sach_text = prepare_chunks(file_path)
    for input_text  in danh_sach_text:
        # --- Nhập đoạn văn ---
        text_input_element = driver.find_element(By.ID, "UserInputTextarea")
        text_input_element.clear()
        text_input_element.send_keys(input_text)
        time.sleep(random.uniform(3, 8))
        input("Nhập captcha rồi nhấn Enter để tiếp tục...")
        # --- Click nút Convert ---
        # convert_button = driver.find_element(By.ID, "tts_order_submit")
        # convert_button.click()
        
        # --- (Tùy chọn) Chờ kết quả, rồi lấy output nếu có ---
        time.sleep(random.uniform(3, 8))
        
        #savevoice
        save_audio = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "tts_mp3_download_btn"))
        )
        save_audio.click()
        time.sleep(random.uniform(3, 8))
    chuong += 1
 
# --- Đóng trình duyệt ---
driver.quit()