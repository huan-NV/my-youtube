import base64
import io
import os

import torch
from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
from TTS.api import TTS

app = Flask(__name__)
CORS(app)

# Khởi tạo TTS với model tiếng Việt
print("Đang tải model TTS tiếng Việt...")

# Sử dụng model VITS cho tiếng Việt (nếu có)
try:
    # Thử sử dụng model tiếng Việt nếu có
    tts = TTS("tts_models/vi/mai/vits")
    print("Đã tải thành công model tiếng Việt VITS")
except:
    try:
        # Fallback sang model đa ngôn ngữ
        tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2")
        print("Đã tải model đa ngôn ngữ XTTS_v2")
    except:
        # Fallback cuối cùng
        tts = TTS("tts_models/en/ljspeech/tacotron2-DDC")
        print("Đã tải model English Tacotron2")


@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "healthy", "message": "TTS service is running"})


@app.route("/tts", methods=["POST"])
def text_to_speech():
    try:
        data = request.get_json()
        text = data.get("text", "")

        if not text:
            return jsonify({"error": "Thiếu nội dung text"}), 400

        # Tạo file âm thanh tạm thời
        output_path = "/tmp/output.wav"

        # Tạo speech từ text
        if "vi/mai/vits" in str(type(tts)):
            # Model tiếng Việt
            tts.tts_to_file(text=text, file_path=output_path)
        elif "xtts" in str(type(tts)).lower():
            # Model đa ngôn ngữ với language setting
            tts.tts_to_file(text=text, file_path=output_path, language="vi")
        else:
            # Model khác
            tts.tts_to_file(text=text, file_path=output_path)

        # Đọc file và trả về base64
        with open(output_path, "rb") as audio_file:
            audio_data = audio_file.read()
            audio_base64 = base64.b64encode(audio_data).decode("utf-8")

        # Xóa file tạm
        os.remove(output_path)

        return jsonify(
            {
                "success": True,
                "audio_base64": audio_base64,
                "message": "Tạo speech thành công",
            }
        )

    except Exception as e:
        print(f"Lỗi: {str(e)}")
        return jsonify({"error": f"Lỗi tạo speech: {str(e)}"}), 500


@app.route("/tts/file", methods=["POST"])
def text_to_speech_file():
    try:
        data = request.get_json()
        text = data.get("text", "")

        if not text:
            return jsonify({"error": "Thiếu nội dung text"}), 400

        # Tạo file âm thanh
        output_path = "/tmp/tts_output.wav"

        if "vi/mai/vits" in str(type(tts)):
            tts.tts_to_file(text=text, file_path=output_path)
        elif "xtts" in str(type(tts)).lower():
            tts.tts_to_file(text=text, file_path=output_path, language="vi")
        else:
            tts.tts_to_file(text=text, file_path=output_path)

        return send_file(
            output_path,
            mimetype="audio/wav",
            as_attachment=True,
            download_name="speech.wav",
        )

    except Exception as e:
        print(f"Lỗi: {str(e)}")
        return jsonify({"error": f"Lỗi tạo file speech: {str(e)}"}), 500


@app.route("/models", methods=["GET"])
def list_models():
    try:
        # Liệt kê các model có sẵn
        models = TTS.list_models()
        vietnamese_models = [
            m for m in models if "vi" in m.lower() or "vietnamese" in m.lower()
        ]

        return jsonify(
            {
                "vietnamese_models": vietnamese_models,
                "all_models_count": len(models),
                "current_model": str(type(tts)),
            }
        )
    except Exception as e:
        return jsonify({"error": f"Lỗi liệt kê models: {str(e)}"}), 500


if __name__ == "__main__":
    print("Khởi động TTS Server...")
    print("API endpoints:")
    print("- POST /tts - Tạo speech và trả về base64")
    print("- POST /tts/file - Tạo speech và tải file")
    print("- GET /models - Liệt kê models")
    print("- GET /health - Kiểm tra health")

    app.run(host="0.0.0.0", port=5002, debug=False)
