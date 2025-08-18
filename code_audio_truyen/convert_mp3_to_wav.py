from pydub import AudioSegment

# Đọc file mp3
audio = AudioSegment.from_mp3("voice_prompt.mp3")

# Chuyển sang wav (mono, 16000Hz)
audio = audio.set_channels(1).set_frame_rate(16000)
audio.export("voice_prompt.wav", format="wav")
