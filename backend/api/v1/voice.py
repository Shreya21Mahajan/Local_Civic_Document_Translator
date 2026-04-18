# api/v1/voice.py
@router.post("/transcribe")
async def transcribe_voice(audio: UploadFile, language: str = "hi"):
    """Convert user's voice to text in regional language"""
    
@router.post("/speak")
async def text_to_speech(text: str, language: str = "hi"):
    """Convert simplified guidance to voice in user's dialect"""