"""
Tiện ích validation script - xác thực script JSON trước khi render.
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any, List


def validate_script(script_data: Dict[str, Any], assets_dir: Path) -> List[str]:
    """
    Xác thực script và trả về danh sách lỗi.
    
    Args:
        script_data: Dữ liệu script JSON đã parse
        assets_dir: Thư mục cơ sở cho assets
    
    Returns:
        Danh sách thông báo lỗi (rỗng nếu hợp lệ)
    """
    errors = []
    
    # Xác thực metadata
    if 'metadata' not in script_data:
        errors.append("Thiếu phần 'metadata'")
    else:
        metadata = script_data['metadata']
        required_meta = ['width', 'height', 'fps']
        for key in required_meta:
            if key not in metadata:
                errors.append(f"Thiếu trường metadata: {key}")
            elif not isinstance(metadata[key], (int, float)) or metadata[key] <= 0:
                errors.append(f"metadata.{key} không hợp lệ: phải là số dương")
    
    # Xác thực scenes
    if 'scenes' not in script_data:
        errors.append("Thiếu phần 'scenes'")
        return errors
    
    scenes = script_data['scenes']
    if not isinstance(scenes, list) or len(scenes) == 0:
        errors.append("'scenes' phải là một mảng không rỗng")
        return errors
    
    # Xác thực từng scene
    for i, scene in enumerate(scenes):
        scene_errors = validate_scene(scene, i, assets_dir)
        errors.extend(scene_errors)
    
    return errors


def validate_scene(scene: Dict[str, Any], scene_index: int, assets_dir: Path) -> List[str]:
    """Xác thực một scene đơn."""
    errors = []
    prefix = f"Scene {scene_index}"
    
    # Xác thực background
    if 'background' not in scene:
        errors.append(f"{prefix}: Thiếu 'background'")
    else:
        bg_path = assets_dir / scene['background']
        if not bg_path.exists():
            errors.append(f"{prefix}: Không tìm thấy background: {bg_path}")
    
    # Xác thực actors
    if 'actors' not in scene:
        errors.append(f"{prefix}: Thiếu 'actors'")
    elif not isinstance(scene['actors'], list):
        errors.append(f"{prefix}: 'actors' phải là một mảng")
    else:
        actor_ids = set()
        for j, actor in enumerate(scene['actors']):
            actor_prefix = f"{prefix}, Actor {j}"
            if 'id' not in actor:
                errors.append(f"{actor_prefix}: Thiếu 'id'")
            else:
                actor_id = actor['id']
                if actor_id in actor_ids:
                    errors.append(f"{prefix}: ID actor trùng lặp: {actor_id}")
                actor_ids.add(actor_id)
            
            if 'image' not in actor:
                errors.append(f"{actor_prefix}: Thiếu 'image'")
            else:
                img_path = assets_dir / actor['image']
                if not img_path.exists():
                    errors.append(f"{actor_prefix}: Không tìm thấy hình ảnh: {img_path}")
    
    # Xác thực timeline
    if 'timeline' not in scene:
        errors.append(f"{prefix}: Thiếu 'timeline'")
    elif not isinstance(scene['timeline'], list):
        errors.append(f"{prefix}: 'timeline' phải là một mảng")
    else:
        timeline_errors = validate_timeline(scene['timeline'], scene.get('actors', []), prefix)
        errors.extend(timeline_errors)
    
    # Xác thực audio (tùy chọn)
    if 'audio' in scene:
        audio_errors = validate_audio(scene['audio'], assets_dir, prefix)
        errors.extend(audio_errors)
    
    return errors


def validate_timeline(timeline: List[Dict[str, Any]], actors: List[Dict[str, Any]], prefix: str) -> List[str]:
    """Xác thực sự kiện timeline."""
    errors = []
    actor_ids = {actor['id'] for actor in actors if 'id' in actor}
    
    for i, event in enumerate(timeline):
        event_prefix = f"{prefix}, Sự kiện timeline {i}"
        
        # Các trường bắt buộc
        if 'type' not in event:
            errors.append(f"{event_prefix}: Thiếu 'type'")
            continue
        
        if 'actor_id' not in event:
            errors.append(f"{event_prefix}: Thiếu 'actor_id'")
        elif event['actor_id'] not in actor_ids:
            errors.append(f"{event_prefix}: actor_id không xác định: {event['actor_id']}")
        
        if 'start_time' not in event:
            errors.append(f"{event_prefix}: Thiếu 'start_time'")
        elif not isinstance(event['start_time'], (int, float)) or event['start_time'] < 0:
            errors.append(f"{event_prefix}: 'start_time' không hợp lệ: phải là số không âm")
        
        if 'duration' not in event:
            errors.append(f"{event_prefix}: Thiếu 'duration'")
        elif not isinstance(event['duration'], (int, float)) or event['duration'] < 0:
            errors.append(f"{event_prefix}: 'duration' không hợp lệ: phải là số không âm")
        
        # Xác thực trường cụ thể cho sự kiện
        event_type = event.get('type', '').lower()
        if event_type == 'spawn':
            if 'position' not in event:
                errors.append(f"{event_prefix}: Sự kiện spawn thiếu 'position'")
            elif not isinstance(event['position'], list) or len(event['position']) != 2:
                errors.append(f"{event_prefix}: 'position' của spawn phải là [x, y]")
        
        elif event_type == 'move':
            if 'from' not in event:
                errors.append(f"{event_prefix}: Sự kiện move thiếu 'from'")
            elif not isinstance(event['from'], list) or len(event['from']) != 2:
                errors.append(f"{event_prefix}: 'from' của move phải là [x, y]")
            
            if 'to' not in event:
                errors.append(f"{event_prefix}: Sự kiện move thiếu 'to'")
            elif not isinstance(event['to'], list) or len(event['to']) != 2:
                errors.append(f"{event_prefix}: 'to' của move phải là [x, y]")
        
        elif event_type == 'exit':
            if 'position' not in event:
                errors.append(f"{event_prefix}: Sự kiện exit thiếu 'position'")
            elif not isinstance(event['position'], list) or len(event['position']) != 2:
                errors.append(f"{event_prefix}: 'position' của exit phải là [x, y]")
    
    return errors


def validate_audio(audio: Dict[str, Any], assets_dir: Path, prefix: str) -> List[str]:
    """Xác thực cấu hình audio."""
    errors = []
    
    for track_type in ['dialog', 'music', 'sfx']:
        if track_type not in audio:
            continue
        
        tracks = audio[track_type]
        if not isinstance(tracks, list):
            errors.append(f"{prefix}: Audio '{track_type}' phải là một mảng")
            continue
        
        for i, track in enumerate(tracks):
            track_prefix = f"{prefix}, Audio {track_type}[{i}]"
            if 'file' not in track:
                errors.append(f"{track_prefix}: Thiếu 'file'")
            else:
                file_path = assets_dir / track['file']
                if not file_path.exists():
                    errors.append(f"{track_prefix}: Không tìm thấy file: {file_path}")
            
            if 'start_time' not in track:
                errors.append(f"{track_prefix}: Thiếu 'start_time'")
            elif not isinstance(track['start_time'], (int, float)) or track['start_time'] < 0:
                errors.append(f"{track_prefix}: 'start_time' không hợp lệ: phải là số không âm")
    
    return errors


def main():
    """Hàm validation chính."""
    if len(sys.argv) < 2:
        print("Cách sử dụng: python validate_script.py <script.json> [assets_dir]")
        sys.exit(1)
    
    script_path = Path(sys.argv[1])
    assets_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else Path('assets')
    
    if not script_path.exists():
        print(f"Lỗi: Không tìm thấy file script: {script_path}")
        sys.exit(1)
    
    try:
        with open(script_path, 'r', encoding='utf-8') as f:
            script_data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Lỗi: JSON không hợp lệ: {e}")
        sys.exit(1)
    
    errors = validate_script(script_data, assets_dir)
    
    if errors:
        print("Tìm thấy lỗi validation:")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)
    else:
        print("Validation script thành công!")
        sys.exit(0)


if __name__ == '__main__':
    main()
