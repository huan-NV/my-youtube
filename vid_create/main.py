"""
Điểm vào chính cho engine render video.
"""

import json
import argparse
from pathlib import Path
from engine import Renderer


def main():
    """Hàm chính để chạy video renderer."""
    parser = argparse.ArgumentParser(description='Engine Render Video Offline')
    parser.add_argument(
        'script',
        type=str,
        help='Đường dẫn đến file script JSON'
    )
    parser.add_argument(
        '--assets',
        type=str,
        default='assets',
        help='Đường dẫn đến thư mục assets (mặc định: assets)'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='output/video.mp4',
        help='Đường dẫn đến file video output (mặc định: output/video.mp4)'
    )
    
    args = parser.parse_args()
    
    # Tải script
    script_path = Path(args.script)
    if not script_path.exists():
        print(f"Lỗi: Không tìm thấy file script: {script_path}")
        return 1
    
    with open(script_path, 'r', encoding='utf-8') as f:
        script_data = json.load(f)
    
    # Khởi tạo renderer
    assets_dir = Path(args.assets)
    renderer = Renderer(script_data, assets_dir)
    
    # Render video
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        renderer.render(output_path)
        return 0
    except Exception as e:
        print(f"Lỗi trong quá trình render: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    exit(main())
