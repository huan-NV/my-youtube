"""
Module Renderer - điều phối render scene và tạo thành phần video cuối cùng.
"""

from typing import List, Dict, Any
from pathlib import Path
from moviepy import concatenate_videoclips, VideoClip

from .scene_builder import SceneBuilder
from .actor import Actor
from .timeline import Timeline
from .audio import AudioManager


class Renderer:
    """Renderer chính điều phối việc tạo video."""
    
    def __init__(self, script_data: Dict[str, Any], assets_dir: Path):
        """
        Khởi tạo renderer với dữ liệu script.
        
        Args:
            script_data: Dữ liệu script JSON đã parse
            assets_dir: Thư mục cơ sở cho assets
        """
        self.script_data = script_data
        self.assets_dir = Path(assets_dir)
        
        # Trích xuất metadata
        metadata = script_data.get('metadata', {})
        self.width = metadata.get('width', 1920)
        self.height = metadata.get('height', 1080)
        self.fps = metadata.get('fps', 30)
        
        self.scene_builder = SceneBuilder(self.width, self.height, self.fps)
    
    def render(self, output_path: Path) -> None:
        """
        Render video hoàn chỉnh từ script.
        
        Args:
            output_path: Đường dẫn để lưu file MP4 output
        """
        scenes_data = self.script_data.get('scenes', [])
        
        if not scenes_data:
            raise ValueError("Script phải chứa ít nhất một scene")
        
        scene_clips = []
        
        for scene_data in scenes_data:
            scene_clip = self._render_scene(scene_data)
            scene_clips.append(scene_clip)
        
        # Nối tất cả scenes
        final_clip = concatenate_videoclips(scene_clips, method="compose")
        
        # Ghi output
        print(f"Đang render video đến {output_path}...")
        final_clip.write_videofile(
            str(output_path),
            fps=self.fps,
            codec='libx264',
            audio_codec='aac',
            preset='medium',
            threads=4
        )
        
        # Dọn dẹp
        final_clip.close()
        for clip in scene_clips:
            clip.close()
        
        print(f"Video đã được render thành công: {output_path}")
    
    def _render_scene(self, scene_data: Dict[str, Any]) -> VideoClip:
        """
        Render một scene đơn.
        
        Args:
            scene_data: Dữ liệu scene từ JSON
        
        Returns:
            VideoClip cho scene
        """
        # Tải actors
        actors = {}
        for actor_data in scene_data.get('actors', []):
            actor = Actor.from_json(actor_data, self.assets_dir)
            actors[actor.actor_id] = actor
        
        # Xây dựng timeline
        timeline = Timeline.from_json(scene_data.get('timeline', []))
        
        # Tải background
        background_path = self.assets_dir / scene_data['background']
        
        # Tải audio nếu có
        audio_manager = None
        if 'audio' in scene_data:
            audio_manager = AudioManager.from_json(scene_data['audio'], self.assets_dir)
        
        # Xây dựng scene
        scene_clip = self.scene_builder.build_scene(
            background_path=background_path,
            actors=actors,
            timeline=timeline,
            audio_manager=audio_manager
        )
        
        return scene_clip
