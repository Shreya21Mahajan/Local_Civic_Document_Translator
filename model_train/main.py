from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

model = AutoModelForSeq2SeqLM.from_pretrained("./models/civic_translator")
tokenizer = AutoTokenizer.from_pretrained("./models/civic_translator")

from pipeline import run_pipeline

result = run_pipeline("sample_image.jpg")
print(result["translated_text"])

from src.image_translator import extract_text_from_image, translate_text

def main():
    image_path = "test.jpg"

    text = extract_text_from_image(image_path)
    translated = translate_text(text)

    print(translated)

if __name__ == "__main__":
    main()

