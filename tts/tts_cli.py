#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import os
from TTS.api import TTS
import torch
from torch.serialization import safe_globals
from TTS.tts.configs.xtts_config import XttsConfig
from TTS.tts.models.xtts import XttsAudioConfig, XttsArgs
from TTS.config.shared_configs import BaseDatasetConfig

def main():
    # Thêm XttsConfig vào safe globals để cho phép load weights
    torch.serialization.add_safe_globals([XttsConfig])
    
    parser = argparse.ArgumentParser(description='Vietnamese Text-to-Speech CLI')
    parser.add_argument('--text', '-t', required=True, help='Văn bản cần chuyển đổi')
    parser.add_argument('--output', '-o', default='output.mp3', help='File đầu ra (default: output.mp3)')
    parser.add_argument('--model', '-m', default='multilingual', 
                       choices=['multilingual', 'vietnamese'],
                       help='Model sử dụng (default: multilingual)')
    parser.add_argument('--speaker', '-s', required=True, help='File audio mẫu (mp3/wav) cho voice cloning (bắt buộc cho model multilingual)')
    parser.add_argument('--language', '-l', default='en', 
                       choices=['en', 'es', 'fr', 'de', 'it', 'pt', 'pl', 'tr', 'ru', 'nl', 'cs', 'ar', 'zh-cn', 'hu', 'ko', 'ja', 'hi'],
                       help='Mã ngôn ngữ cho XTTS (default: en). Đối với văn bản tiếng Việt, dùng "en" vẫn hoạt động tốt')
    parser.add_argument('--device', '-d', help='Device sử dụng (cuda/cpu)')
    
    args = parser.parse_args()
    
    # Xác định device
    if args.device:
        device = args.device
    else:
        device = "cuda" if torch.cuda.is_available() else "cpu"
    
    print(f"🚀 Khởi tạo TTS với device: {device}")
    
    try:
        # Khởi tạo model với use_gpu và progress bar
        if args.model == 'multilingual':
            with torch.serialization.safe_globals([XttsConfig, XttsAudioConfig, XttsArgs, BaseDatasetConfig]):
                tts = TTS(model_name="tts_models/multilingual/multi-dataset/xtts_v2", 
                         progress_bar=True, 
                         gpu=True if device == "cuda" else False).to(device)
        else:
            try:
                tts = TTS("tts_models/vi/cv/vits").to(device)
            except:
                print("⚠️ Model tiếng Việt không khả dụng, chuyển sang multilingual")
                tts = TTS(model_name="tts_models/multilingual/multi-dataset/xtts_v2",
                         progress_bar=True,
                         gpu=True if device == "cuda" else False).to(device)
        
        print(f"📝 Văn bản: {args.text}")
        print(f"🎵 Đang tạo file audio: {args.output}")
        
        # Kiểm tra file audio mẫu tồn tại
        if not os.path.exists(args.speaker):
            raise Exception(f"File audio mẫu không tồn tại: {args.speaker}")
        
        # Kiểm tra định dạng file audio mẫu
        speaker_ext = os.path.splitext(args.speaker)[1].lower()
        if speaker_ext not in ['.mp3', '.wav']:
            raise Exception(f"File audio mẫu phải có định dạng .mp3 hoặc .wav: {args.speaker}")
            
        print(f"🎤 Sử dụng voice cloning với file: {args.speaker}")
        # Tổng hợp giọng nói
        tts.tts_to_file(
            text=args.text,
            file_path=args.output,
            speaker_wav=args.speaker,
            language=args.language
        )
        
        print(f"✅ Hoàn thành! File audio đã được lưu: {args.output}")
        
    except Exception as e:
        print(f"❌ Lỗi: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())