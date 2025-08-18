from pydub import AudioSegment
import os
import re
from datetime import datetime

# Thư mục chứa file audio
ten_truyen = "nong-gia-tieu-han-phi-mang-theo-de-muoi-kiem-song"
folder_path = "Z:/audio truyen/" + ten_truyen + "/audio/audio-theo-ngay/"

# Lấy danh sách file mp3 trong thư mục
files = [f for f in os.listdir(folder_path) if f.endswith(".mp3")]

# Hàm sắp xếp theo số hoặc theo thời gian trong tên file
def sort_key(filename):
    # Nếu tên file là số, sắp theo số
    if re.match(r'^\d+\.mp3$', filename):
        return int(filename.split(".")[0])
    # Nếu tên file dạng ttsmaker-file-2025-4-16-20-48-54.mp3
    else:
        match = re.search(r'(\d{4}-\d+-\d+-\d+-\d+-\d+)', filename)
        if match:
            date_parts = [int(x) for x in match.group(1).split("-")]
            return date_parts
        else:
            # Nếu không match thì để sau cùng
            return [9999, 99, 99, 99, 99, 99]

# Sắp xếp file
files.sort(key=sort_key)

# Ghép file
combined = AudioSegment.empty()

for file in files:
    audio = AudioSegment.from_mp3(os.path.join(folder_path, file))
    combined += audio

now = datetime.now()
output_filename = now.strftime(f"{ten_truyen}-%d-%m-%Y-%H-%M-%S.mp3")
# Xuất file cuối cùng
output_folder = folder_path + "all-mp3/"
os.makedirs(output_folder, exist_ok=True)
combined.export(output_folder + output_filename, format="mp3")

print(f"Đã ghép {len(files)} file audio thành: {output_folder + output_filename}")
