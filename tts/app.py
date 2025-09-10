#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import io
import base64
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from TTS.api import TTS
import torch
import logging
import tempfile
import uuid

# Thiết lập logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

class VietnameseTTS:
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Sử dụng device: {self.device}")
        
        # Khởi tạo TTS models
        self.models = {}
        self.init_models()
    
    def init_models(self):
        """Khởi tạo các model TTS"""
        try:
            # Model đa ngôn ngữ hỗ trợ tiếng Việt
            logger.info("Đang tải model TTS đa ngôn ngữ...")
            self.models['multilingual'] = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(self.device)
            
            # Model Tacotron2 cho tiếng Việt (nếu có)
            try:
                logger.info("Đang tải model Tacotron2 cho tiếng Việt...")
                self.models['vietnamese'] = TTS("tts_models/vi/cv/vits").to(self.device)
            except Exception as e:
                logger.warning(f"Không thể tải model tiếng Việt chuyên dụng: {e}")
            
            logger.info("Khởi tạo models thành công!")
            
        except Exception as e:
            logger.error(f"Lỗi khi khởi tạo models: {e}")
            raise
    
    def synthesize(self, text, model_name="multilingual", speaker_wav=None, language="vi"):
        """
        Tổng hợp giọng nói từ text
        
        Args:
            text (str): Văn bản cần đọc
            model_name (str): Tên model sử dụng
            speaker_wav (str): Đường dẫn tới file audio mẫu (cho voice cloning)
            language (str): Mã ngôn ngữ
        
        Returns:
            str: Đường dẫn tới file audio được tạo
        """
        try:
            # Tạo tên file unique
            output_filename = f"output_{uuid.uuid4().hex}.wav"
            output_path = os.path.join("/app/output", output_filename)
            
            model = self.models.get(model_name, self.models['multilingual'])
            
            if model_name == "multilingual" and speaker_wav:
                # Sử dụng voice cloning với XTTS
                model.tts_to_file(
                    text=text,
                    file_path=output_path,
                    speaker_wav=speaker_wav,
                    language=language
                )
            elif model_name == "vietnamese" and "vietnamese" in self.models:
                # Sử dụng model tiếng Việt chuyên dụng
                model.tts_to_file(
                    text=text,
                    file_path=output_path
                )
            else:
                # Sử dụng model mặc định
                model.tts_to_file(
                    text=text,
                    file_path=output_path,
                    language=language
                )
            
            return output_path
            
        except Exception as e:
            logger.error(f"Lỗi khi tổng hợp giọng nói: {e}")
            raise

# Khởi tạo TTS engine
tts_engine = VietnameseTTS()

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "models": list(tts_engine.models.keys())})

@app.route('/models', methods=['GET'])
def get_models():
    """Lấy danh sách models khả dụng"""
    return jsonify({
        "available_models": list(tts_engine.models.keys()),
        "device": tts_engine.device
    })

@app.route('/synthesize', methods=['POST'])
def synthesize_text():
    """
    API endpoint để tổng hợp giọng nói
    
    Body JSON:
    {
        "text": "Văn bản cần đọc",
        "model": "multilingual|vietnamese",
        "language": "vi",
        "speaker_wav_base64": "base64_encoded_audio" (tùy chọn)
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({"error": "Thiếu trường 'text' trong request"}), 400
        
        text = data['text']
        model_name = data.get('model', 'multilingual')
        language = data.get('language', 'vi')
        speaker_wav_base64 = data.get('speaker_wav_base64')
        
        # Xử lý speaker audio nếu có
        speaker_wav_path = None
        if speaker_wav_base64:
            try:
                # Decode base64 audio
                audio_data = base64.b64decode(speaker_wav_base64)
                
                # Lưu vào file tạm
                with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
                    tmp_file.write(audio_data)
                    speaker_wav_path = tmp_file.name
                    
            except Exception as e:
                logger.error(f"Lỗi khi xử lý speaker audio: {e}")
                return jsonify({"error": "Lỗi khi xử lý speaker audio"}), 400
        
        # Tổng hợp giọng nói
        output_path = tts_engine.synthesize(
            text=text,
            model_name=model_name,
            speaker_wav=speaker_wav_path,
            language=language
        )
        
        # Cleanup temporary file
        if speaker_wav_path and os.path.exists(speaker_wav_path):
            os.unlink(speaker_wav_path)
        
        # Đọc file audio và trả về base64
        with open(output_path, 'rb') as audio_file:
            audio_data = audio_file.read()
            audio_base64 = base64.b64encode(audio_data).decode('utf-8')
        
        # Cleanup output file
        os.unlink(output_path)
        
        return jsonify({
            "success": True,
            "audio_base64": audio_base64,
            "text": text,
            "model_used": model_name,
            "language": language
        })
        
    except Exception as e:
        logger.error(f"Lỗi trong API synthesize: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/synthesize_file', methods=['POST'])
def synthesize_to_file():
    """
    API endpoint để tổng hợp giọng nói và trả về file audio
    """
    try:
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({"error": "Thiếu trường 'text' trong request"}), 400
        
        text = data['text']
        model_name = data.get('model', 'multilingual')
        language = data.get('language', 'vi')
        
        # Tổng hợp giọng nói
        output_path = tts_engine.synthesize(
            text=text,
            model_name=model_name,
            language=language
        )
        
        # Trả về file audio
        return send_file(
            output_path,
            as_attachment=True,
            download_name=f"tts_output_{uuid.uuid4().hex[:8]}.wav",
            mimetype="audio/wav"
        )
        
    except Exception as e:
        logger.error(f"Lỗi trong API synthesize_file: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/', methods=['GET'])
def index():
    """Trang chủ với giao diện demo"""
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Vietnamese TTS with Coqui</title>
        <meta charset="UTF-8">
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
            .container { background: #f5f5f5; padding: 20px; border-radius: 10px; }
            textarea { width: 100%; height: 100px; margin: 10px 0; }
            button { background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; }
            button:hover { background: #0056b3; }
            audio { width: 100%; margin: 10px 0; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎤 Vietnamese Text-to-Speech</h1>
            <p>Nhập văn bản tiếng Việt để chuyển đổi thành giọng nói:</p>
            
            <textarea id="textInput" placeholder="Nhập văn bản tiếng Việt ở đây...">Xin chào, tôi là hệ thống chuyển đổi văn bản thành giọng nói tiếng Việt.</textarea>
            
            <div>
                <label>Model: </label>
                <select id="modelSelect">
                    <option value="multilingual">Multilingual (XTTS)</option>
                    <option value="vietnamese">Vietnamese (VITS)</option>
                </select>
            </div>
            
            <button onclick="synthesize()">🎵 Tạo giọng nói</button>
            
            <div id="loading" style="display: none;">Đang xử lý...</div>
            <div id="error" style="color: red; display: none;"></div>
            
            <audio id="audioPlayer" controls style="display: none;"></audio>
        </div>
        
        <script>
            async function synthesize() {
                const text = document.getElementById('textInput').value;
                const model = document.getElementById('modelSelect').value;
                const loading = document.getElementById('loading');
                const error = document.getElementById('error');
                const audioPlayer = document.getElementById('audioPlayer');
                
                if (!text.trim()) {
                    alert('Vui lòng nhập văn bản!');
                    return;
                }
                
                loading.style.display = 'block';
                error.style.display = 'none';
                audioPlayer.style.display = 'none';
                
                try {
                    const response = await fetch('/synthesize', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            text: text,
                            model: model,
                            language: 'vi'
                        })
                    });
                    
                    const result = await response.json();
                    
                    if (result.success) {
                        const audioBlob = new Blob([
                            Uint8Array.from(atob(result.audio_base64), c => c.charCodeAt(0))
                        ], { type: 'audio/wav' });
                        
                        const audioUrl = URL.createObjectURL(audioBlob);
                        audioPlayer.src = audioUrl;
                        audioPlayer.style.display = 'block';
                    } else {
                        error.textContent = result.error || 'Có lỗi xảy ra';
                        error.style.display = 'block';
                    }
                } catch (err) {
                    error.textContent = 'Lỗi kết nối: ' + err.message;
                    error.style.display = 'block';
                } finally {
                    loading.style.display = 'none';
                }
            }
        </script>
    </body>
    </html>
    '''

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)