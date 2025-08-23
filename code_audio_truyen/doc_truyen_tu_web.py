import os
from selenium import webdriver
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import time
 


# tên truyện sẽ được cài đặt làm tên file
TRUYEN_NAME = "cai-gia-cua-ngai-hau"
# link truyện bắt đầu từ chương 1
# trong url thay số chương bằng %chuong
URL = f"https://truyenfull.vision/{TRUYEN_NAME}/chuong-%chuong"
# số chương tối đa(chương cuối)
END_CHAP = 32
# id thẻ chứa nội dung truyện
ID_THE_NOI_DUNG = "chapter-c"
# thư mục chứa nội dung truyện
SAVE_TRUYEN_PATH = "E:/project/my-youtube/audio_truyen/"

folder_path = f"{SAVE_TRUYEN_PATH}{TRUYEN_NAME}"
if not os.path.exists(folder_path):
    os.makedirs(folder_path)
    print(f"Đã tạo thư mục: {folder_path}")

# --- Cấu hình trình duyệt ---
driver = webdriver.Chrome()  # Bạn cần cài sẵn chromedriver hoặc để nó trong PATH

chuong = 1
while chuong <= END_CHAP:
    # --- Truy cập website ---
    driver.get(URL.replace("%chuong", f"{chuong}"))
    time.sleep(2)  # Chờ trang load
    the_noi_dung_chap = driver.find_element(By.ID, ID_THE_NOI_DUNG)
    noi_dung_chap = the_noi_dung_chap.text
    time.sleep(1)
    # ghi vào thư mục
    with open(folder_path + f"/{chuong}.txt", "w", encoding="utf-8") as f:
        f.write(noi_dung_chap)
    time.sleep(1)
    chuong += 1
 
# --- Đóng trình duyệt ---
driver.quit()