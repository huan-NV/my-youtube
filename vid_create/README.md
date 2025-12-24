# Engine Render Video Offline

Một engine Python sẵn sàng cho production để tạo video từ hình ảnh, file âm thanh và script dựa trên JSON. Hoàn toàn offline, sử dụng moviepy và ffmpeg.

## Tính năng

- **Hoàn toàn Offline**: Không cần cloud API hay dịch vụ bên ngoài
- **Điều khiển bằng JSON**: Kiểm soát hoàn toàn qua script JSON - không có logic hardcode
- **Animation Keyframe**: Nội suy mượt mà với các hàm easing có thể mở rộng
- **Dựa trên Timeline**: Kiểm soát chính xác chuyển động nhân vật, hội thoại và sự kiện
- **Đồng bộ Audio**: Nhiều track audio với timing chính xác
- **Kiến trúc Module**: Tách biệt rõ ràng các mối quan tâm, sẵn sàng mở rộng

## Bắt đầu nhanh

1. **Cài đặt dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

2. **Xác minh FFmpeg đã được cài đặt:**

   ```bash
   ffmpeg -version
   ```

3. **Chuẩn bị assets:**

   - Đặt hình nền vào `assets/backgrounds/`
   - Đặt PNG nhân vật vào `assets/characters/`
   - Đặt file audio vào `assets/audio/`

4. **Tạo hoặc sử dụng script mẫu:**

   ```bash
   python main.py scripts/example_scene.json
   ```

5. **Kiểm tra script (tùy chọn):**
   ```bash
   python validate_script.py scripts/example_scene.json
   ```

## Cài đặt

### Yêu cầu

- Python 3.8+
- FFmpeg (phải được cài đặt và có trong PATH)

### Cài đặt Dependencies

```bash
pip install -r requirements.txt
```

### Xác minh FFmpeg

```bash
ffmpeg -version
```

## Cấu trúc Dự án

```
vid_create/
├── engine/              # Engine render chính
│   ├── actor.py        # Quản lý actor/nhân vật
│   ├── timeline.py     # Parse sự kiện timeline
│   ├── animation.py    # Hệ thống animation keyframe
│   ├── audio.py        # Quản lý track audio
│   ├── scene_builder.py # Tạo thành phần scene
│   └── renderer.py     # Điều phối renderer chính
├── assets/             # Assets hình ảnh và audio
│   ├── backgrounds/    # Hình nền
│   ├── characters/     # PNG nhân vật (có alpha)
│   └── audio/          # File audio (dialog, music, sfx)
├── scripts/            # File script JSON
├── output/             # Video đã render
└── main.py             # Điểm vào chính
```

## Schema Script JSON

### Metadata

```json
{
  "metadata": {
    "width": 1920,
    "height": 1080,
    "fps": 30
  }
}
```

### Cấu trúc Scene

```json
{
  "scenes": [
    {
      "background": "backgrounds/scene1_bg.png",
      "actors": [
        {
          "id": "character_a",
          "image": "characters/character_a.png",
          "scale": 1.0
        }
      ],
      "timeline": [...],
      "audio": {...}
    }
  ]
}
```

### Sự kiện Timeline

#### Sự kiện Spawn

```json
{
  "type": "spawn",
  "actor_id": "character_a",
  "start_time": 0.0,
  "duration": 0.0,
  "position": [960, 540]
}
```

#### Sự kiện Move

```json
{
  "type": "move",
  "actor_id": "character_a",
  "start_time": 1.0,
  "duration": 2.0,
  "from": [100, 540],
  "to": [900, 540],
  "easing": "linear"
}
```

Các loại easing được hỗ trợ: `linear`, `ease_in`, `ease_out`, `ease_in_out`

#### Sự kiện Dialog

```json
{
  "type": "dialog",
  "actor_id": "character_a",
  "start_time": 3.0,
  "duration": 2.5
}
```

#### Sự kiện Idle

```json
{
  "type": "idle",
  "actor_id": "character_a",
  "start_time": 3.0,
  "duration": 5.0
}
```

#### Sự kiện Exit

```json
{
  "type": "exit",
  "actor_id": "character_a",
  "start_time": 8.0,
  "duration": 1.0,
  "position": [-200, 540]
}
```

### Cấu hình Audio

```json
{
  "audio": {
    "dialog": [
      {
        "file": "audio/dialog_character_a_line1.wav",
        "start_time": 3.0,
        "volume": 1.0
      }
    ],
    "music": [
      {
        "file": "audio/background_music.mp3",
        "start_time": 0.0,
        "volume": 0.3,
        "loop": true
      }
    ],
    "sfx": [
      {
        "file": "audio/sfx_impact.wav",
        "start_time": 2.5,
        "volume": 0.8
      }
    ]
  }
}
```

## Cách sử dụng

### Sử dụng cơ bản

```bash
python main.py scripts/example_scene.json
```

### Thư mục Assets tùy chỉnh

```bash
python main.py scripts/example_scene.json --assets custom_assets
```

### Đường dẫn Output tùy chỉnh

```bash
python main.py scripts/example_scene.json --output output/my_video.mp4
```

### Ví dụ đầy đủ

```bash
python main.py scripts/example_scene.json --assets assets --output output/final.mp4
```

## Ví dụ Kịch bản

Script mẫu (`scripts/example_scene.json`) minh họa:

1. Nhân vật B xuất hiện ở giữa
2. Nhân vật A xuất hiện ngoài màn hình (bên trái)
3. Nhân vật A di chuyển về phía Nhân vật B
4. Cả hai nhân vật giữ nguyên vị trí để hội thoại
5. Audio hội thoại phát cho cả hai nhân vật
6. Cả hai nhân vật rời khỏi màn hình
7. Nhạc nền phát trong suốt

## Kiến trúc

### Các thành phần chính

- **Actor**: Quản lý hình ảnh nhân vật và biến đổi
- **Timeline**: Parse và quản lý sự kiện timeline
- **Animation**: Animation dựa trên keyframe với nội suy
- **AudioManager**: Xử lý nhiều track audio và đồng bộ
- **SceneBuilder**: Tạo thành phần scene từ actors, backgrounds và timelines
- **Renderer**: Điều phối pipeline render hoàn chỉnh

### Nguyên tắc thiết kế

- **Tách biệt mối quan tâm**: Mỗi module có một trách nhiệm duy nhất
- **Có thể mở rộng**: Dễ dàng thêm loại sự kiện mới, hàm easing, tính năng
- **Không có Magic Numbers**: Tất cả giá trị có thể cấu hình qua JSON
- **Sẵn sàng Production**: Xử lý lỗi, validation, code sạch

## Mở rộng trong tương lai

Kiến trúc được thiết kế để dễ dàng hỗ trợ:

- **Easing nâng cao**: Các hàm easing tùy chỉnh (bounce, elastic, v.v.)
- **Chuyển động Camera**: Hiệu ứng pan, zoom, shake
- **Lip Sync**: Đồng bộ chuyển động miệng với audio
- **Phụ đề**: Overlay văn bản với timing
- **Render hàng loạt**: Xử lý nhiều script
- **Hiệu ứng**: Bộ lọc, chuyển cảnh, hiệu ứng hạt

## Khắc phục sự cố

### Không tìm thấy FFmpeg

Đảm bảo FFmpeg đã được cài đặt và có trong PATH:

```bash
# Windows (sử dụng chocolatey)
choco install ffmpeg

# macOS
brew install ffmpeg

# Linux
sudo apt-get install ffmpeg
```

### Vấn đề đồng bộ Audio

- Đảm bảo định dạng file audio tương thích (khuyến nghị WAV, MP3)
- Kiểm tra giá trị `start_time` khớp với sự kiện timeline
- Xác minh thời lượng file audio khớp với thời lượng sự kiện dialog

### Định vị Actor

- Vị trí được chỉ định dưới dạng tọa độ trung tâm `[x, y]`
- Gốc (0, 0) là góc trên bên trái
- Actors tự động được căn giữa tại vị trí của chúng

### Hiệu suất

- Độ phân giải lớn và FPS cao làm tăng thời gian render
- Cân nhắc sử dụng `preset='fast'` trong renderer.py để render nhanh hơn (chất lượng thấp hơn)
- Nhiều track audio có thể làm tăng thời gian xử lý

## Giấy phép

Dự án này được cung cấp như hiện tại cho mục đích sử dụng production.
