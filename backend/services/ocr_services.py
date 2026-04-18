#services/ocr_service.py
import logging
from paddleocr import PaddleOCR
logger = logging.getLogger(__name__)

# Initialize PaddleOCR once (lazy loading to save startup time)
ocr_engine = None

def get_ocr_engine():
    global ocr_engine
    if ocr_engine is None:
        from paddleocr import PaddleOCR
        # lang='en' for English, 'ch' for Chinese, etc.
        ocr_engine = PaddleOCR(use_angle_cls=True, lang='en', show_log=False)
    return ocr_engine

def extract_text_from_image(image_path: str) -> str:
    """
    Takes an image path, runs OCR, and returns cleaned text.
    """
    try:
        engine = get_ocr_engine()
        
        # Run OCR
        result = engine.ocr(image_path, cls=True)
        
        # PaddleOCR returns a list of lists: [[box, (text, confidence)], ...]
        # We only want the text
        extracted_texts = []
        if result and result[0]:
            for line in result[0]:
                text = line[1][0] # The text content
                confidence = line[1][1]
                
                # Filter low confidence predictions
                if confidence > 0.5:
                    extracted_texts.append(text)
        
        # Join all lines with newlines
        full_text = "\n".join(extracted_texts)
        logger.info(f"Successfully extracted {len(full_text)} chars from {image_path}")
        return full_text

    except Exception as e:
        logger.error(f"OCR failed for {image_path}: {str(e)}")
        raise Exception(f"OCR Processing Error: {str(e)}")