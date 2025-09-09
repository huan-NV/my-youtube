FROM python:3.9-slim

# Cài đặt các dependencies cần thiết
RUN apt-get update && apt-get install -y \
    git \
    build-essential \
    libsndfile1 \
    ffmpeg \
    espeak-ng \
    espeak \
    espeak-data \
    libespeak1 \
    libespeak-dev \
    festival* \
    && rm -rf /var/lib/apt/lists/*

# Thiết lập thư mục làm việc
WORKDIR /app

# Cài đặt Coqui TTS
RUN pip install --no-cache-dir TTS torch torchaudio

# Copy script khởi động
COPY start.py /app/
COPY requirements.txt /app/

# Cài đặt thêm dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port
EXPOSE 5002

# Chạy ứng dụng
CMD ["python", "start.py"]