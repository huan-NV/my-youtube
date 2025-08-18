import tkinter as tk
from tkinter import ttk, filedialog
import os
import torch
from TTS.api import TTS

class CoquiTTSApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Coqui TTS App")
        self.root.geometry("500x450")
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.tts = None
        self.setup_ui()
        self.load_model()

    def load_model(self):
        try:
            self.tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2", progress_bar=False).to(self.device)
            self.status_label.config(text="Mô hình XTTSv2 đã tải.")
        except Exception as e:
            self.status_label.config(text=f"Lỗi tải mô hình: {str(e)}")

    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Nhãn và ô nhập văn bản
        ttk.Label(main_frame, text="Nhập văn bản:").grid(row=0, column=0, columnspan=2, pady=5)
        self.text_input = tk.Text(main_frame, height=5, width=50)
        self.text_input.grid(row=1, column=0, columnspan=2, pady=5)

        # Chọn ngôn ngữ
        ttk.Label(main_frame, text="Ngôn ngữ:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.language_var = tk.StringVar(value="vi")
        languages = ["vi", "en", "es", "fr", "de", "it", "pt", "pl", "tr", "ru", "nl", "cs", "ar", "zh-cn", "ja", "hu", "ko", "hi"]
        self.language_menu = ttk.Combobox(main_frame, textvariable=self.language_var, values=languages, state="readonly")
        self.language_menu.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5)

        # File âm thanh tham chiếu
        ttk.Label(main_frame, text="File âm thanh tham chiếu:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.speaker_wav_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.speaker_wav_var, width=30).grid(row=3, column=1, sticky=(tk.W, tk.E), pady=5)
        ttk.Button(main_frame, text="Chọn file", command=self.choose_speaker_wav).grid(row=3, column=1, sticky=tk.E, pady=5)

        # Tốc độ nói
        ttk.Label(main_frame, text="Tốc độ (0.5-2.0):").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.speed_scale = ttk.Scale(main_frame, from_=0.5, to=2.0, orient=tk.HORIZONTAL)
        self.speed_scale.set(1.0)
        self.speed_scale.grid(row=4, column=1, sticky=(tk.W, tk.E), pady=5)

        # Nút điều khiển
        ttk.Button(main_frame, text="Phát", command=self.speak_text).grid(row=5, column=0, pady=10)
        ttk.Button(main_frame, text="Lưu WAV", command=self.save_to_wav).grid(row=5, column=1, pady=10)
        ttk.Button(main_frame, text="Xóa", command=self.clear_text).grid(row=6, column=0, columnspan=2, pady=10)

        # Nhãn trạng thái
        self.status_label = ttk.Label(main_frame, text="Sẵn sàng")
        self.status_label.grid(row=7, column=0, columnspan=2, pady=5)

    def choose_speaker_wav(self):
        file_path = filedialog.askopenfilename(filetypes=[("WAV files", "*.wav")])
        if file_path:
            self.speaker_wav_var.set(file_path)
            self.status_label.config(text="Đã chọn file tham chiếu.")

    def speak_text(self):
        text = self.text_input.get("1.0", tk.END).strip()
        if not text:
            self.status_label.config(text="Vui lòng nhập văn bản!")
            return
        speaker_wav = self.speaker_wav_var.get()
        if not speaker_wav or not os.path.exists(speaker_wav):
            self.status_label.config(text="Vui lòng chọn file âm thanh tham chiếu!")
            return
        try:
            self.tts.tts(text=text, speaker_wav=speaker_wav, language=self.language_var.get(), speed=self.speed_scale.get())
            self.status_label.config(text="Đã phát giọng nói.")
        except Exception as e:
            self.status_label.config(text=f"Lỗi: {str(e)}")

    def save_to_wav(self):
        text = self.text_input.get("1.0", tk.END).strip()
        if not text:
            self.status_label.config(text="Vui lòng nhập văn bản!")
            return
        speaker_wav = self.speaker_wav_var.get()
        if not speaker_wav or not os.path.exists(speaker_wav):
            self.status_label.config(text="Vui lòng chọn file âm thanh tham chiếu!")
            return
        file_path = filedialog.asksaveasfilename(defaultextension=".wav", filetypes=[("WAV files", "*.wav")])
        if file_path:
            try:
                self.tts.tts_to_file(text=text, speaker_wav=speaker_wav, language=self.language_var.get(), speed=self.speed_scale.get(), file_path=file_path)
                self.status_label.config(text=f"Đã lưu file tại: {os.path.basename(file_path)}")
            except Exception as e:
                self.status_label.config(text=f"Lỗi: {str(e)}")

    def clear_text(self):
        self.text_input.delete("1.0", tk.END)
        self.speaker_wav_var.set("")
        self.status_label.config(text="Đã xóa văn bản.")

if __name__ == "__main__":
    root = tk.Tk()
    app = CoquiTTSApp(root)
    root.mainloop()