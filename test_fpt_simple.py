import os
import time

import requests


def download_audio_with_long_wait(async_url, output_file):
    """
    Tải file audio với thời gian chờ dài hơn
    """
    print(f"🔗 URL: {async_url}")
    print("⏳ Chờ 30 giây trước khi bắt đầu tải...")
    time.sleep(30)

    for attempt in range(1, 11):
        try:
            print(f"Lần thử {attempt}/10: Đang tải file audio...")

            response = requests.get(async_url, timeout=30)

            if response.status_code == 200:
                content_type = response.headers.get("content-type", "")
                print(f"Content-Type: {content_type}")

                if "audio" in content_type or "mp3" in content_type:
                    with open(output_file, "wb") as f:
                        f.write(response.content)

                    file_size = os.path.getsize(output_file)
                    print(f"✅ Tải file thành công!")
                    print(f"📁 File: {output_file}")
                    print(f"📊 Kích thước: {file_size:,} bytes")
                    return True
                else:
                    print(f"⚠️ Response không phải audio. Content-Type: {content_type}")
                    print(f"Response: {response.text[:200]}...")
            else:
                print(f"⚠️ HTTP {response.status_code}: {response.text[:200]}...")

        except Exception as e:
            print(f"❌ Lỗi: {str(e)}")

        if attempt < 10:
            print(f"⏳ Chờ 10 giây trước khi thử lại...")
            time.sleep(10)

    print("❌ Không thể tải file sau 10 lần thử")
    return False


# Test với URL gốc
if __name__ == "__main__":
    original_url = "https://file01.fpt.ai/text2speech-v5/short/2025-09-16/29f154096e4bd0bd0adc081f4c900959.mp3"
    print("🎤 Test tải file audio với thời gian chờ dài...")

    success = download_audio_with_long_wait(original_url, "test_audio.mp3")

    if success:
        print("🎉 Thành công!")
    else:
        print("❌ Thất bại!")

