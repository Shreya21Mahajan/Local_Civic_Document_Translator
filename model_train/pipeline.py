from src.ocr import extract_text_from_image
from src.translator import load_model, translate_text
import os

# Load model once
model, tokenizer = load_model()

image_path = r"E:\JLU\civic_translator\data\sample.png"

def run_pipeline(image_path):
    try:
        if not os.path.exists(image_path):
            print("❌ Image not found:", image_path)
            return

        print("📸 Processing image:", image_path)

        text = extract_text_from_image(image_path)
        print("\n📝 Extracted Text:\n", text)

        if not text.strip():
            print("⚠️ No text detected!")
            return

        translated = translate_text(text, model, tokenizer)
        print("\n🌍 Translated Text:\n", translated)

    except Exception as e:
        print("❌ Error:", str(e))


if __name__ == "__main__":
    run_pipeline(image_path)