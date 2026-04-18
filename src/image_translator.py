import easyocr
from deep_translator import GoogleTranslator
import os

reader = easyocr.Reader(['en', 'hi'])

def extract_text_from_image(image_path):
    if not os.path.exists(image_path):
        print(" Image not found!")
        return ""

    results = reader.readtext(image_path)
    text = " ".join([res[1] for res in results])
    return text


def translate_text(text, target_lang='en'):
    translated = GoogleTranslator(source='auto', target=target_lang).translate(text)
    return translated


def main():
    image_path = input("Enter image path: ")

    text = extract_text_from_image(image_path)
    print("\n📝 Extracted:", text)

    translated = translate_text(text, target_lang='hi')
    print("\n🌍 Translated (Hindi):", translated)   


if __name__ == "__main__":
    main()