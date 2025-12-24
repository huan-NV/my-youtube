"""
Module Audio - quản lý track audio và đồng bộ.
"""

from typing import List, Optional, Dict, Any
from pathlib import Path
from moviepy import AudioFileClip, CompositeAudioClip
from dataclasses import dataclass


@dataclass
class AudioTrack:
    """Đại diện cho một track audio với thông tin timing."""
    file_path: Path
    start_time: float
    volume: float = 1.0
    loop: bool = False
    
    def __post_init__(self):
        """Xác thực track audio."""
        if not self.file_path.exists():
            raise FileNotFoundError(f"Không tìm thấy file audio: {self.file_path}")


class AudioManager:
    """Quản lý track audio và tạo composite audio cho scenes."""
    
    def __init__(self, tracks: List[AudioTrack]):
        """
        Khởi tạo audio manager với các track.
        
        Args:
            tracks: Danh sách track audio
        """
        self.tracks = tracks
    
    def create_composite_audio(self, duration: float) -> Optional[CompositeAudioClip]:
        """
        Tạo composite audio clip từ tất cả các track.
        
        Args:
            duration: Tổng thời lượng của video tính bằng giây
        
        Returns:
            CompositeAudioClip hoặc None nếu không có track audio
        """
        if not self.tracks:
            return None
        
        audio_clips = []
        
        for track in self.tracks:
            try:
                clip = AudioFileClip(str(track.file_path))
                
                # Áp dụng volume
                if track.volume != 1.0:
                    clip = clip.volumex(track.volume)
                
                # Xử lý lặp cho nhạc nền
                if track.loop and clip.duration < duration:
                    # Tính số lần lặp cần thiết
                    loops_needed = int(duration / clip.duration) + 1
                    clip = clip.loop(duration=loops_needed * clip.duration)
                
                # Đặt thời điểm bắt đầu (MoviePy 2.x: with_start)
                clip = clip.with_start(track.start_time)
                
                # Cắt theo thời lượng
                clip = clip.subclip(0, min(clip.duration, duration - track.start_time))
                
                audio_clips.append(clip)
            except Exception as e:
                print(f"Cảnh báo: Không thể tải track audio {track.file_path}: {e}")
                continue
        
        if not audio_clips:
            return None
        
        return CompositeAudioClip(audio_clips)
    
    @staticmethod
    def from_json(audio_data: Dict[str, Any], assets_dir: Path) -> 'AudioManager':
        """
        Tạo AudioManager từ dữ liệu JSON.
        
        Args:
            audio_data: Dictionary với các mảng 'dialog', 'music', 'sfx'
            assets_dir: Thư mục cơ sở cho đường dẫn assets
        
        Returns:
            Instance AudioManager
        """
        tracks = []
        
        # Xử lý track dialog
        for dialog in audio_data.get('dialog', []):
            file_path = assets_dir / dialog['file']
            start_time = float(dialog['start_time'])
            volume = float(dialog.get('volume', 1.0))
            
            tracks.append(AudioTrack(
                file_path=file_path,
                start_time=start_time,
                volume=volume,
                loop=False
            ))
        
        # Xử lý nhạc nền
        for music in audio_data.get('music', []):
            file_path = assets_dir / music['file']
            start_time = float(music.get('start_time', 0.0))
            volume = float(music.get('volume', 0.5))  # Volume mặc định thấp hơn cho nhạc
            loop = music.get('loop', True)
            
            tracks.append(AudioTrack(
                file_path=file_path,
                start_time=start_time,
                volume=volume,
                loop=loop
            ))
        
        # Xử lý hiệu ứng âm thanh
        for sfx in audio_data.get('sfx', []):
            file_path = assets_dir / sfx['file']
            start_time = float(sfx['start_time'])
            volume = float(sfx.get('volume', 1.0))
            
            tracks.append(AudioTrack(
                file_path=file_path,
                start_time=start_time,
                volume=volume,
                loop=False
            ))
        
        return AudioManager(tracks)
