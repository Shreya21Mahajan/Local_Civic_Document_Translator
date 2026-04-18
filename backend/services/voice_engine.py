# services/voice_service.py
import whisper  # OpenAI Whisper (offline)
from gtts import gTTS  # Google TTS (free, supports Hindi)
import io

class VoiceService:
    def __init__(self):
        self.stt_model = whisper.load_model("base")  # Supports Hindi
    
    def speech_to_text(self, audio_path: str, language: str = "hi"):
        """Convert voice to text in regional language"""
        result = self.stt_model.transcribe(audio_path, language=language)
        return result["text"]
    
    def text_to_speech(self, text: str, language: str = "hi"):
        """Convert text to voice in regional language"""
        tts = gTTS(text=text, lang=language, slow=False)
        audio_buffer = io.BytesIO()
        tts.write_to_fp(audio_buffer)
        return audio_buffer.getvalue()