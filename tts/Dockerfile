FROM python:3.9-slim

# Cài đặt các dependencies hệ thống
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    libsndfile1 \
    espeak-ng \
    espeak-ng-data \
    libespeak-ng1 \
    git \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Thiết lập thư mục làm việc
WORKDIR /app

# Copy requirements và cài đặt Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Tạo thư mục cho models và audio output
RUN mkdir -p /app/models /app/output

# Expose port cho API
EXPOSE 5000

# Command mặc định
CMD ["python", "app.py"]