import os
import re


def split_text_by_sentences(text, max_words=1000):
    """Tách văn bản thành các đoạn <= max_words từ, giữ nguyên câu."""
    # Tách câu theo dấu câu (., !, ?, …)
    sentences = re.split(r"(?<=[\.\!\?…])\s+", text.strip())
    chunks = []
    current_chunk = []
    current_count = 0

    for sentence in sentences:
        words = sentence.split()
        word_count = len(words)

        # Nếu câu này quá dài (> max_words), cắt nhỏ theo từ
        if word_count > max_words:
            for i in range(0, word_count, max_words):
                chunk = " ".join(words[i : i + max_words])
                chunks.append(chunk.strip())
            continue

        # Nếu thêm câu này vẫn < max_words thì cộng dồn
        if current_count + word_count <= max_words:
            current_chunk.append(sentence)
            current_count += word_count
        else:
            # Lưu đoạn cũ và reset
            chunks.append(" ".join(current_chunk).strip())
            current_chunk = [sentence]
            current_count = word_count

    # Thêm đoạn cuối cùng
    if current_chunk:
        chunks.append(" ".join(current_chunk).strip())

    return chunks


def process_txt_files(input_dir, output_dir, max_words=1000):
    """Xử lý tất cả file txt trong thư mục"""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for filename in os.listdir(input_dir):
        if filename.endswith(".txt"):
            input_path = os.path.join(input_dir, filename)

            with open(input_path, "r", encoding="utf-8") as f:
                text = f.read()

            chunks = split_text_by_sentences(text, max_words)

            # Lưu các đoạn vào file mới
            for idx, chunk in enumerate(chunks, 1):
                output_filename = f"{os.path.splitext(filename)[0]}_part{idx}.txt"
                output_path = os.path.join(output_dir, output_filename)
                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(chunk)

            print(f"✅ Đã xử lý {filename}, chia thành {len(chunks)} file nhỏ")


# Ví dụ chạy
input_dir = (
    "D:/my/my-youtube/audio_truyen/cung-nu-kieu-kieu-an-duong"  # thư mục chứa file gốc
)
output_dir = "D:/my/my-youtube/audio_truyen/cung-nu-kieu-kieu-an-duong-converted"  # thư mục kết quả
process_txt_files(input_dir, output_dir, max_words=1000)
