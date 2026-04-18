# services/llm_engine.py
from groq import Groq  # FREE & FAST alternative to OpenAI
import os

class LLMEngine:
    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    
    def simplify_government_text(self, text: str, language: str = "Hindi"):
        prompt = f"""You are a helpful assistant for Indian citizens.
        Simplify this government document text into very simple {language} 
        that a person with low literacy can understand. Explain WHY each 
        field is needed and HOW to fill it.
        
        Document text: {text}
        
        Output format:
        1. Simple explanation
        2. Step-by-step instructions
        3. Common mistakes to avoid
        """
        response = self.client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content