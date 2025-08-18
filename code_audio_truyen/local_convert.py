import json
from TTS.api import TTS

# Bước 1: Load từ điển chuẩn hóa
def normalize_text(text, dict_path="dictionary.json"):
    with open(dict_path, "r", encoding="utf-8") as f:
        custom_dict = json.load(f)

    for k, v in custom_dict.items():
        text = text.replace(k, v)
    return text

# Bước 2: Tạo TTS model local (auto tải model tiếng Việt lần đầu)
tts = TTS(model_name="tts_models/vi/viet_tts", progress_bar=True)

# Bước 3: Chuẩn hóa câu cần đọc
text = "Xin chào TP.HCM! Tôi nặng 70kg."
text_normalized = normalize_text(text)

# Bước 4: TTS - Chuyển text thành audio WAV
tts.tts_to_file(text=text_normalized, file_path="output.wav")

print("✅ Đã tạo file audio: output.wav")
