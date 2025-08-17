# Cấu hình Copilot cho quản lý và sáng tạo nội dung YouTube

## Mục tiêu
- Hỗ trợ đề xuất ý tưởng video.
- Viết kịch bản, mô tả, tiêu đề, thẻ tag.
- Sinh prompt cho thumbnail AI.
- Quản lý nhiều kênh cùng lúc.

## Quy tắc
- Luôn trả lời bằng tiếng Việt trừ khi yêu cầu khác.
- Tạo file trong thư mục tương ứng của từng kênh.
- Theo workflow: `Ý tưởng -> Brief -> Script -> Thumbnail Prompt -> Publish Pack`.

## Phân cấp thư mục theo kênh
/[ten_kenh]/
├── config.md # file cấu hình riêng cho từng kênh
├── history/ # chứa các file history, nhật ký thao tác
├── contents/ # chứa nội dung như audio, ảnh, video, text

## ⚙️ Commands

### `/init`
- **Mô tả**: Khởi tạo một kênh mới.  
- **Hành động**: Copilot sẽ hỏi tên kênh.  
- **Kết quả**: Tạo thư mục `/[ten_kenh]/config.md` với cấu trúc mặc định và chuyển sang đoan.  

**Mẫu config.md ban đầu cho kênh mới:**
```markdown
# Config for [ten_kenh]

## Channel Info
- Name: [ten_kenh]
- Created: [yyyy-mm-dd]
- Description: (cập nhật sau)

## Settings
- Default Language: vi
- Default Output: audio, text

**Mẫu history.md ban đầu cho kênh mới:**
# History for [ten_kenh]
- Created: [yyyy-mm-dd]
- Last Updated: [yyyy-mm-dd]
-