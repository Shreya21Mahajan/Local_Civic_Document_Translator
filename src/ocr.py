import easyocr

# Load EasyOCR model once
reader = easyocr.Reader(['en'], gpu=False)  # set gpu=True if you have GPU

def extract_text_from_image(image_path):
    result = reader.readtext(image_path)

    extracted_text = ""

    for detection in result:
        text = detection[1]   # (bbox, text, confidence)
        extracted_text += text + " "

    return extracted_text.strip()