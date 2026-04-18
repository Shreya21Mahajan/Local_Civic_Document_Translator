# File: services/voice_service.py (NEW)
from faster_whisper import WhisperModel  # for offline STT
from TTS.api import TTS  # for offline TTS (Coqui)

async def transcribe_audio(audio_file: bytes, language: str = "hi"):
    """Transcribe user voice input in regional languages"""
    model = WhisperModel("base", device="cpu", compute_type="int8")
    segments, info = model.transcribe(audio_file, language=language)
    return "".join([seg.text for seg in segments])

async def synthesize_speech(text: str, language: str = "hi"):
    """Convert simplified text to speech in user's dialect"""
    tts = TTS(model_name="tts_models/multilingual/multi-dataset/bark", gpu=False)
    tts.tts_to_file(text=text, speaker="p260", language=language, file_path="output.wav")