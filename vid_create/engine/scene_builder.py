"""
Module Scene builder - xây dựng clip moviepy từ định nghĩa scene.
"""

from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
from moviepy import ImageClip, CompositeVideoClip, VideoClip, vfx

from .actor import Actor
from .timeline import Timeline, TimelineEvent, EventType
from .animation import Animation, Keyframe, EasingType
from .audio import AudioManager


class SceneBuilder:
    """Xây dựng video clip từ định nghĩa scene."""
    
    def __init__(self, width: int, height: int, fps: int = 30):
        """
        Khởi tạo scene builder.
        
        Args:
            width: Chiều rộng video tính bằng pixel
            height: Chiều cao video tính bằng pixel
            fps: Khung hình mỗi giây
        """
        self.width = width
        self.height = height
        self.fps = fps
    
    def build_scene(
        self,
        background_path: Path,
        actors: Dict[str, Actor],
        timeline: Timeline,
        audio_manager: Optional[AudioManager] = None
    ) -> VideoClip:
        """
        Xây dựng clip scene hoàn chỉnh từ các thành phần.
        
        Args:
            background_path: Đường dẫn đến hình nền
            actors: Dictionary ánh xạ actor_id đến instance Actor
            timeline: Timeline với các sự kiện
            audio_manager: Audio manager tùy chọn cho audio scene
        
        Returns:
            CompositeVideoClip đại diện cho scene
        """
        if not background_path.exists():
            raise FileNotFoundError(f"Không tìm thấy hình nền: {background_path}")
        
        # Tạo clip nền (MoviePy 2.x dùng with_duration/with_size thay cho set_duration/resize)
        bg_clip = ImageClip(str(background_path)).with_duration(
            timeline.get_total_duration()
        )
        bg_clip = bg_clip.with_effects([vfx.Resize((self.width, self.height))])
        
        # Xây dựng clip actor
        actor_clips = []
        
        for actor_id, actor in actors.items():
            actor_events = timeline.get_events_for_actor(actor_id)
            if not actor_events:
                continue
            
            actor_clip = self._build_actor_clip(actor, actor_events, timeline.get_total_duration())
            if actor_clip:
                actor_clips.append(actor_clip)
        
        # Composite tất cả clip
        all_clips = [bg_clip] + actor_clips
        final_clip = CompositeVideoClip(all_clips, size=(self.width, self.height))
        
        # Thêm audio nếu có (MoviePy 2.x: with_audio)
        if audio_manager:
            audio_clip = audio_manager.create_composite_audio(final_clip.duration)
            if audio_clip:
                final_clip = final_clip.with_audio(audio_clip)
        
        # MoviePy 2.x: with_fps thay cho set_fps
        return final_clip.with_fps(self.fps)
    
    def _build_actor_clip(
        self,
        actor: Actor,
        events: List[TimelineEvent],
        total_duration: float
    ) -> Optional[VideoClip]:
        """
        Xây dựng video clip cho một actor dựa trên sự kiện timeline.
        
        Args:
            actor: Instance Actor
            events: Sự kiện timeline cho actor này
            total_duration: Tổng thời lượng của scene
        
        Returns:
            VideoClip cho actor hoặc None nếu actor không bao giờ xuất hiện
        """
        # Tìm sự kiện spawn
        spawn_event = next((e for e in events if e.event_type == EventType.SPAWN), None)
        if not spawn_event:
            return None
        
        # Tải hình ảnh actor
        actor_image = actor.load_image()
        actor_w, actor_h = actor.get_dimensions()
        
        # Xác định khoảng thời gian hiển thị actor
        spawn_time = spawn_event.start_time
        exit_event = next((e for e in events if e.event_type == EventType.EXIT), None)
        exit_time = exit_event.end_time if exit_event else total_duration
        
        actor_duration = exit_time - spawn_time
        if actor_duration <= 0:
            return None
        
        # Tạo clip cơ sở
        # MoviePy 2.x: dùng with_duration/with_start thay cho set_duration/set_start
        actor_clip = actor_image.with_duration(actor_duration).with_start(spawn_time)
        
        # Xây dựng hàm vị trí từ sự kiện
        position_func = self._build_position_function(actor, events, spawn_time)
        
        # Áp dụng hàm vị trí (MoviePy 2.x: with_position)
        actor_clip = actor_clip.with_position(position_func)
        
        return actor_clip
    
    def _build_position_function(
        self,
        actor: Actor,
        events: List[TimelineEvent],
        spawn_time: float
    ) -> callable:
        """
        Xây dựng hàm vị trí cho một actor dựa trên sự kiện timeline.
        
        Args:
            actor: Instance Actor
            events: Sự kiện timeline cho actor này
            spawn_time: Khi actor spawn
        
        Returns:
            Hàm vị trí nhận thời gian t và trả về (x, y)
        """
        actor_w, actor_h = actor.get_dimensions()
        
        # Lấy vị trí ban đầu từ sự kiện spawn
        spawn_event = next((e for e in events if e.event_type == EventType.SPAWN), None)
        if not spawn_event:
            raise ValueError("Actor phải có sự kiện spawn")
        
        initial_pos = tuple(spawn_event.data.get('position', (self.width // 2, self.height // 2)))
        current_pos = initial_pos
        
        # Xây dựng timeline vị trí
        position_segments = []
        
        for event in sorted(events, key=lambda e: e.start_time):
            if event.event_type == EventType.SPAWN:
                pos = tuple(event.data.get('position', initial_pos))
                position_segments.append({
                    'start_time': event.start_time,
                    'end_time': event.end_time,
                    'position': pos
                })
                current_pos = pos
            
            elif event.event_type == EventType.MOVE:
                # Tạo animation cho chuyển động (duration lấy từ TimelineEvent.duration)
                animation = Animation.from_move_event(event.data, event.duration)
                position_segments.append({
                    'start_time': event.start_time,
                    'end_time': event.end_time,
                    'animation': animation
                })
                # Cập nhật vị trí hiện tại đến đích
                current_pos = tuple(event.data['to'])
            
            elif event.event_type == EventType.IDLE:
                # Giữ nguyên vị trí hiện tại
                position_segments.append({
                    'start_time': event.start_time,
                    'end_time': event.end_time,
                    'position': current_pos
                })
            
            elif event.event_type == EventType.EXIT:
                # Di chuyển đến vị trí exit
                exit_pos = tuple(event.data.get('position', (-actor_w, current_pos[1])))
                position_segments.append({
                    'start_time': event.start_time,
                    'end_time': event.end_time,
                    'position': exit_pos
                })
                current_pos = exit_pos
        
        def position_func(t: float) -> Tuple[float, float]:
            """Tính toán vị trí tại thời điểm t."""
            # Tìm segment liên quan
            for segment in position_segments:
                if segment['start_time'] <= t < segment['end_time']:
                    if 'animation' in segment:
                        center_pos = segment['animation'].get_value_at(t - segment['start_time'])
                        # Điều chỉnh cho trung tâm actor (moviepy sử dụng góc trên bên trái)
                        return (center_pos[0] - actor_w // 2, center_pos[1] - actor_h // 2)
                    else:
                        pos = segment['position']
                        # Điều chỉnh cho trung tâm actor (moviepy sử dụng góc trên bên trái)
                        return (pos[0] - actor_w // 2, pos[1] - actor_h // 2)
            
            # Mặc định về vị trí đã biết cuối cùng
            return (current_pos[0] - actor_w // 2, current_pos[1] - actor_h // 2)
        
        return position_func
