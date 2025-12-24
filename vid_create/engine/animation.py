"""
Module Animation - hệ thống animation dựa trên keyframe với nội suy.
"""

from typing import List, Tuple, Callable, Optional
from enum import Enum


class EasingType(Enum):
    """Các loại hàm easing cho animation."""
    LINEAR = "linear"
    EASE_IN = "ease_in"
    EASE_OUT = "ease_out"
    EASE_IN_OUT = "ease_in_out"


class Keyframe:
    """Đại diện cho một keyframe đơn trong animation."""
    
    def __init__(self, time: float, value: Tuple[float, float], easing: EasingType = EasingType.LINEAR):
        """
        Khởi tạo một keyframe.
        
        Args:
            time: Thời gian tính bằng giây (tương đối với điểm bắt đầu animation)
            value: Tuple vị trí (x, y) hoặc giá trị khác
            easing: Loại easing cho nội suy từ keyframe này
        """
        self.time = time
        self.value = value
        self.easing = easing


class Animation:
    """Quản lý animation dựa trên keyframe với nội suy."""
    
    def __init__(self, keyframes: List[Keyframe], duration: float):
        """
        Khởi tạo animation với keyframes.
        
        Args:
            keyframes: Danh sách keyframes, phải được sắp xếp theo thời gian
            duration: Tổng thời lượng của animation tính bằng giây
        """
        self.keyframes = sorted(keyframes, key=lambda k: k.time)
        self.duration = duration
        
        if not self.keyframes:
            raise ValueError("Animation phải có ít nhất một keyframe")
        
        # Đảm bảo keyframe đầu tiên ở thời điểm 0
        if self.keyframes[0].time != 0:
            raise ValueError("Keyframe đầu tiên phải ở thời điểm 0")
    
    def get_value_at(self, t: float) -> Tuple[float, float]:
        """
        Lấy giá trị nội suy tại thời điểm t (0 đến duration).
        
        Args:
            t: Thời gian tính bằng giây (bị giới hạn trong [0, duration])
        
        Returns:
            Tuple vị trí nội suy (x, y)
        """
        t = max(0, min(t, self.duration))
        
        # Tìm hai keyframe để nội suy giữa chúng
        if t == 0:
            return self.keyframes[0].value
        
        if t >= self.duration:
            return self.keyframes[-1].value
        
        # Tìm các keyframe xung quanh
        prev_kf = self.keyframes[0]
        next_kf = self.keyframes[-1]
        
        for i, kf in enumerate(self.keyframes):
            if kf.time > t:
                next_kf = kf
                prev_kf = self.keyframes[i - 1]
                break
        
        # Nội suy giữa prev_kf và next_kf
        segment_duration = next_kf.time - prev_kf.time
        if segment_duration == 0:
            return prev_kf.value
        
        local_t = (t - prev_kf.time) / segment_duration
        eased_t = self._apply_easing(local_t, prev_kf.easing)
        
        # Nội suy tuyến tính
        x = prev_kf.value[0] + (next_kf.value[0] - prev_kf.value[0]) * eased_t
        y = prev_kf.value[1] + (next_kf.value[1] - prev_kf.value[1]) * eased_t
        
        return (x, y)
    
    def _apply_easing(self, t: float, easing: EasingType) -> float:
        """
        Áp dụng hàm easing cho thời gian chuẩn hóa t (0 đến 1).
        
        Args:
            t: Thời gian chuẩn hóa [0, 1]
            easing: Loại easing
        
        Returns:
            Giá trị thời gian đã được easing [0, 1]
        """
        if easing == EasingType.LINEAR:
            return t
        elif easing == EasingType.EASE_IN:
            return t * t
        elif easing == EasingType.EASE_OUT:
            return 1 - (1 - t) * (1 - t)
        elif easing == EasingType.EASE_IN_OUT:
            if t < 0.5:
                return 2 * t * t
            else:
                return 1 - 2 * (1 - t) * (1 - t)
        else:
            return t
    
    def create_position_function(self, start_time: float = 0.0) -> Callable[[float], Tuple[float, float]]:
        """
        Tạo hàm vị trí tương thích với tham số position của moviepy.
        
        Args:
            start_time: Thời điểm bắt đầu toàn cục của animation này
        
        Returns:
            Hàm nhận thời gian toàn cục và trả về vị trí (x, y)
        """
        def position_func(t: float) -> Tuple[float, float]:
            local_t = t - start_time
            if local_t < 0:
                return self.keyframes[0].value
            if local_t > self.duration:
                return self.keyframes[-1].value
            return self.get_value_at(local_t)
        
        return position_func
    
    @staticmethod
    def from_move_event(event_data: dict, duration: float) -> "Animation":
        """
        Tạo Animation từ dữ liệu sự kiện move JSON.

        Args:
            event_data: Dictionary với 'from', 'to' và tùy chọn 'easing'
            duration: Thời lượng chuyển động (giây), thường lấy từ TimelineEvent.duration
        """
        from_pos = tuple(event_data["from"])
        to_pos = tuple(event_data["to"])
        easing_str = event_data.get("easing", "linear")

        easing = EasingType(easing_str.lower())

        keyframes = [
            Keyframe(0.0, from_pos, easing),
            Keyframe(duration, to_pos, easing),
        ]

        return Animation(keyframes, duration)
