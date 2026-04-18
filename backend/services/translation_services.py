# services/translation_service.py
import requests
from deep_translator import GoogleTranslator  # Free fallback

class TranslationService:
    def __init__(self):
        self.bhashini_url = "https://bhashini.gov.in/ulca/apis/v0/model/compute"
        
    def translate(self, text: str, source_lang: str = "en", target_lang: str = "hi"):
        """Translate text to regional Indian language"""
        try:
            # Use Google Translator as fallback (free, no API key)
            result = GoogleTranslator(source=source_lang, target=target_lang).translate(text)
            return {"translated": result, "source": source_lang, "target": target_lang}
        except Exception as e:
            return {"error": str(e)}
    
    def simplify_and_translate(self, complex_text: str, target_lang: str = "hi"):
        """Simplify govt jargon then translate"""
        # Step 1: Simplify (use LLM)
        # Step 2: Translate
        simplified = self._simplify(complex_text)
        translated = self.translate(simplified, "en", target_lang)
        return {"original": complex_text, "simplified": simplified, "translated": translated}