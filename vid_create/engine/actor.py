"""
Module Actor - quản lý các actor nhân vật với assets hình ảnh và biến đổi.
"""

from typing import Tuple, Optional, Dict, Any
from pathlib import Path

import numpy as np
from PIL import Image
from moviepy import ImageClip


class Actor:
    """Đại diện cho một actor nhân vật với asset hình ảnh và thuộc tính biến đổi."""

    def __init__(
        self,
        actor_id: str,
        image_path: str,
        scale: float = 1.0,
        remove_white_bg: bool = False,
        white_bg_threshold: int = 240,
    ):
        """
        Khởi tạo một actor.

        Args:
            actor_id: Định danh duy nhất cho actor
            image_path: Đường dẫn đến file hình ảnh (PNG/JPEG)
            scale: Hệ số tỷ lệ cho actor (1.0 = kích thước gốc)
            remove_white_bg: Nếu True, tự động xóa nền trắng (tạo alpha)
            white_bg_threshold: Ngưỡng màu trắng (0–255), càng cao càng dễ bị ăn vào biên nhân vật
        """
        self.actor_id = actor_id
        self.image_path = Path(image_path)
        self.scale = scale
        self.remove_white_bg = remove_white_bg
        self.white_bg_threshold = white_bg_threshold

        if not self.image_path.exists():
            raise FileNotFoundError(f"Không tìm thấy hình ảnh actor: {self.image_path}")

        self._clip: Optional[ImageClip] = None
        self._base_width: Optional[int] = None
        self._base_height: Optional[int] = None
        self._scaled_width: Optional[int] = None
        self._scaled_height: Optional[int] = None

    def _load_pil_image(self) -> Image.Image:
        """Tải ảnh bằng Pillow, áp dụng xóa nền trắng và scale."""
        img = Image.open(self.image_path).convert("RGBA")
        self._base_width, self._base_height = img.size

        if self.remove_white_bg:
            # Chuyển sang numpy để xử lý alpha cho vùng gần trắng
            data = np.array(img)
            r = data[..., 0]
            g = data[..., 1]
            b = data[..., 2]

            thr = self.white_bg_threshold
            white_mask = (r >= thr) & (g >= thr) & (b >= thr)
            # Đặt alpha = 0 cho vùng nền trắng
            data[white_mask, 3] = 0

            img = Image.fromarray(data, mode="RGBA")

        # Scale bằng Pillow để tránh phụ thuộc resize trong MoviePy 2.x
        if self.scale != 1.0:
            new_w = max(1, int(self._base_width * self.scale))
            new_h = max(1, int(self._base_height * self.scale))
            img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
            self._scaled_width, self._scaled_height = new_w, new_h
        else:
            self._scaled_width, self._scaled_height = self._base_width, self._base_height

        return img

    def load_image(self) -> ImageClip:
        """Tải và scale clip hình ảnh của actor, có thể xóa nền trắng."""
        if self._clip is None:
            img = self._load_pil_image()
            arr = np.array(img)
            clip = ImageClip(arr)
            self._clip = clip

        return self._clip

    def get_dimensions(self) -> Tuple[int, int]:
        """Lấy kích thước đã scale của actor."""
        if self._scaled_width is None or self._scaled_height is None:
            self.load_image()

        return int(self._scaled_width), int(self._scaled_height)

    @staticmethod
    def from_json(actor_data: Dict[str, Any], assets_dir: Path) -> "Actor":
        """
        Tạo một instance Actor từ dữ liệu JSON.

        Args:
            actor_data: Dictionary với 'id', 'image', tùy chọn 'scale',
                        'remove_white_bg', 'white_bg_threshold'
            assets_dir: Thư mục cơ sở cho đường dẫn assets
        """
        actor_id = actor_data["id"]
        image_path = assets_dir / actor_data["image"]
        scale = actor_data.get("scale", 1.0)
        remove_white_bg = actor_data.get("remove_white_bg", False)
        white_bg_threshold = int(actor_data.get("white_bg_threshold", 240))

        return Actor(
            actor_id,
            str(image_path),
            scale=scale,
            remove_white_bg=remove_white_bg,
            white_bg_threshold=white_bg_threshold,
        )
