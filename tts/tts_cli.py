#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import os
from TTS.api import TTS
import torch

def main():
    parser = argparse.ArgumentParser(description='Vietnamese Text-to-Speech CLI')
    parser.add_argument('--text', '-t', required=True, help='Văn bản cần chuyển đổi')
    parser.add_argument('--output', '-o', default='output.wav', help='File đầu ra (default: output.wav)')
    parser.add_argument('--model', '-m', default='multilingual', 
                       choices=['multilingual', 'vietnamese'],
                       help='Model sử dụng (default: multilingual)')
    parser.add_argument('--speaker', '-s', help='File audio mẫu cho voice cloning')
    parser.add_argument('--language', '-l', default='vi', help='Mã ngôn ngữ (default: vi)')
    parser.add_argument('--device', '-d', help='Device sử dụng (cuda/cpu)')
    
    args = parser.parse_args()
    
    # Xác định device
    if args.device:
        device = args.device
    else:
        device = "cuda" if torch.cuda.is_available() else "cpu"
    
    print(f"🚀 Khởi tạo TTS với device: {device}")
    
    try:
        # Khởi tạo model
        if args.model == 'multilingual':
            tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)
        else:
            try:
                tts = TTS("tts_models/vi/cv/vits").to(device)
            except:
                print("⚠️ Model tiếng Việt không khả dụng, chuyển sang multilingual")
                tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)
        
        print(f"📝 Văn bản: {args.text}")
        print(f"🎵 Đang tạo file audio: {args.output}")
        
        # Tổng hợp giọng nói
        if args.speaker and os.path.exists(args.speaker):
            print(f"🎤 Sử dụng voice cloning với file: {args.speaker}")
            tts.tts_to_file(
                text=args.text,
                file_path=args.output,
                speaker_wav=args.speaker,
                language=args.language
            )
        else:
            tts.tts_to_file(
                text=args.text,
                file_path=args.output,
                language=args.language
            )
        
        print(f"✅ Hoàn thành! File audio đã được lưu: {args.output}")
        
    except Exception as e:
        print(f"❌ Lỗi: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())