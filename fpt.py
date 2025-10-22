import json
import os
import time

import requests


def text_to_speech_fpt_sync(text, voice="banmai", speed="", output_file="output.mp3"):
    """
    Chuyển đổi text thành giọng nói sử dụng FPT TTS API (sync)
    """
    url = "https://api.fpt.ai/hmi/tts/v5"

    headers = {
        "api-key": "cw8ujjrrSMYNCP2gyf4NSJOGpyd3NwZr",
        "speed": speed,
        "voice": voice,
    }

    try:
        # Gửi request để tạo audio
        print("Đang gửi request tạo audio (sync)...")
        response = requests.post(url, data=text.encode("utf-8"), headers=headers)

        if response.status_code == 200:
            # Kiểm tra content-type để xem có phải là file audio không
            content_type = response.headers.get("content-type", "")
            print(f"Content-Type: {content_type}")

            if "audio" in content_type or "mp3" in content_type:
                # Lưu file trực tiếp
                with open(output_file, "wb") as f:
                    f.write(response.content)

                file_size = os.path.getsize(output_file)
                print(f"✅ Tải file thành công!")
                print(f"📁 File: {output_file}")
                print(f"📊 Kích thước: {file_size:,} bytes")
                return True
            else:
                # Thử parse JSON response
                try:
                    result = response.json()
                    print(f"JSON Response: {result}")

                    if result.get("error") == 0 and "async" in result:
                        async_url = result["async"]
                        print(f"Đang chờ file audio được tạo...")
                        print(f"Async URL: {async_url}")

                        # Chờ và tải file MP3
                        return download_audio_file(async_url, output_file)
                    else:
                        print(f"Lỗi từ API: {result.get('message', 'Unknown error')}")
                        return False
                except:
                    print(f"Response không phải JSON: {response.text[:200]}...")
                    return False
        else:
            print(f"Lỗi HTTP: {response.status_code}")
            print(f"Response: {response.text}")
            return False

    except Exception as e:
        print(f"Lỗi: {str(e)}")
        return False


def text_to_speech_fpt(text, voice="banmai", speed="", output_file="output.mp3"):
    """
    Chuyển đổi text thành giọng nói sử dụng FPT TTS API
    """
    url = "https://api.fpt.ai/hmi/tts/v5"

    headers = {
        "api-key": "cw8ujjrrSMYNCP2gyf4NSJOGpyd3NwZr",
        "speed": speed,
        "voice": voice,
    }

    try:
        # Gửi request để tạo audio
        print("Đang gửi request tạo audio...")
        response = requests.post(url, data=text.encode("utf-8"), headers=headers)

        if response.status_code == 200:
            result = response.json()
            print(f"Response: {result}")

            if result.get("error") == 0 and "async" in result:
                async_url = result["async"]
                print(f"Đang chờ file audio được tạo...")
                print(f"Async URL: {async_url}")

                # Chờ và tải file MP3
                return download_audio_file(async_url, output_file)
            else:
                print(f"Lỗi từ API: {result.get('message', 'Unknown error')}")
                return False
        else:
            print(f"Lỗi HTTP: {response.status_code}")
            print(f"Response: {response.text}")
            return False

    except Exception as e:
        print(f"Lỗi: {str(e)}")
        return False


def download_audio_file(async_url, output_file, max_retries=20, delay=5):
    """
    Tải file audio từ async URL với retry logic
    """
    for attempt in range(max_retries):
        try:
            print(f"Lần thử {attempt + 1}/{max_retries}: Đang tải file audio...")

            # Gửi request GET để tải file
            response = requests.get(async_url, timeout=30)

            if response.status_code == 200:
                # Kiểm tra content-type để đảm bảo là file audio
                content_type = response.headers.get("content-type", "")
                if "audio" in content_type or "mp3" in content_type:
                    # Lưu file
                    with open(output_file, "wb") as f:
                        f.write(response.content)

                    file_size = os.path.getsize(output_file)
                    print(f"✅ Tải file thành công!")
                    print(f"📁 File: {output_file}")
                    print(f"📊 Kích thước: {file_size:,} bytes")
                    return True
                else:
                    print(
                        f"⚠️ Response không phải là file audio. Content-Type: {content_type}"
                    )
                    print(f"Response content: {response.text[:200]}...")
            else:
                print(f"⚠️ HTTP {response.status_code}: {response.text[:200]}...")

        except requests.exceptions.Timeout:
            print(f"⏰ Timeout - File chưa sẵn sàng")
        except Exception as e:
            print(f"❌ Lỗi khi tải file: {str(e)}")

        if attempt < max_retries - 1:
            print(f"⏳ Chờ {delay} giây trước khi thử lại...")
            time.sleep(delay)

    print(f"❌ Không thể tải file sau {max_retries} lần thử")
    return False


# Nội dung text cần chuyển đổi
payload = """Scandal Hôn Nhân
 Năm tháng nổi tiếng nhất, Khương Khoáng đã bất chấp tất cả mà công bố chuyện tình cảm.
 Sự nghiệp của tôi lao dốc.
 Fan quay lưng "cắn" ngược.
 Anh ấy vẫn nói không hối hận.
 Tôi từ bỏ công việc.
 Kết hôn với anh ấy, trở thành nội trợ toàn thời gian.
 Năm thứ năm sau khi kết hôn.
 Ánh mắt anh ấy nhìn tôi không còn nồng nhiệt.
 Tôi không để tâm.
 Chỉ coi đó là hôn nhân bước vào giai đoạn bình lặng.
 Cho đến khi.
 Tin đồn anh ấy và người mẫu hạng bét hôn nhau cuồng nhiệt trước cửa khách sạn.
 Ồn ào trên Top tìm kiếm.
 Tôi nén đau đi tìm anh ấy hỏi cho ra lẽ.
 Người đàn ông chỉ mệt mỏi day trán.
 Năm đó sau khi công bố chính thức về em.
 Sự nghiệp của anh suýt chút nữa đã tiêu tan.
 Em còn muốn gì nữa?
 Không muốn gì cả.
 Chỉ là ly hôn thôi.
 Bạn bè nói Khương Khoáng hình như ngoại tình.
 Tôi không tin.
 Anh ấy bận rộn như vậy.
 Tất cả lịch trình gần như đều có ống kính theo sát.
 Thời gian đâu mà ngoại tình?
 Chỉ là không ngờ bị "tát" vào mặt nhanh đến vậy.
 Top tìm kiếm về nghệ sĩ đang hot Khương Khoáng hẹn hò bí mật với người mẫu hạng bét vào đêm khuya.
 Được đẩy về điện thoại của tôi.
 Trước khi bấm mở.
 Tôi đã mong biết bao đó là do Paparazzi làm chiêu trò.
 Một video cắt ghép.
 Năm phút trôi qua.
 Trong điện thoại tôi, đoạn video đó đã lặp đi lặp lại vô số lần.
 Đoạn video quay lén đó.
 Khương Khoáng đội mũ, cúi đầu hôn người phụ nữ trong lòng.
 Ngay trước cửa khách sạn, ngang nhiên như vậy.
 Tôi không biết là Khương Khoáng chắc mẩm không ai quay được.
 Hay là đã quá quen thuộc với việc xử lý những chuyện như thế này rồi.
 Hoàn toàn không sợ tôi sẽ biết.
 Khi bấm mở lại.
 Đoạn video đã biến mất.
 Tất cả kết quả tìm kiếm liên quan đến chuyện này đều không còn.
 Bộ phận PR làm việc rất nhanh.
 Nếu không tình cờ nhìn vào điện thoại.
 Chắc tôi cả đời cũng khó mà biết được chuyện này.
 Tay tôi vẫn còn xách canh đã hầm cho Khương Khoáng.
 Tối qua anh ấy gọi điện thoại.
 Nói rằng ăn cơm ở đoàn làm phim bị tái phát bệnh dạ dày.
 Tôi đã thức trắng đêm.
 Hôm nay là chuyến bay sớm nhất tôi bay đến.
 Vốn dĩ là muốn tạo cho anh ấy một bất ngờ.
 Nên đã không nói cho ai biết.
 Không ngờ.
 Anh ấy lại tạo cho tôi một bất ngờ lớn hơn.
 Lớn đến mức khiến người ta không thể chịu đựng nổi.
 Tôi chỉ nhắn cho Khương Khoáng một câu: Về nhà đi, có chuyện cần nói với anh.
 Anh ấy gọi lại.
 Tôi bấm tắt máy.
 Chưa đầy một tiếng sau.
  Khương Khoáng đã về.
 Về rồi, chắc là vừa xuống máy bay đã đến ngay.
 Trong lòng còn ôm hoa và thư của fan tặng.
 Anh ấy buông va li ra.
 Quỳ một chân xuống.
 Ôm lấy eo tôi.
 Anh nhớ em lắm.
 Khương Khoáng rất yêu sạch sẽ.
 Có tính sạch sẽ gần như ám ảnh.
 Vậy nên.
 Tôi không ngửi thấy mùi nước hoa của phụ nữ khác trên người anh ấy.
 Tôi đẩy anh ấy ra, bật đèn lên.
 Có ánh đèn, mọi thứ trên bàn đều rõ ràng.
 Là một tấm ảnh vừa in ra.
 Một trong những nhân vật chính trong ảnh, chính là anh ấy đêm qua.
 Khương Khoáng hơi sững lại, đứng dậy.
 Lạnh giọng nói: Em biết hết rồi à?
 Tôi đã cẩn thận, chụp lại màn hình.
 Chụp lại màn hình, cố ý rửa ra.
 Để tránh khi tôi chất vấn, anh ấy giả vờ không biết.
 Bắt đầu từ khi nào?
 Tôi không hỏi anh ấy.
 Là ai?
 Là ai cũng không còn quan trọng nữa rồi.
 Khương Khoáng hơi bực bội, giật lỏng cà vạt.
 Ngồi đối diện với tôi.
 Anh không nhớ.
 Tôi nhìn người mình đã yêu 15 năm này, không thể nhìn rõ.
 Ly hôn đi.
 Người đàn ông khựng lại.
 Ánh mắt không thiện cảm nhìn chằm chằm tôi.
 Em có biết bây giờ mà ly hôn.
 Sẽ gây ra hậu quả gì cho anh không?
 Anh ấy đã mất 5 năm.
 Để bò dậy từ đáy.
 Nếu lại dính vào scandal ngoại tình trong hôn nhân.
 Lại phải trở về vạch xuất phát."""


# Test với URL từ response gốc của bạn
def test_with_original_url():
    """
    Test với URL từ response gốc
    """
    original_url = "https://file01.fpt.ai/text2speech-v5/short/2025-09-16/29f154096e4bd0bd0adc081f4c900959.mp3"
    print("🔗 Đang thử tải file từ URL gốc...")
    success = download_audio_file(
        original_url, "scandal_hon_nhan_original.mp3", max_retries=10, delay=5
    )
    return success


# Chạy chương trình
if __name__ == "__main__":
    print("🎤 Bắt đầu chuyển đổi text thành giọng nói...")

    # Thử với URL gốc trước
    print("\n=== THỬ VỚI URL GỐC ===")
    success_original = test_with_original_url()

    if not success_original:
        print("\n=== THỬ TẠO FILE MỚI (SYNC) ===")
        success_sync = text_to_speech_fpt_sync(
            payload, voice="banmai", output_file="scandal_hon_nhan_sync.mp3"
        )

        if success_sync:
            print("🎉 Hoàn thành! File audio sync đã được lưu.")
        else:
            print("\n=== THỬ TẠO FILE MỚI (ASYNC) ===")
            success_async = text_to_speech_fpt(
                payload, voice="banmai", output_file="scandal_hon_nhan_async.mp3"
            )

            if success_async:
                print("🎉 Hoàn thành! File audio async đã được lưu.")
            else:
                print("❌ Có lỗi xảy ra trong quá trình tạo audio.")
    else:
        print("🎉 Hoàn thành! File audio gốc đã được lưu.")
