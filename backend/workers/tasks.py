# app/workers/tasks.py
from core.celery_config import celery_app
from services.ocr_services import extract_text_from_image
from services.nlp_services import process_document_text
from services.form_engine import FormEngine
from db.session import SessionLocal
from models.document import Document
import logging
import json

logger = logging.getLogger(__name__)

@celery_app.task(bind=True, max_retries=3)
def process_document_ocr(self, document_id: int, file_path: str):
    db = SessionLocal()
    try:
        doc = db.query(Document).filter(Document.id == document_id).first()
        if not doc:
            raise ValueError(f"Document {document_id} not found")
        
        doc.status = "PROCESSING"
        db.commit()

        # --- STEP 1: OCR ---
        raw_text = extract_text_from_image(file_path)
        
        # --- STEP 2: NLP ---
        nlp_result = process_document_text(raw_text)
        entities = nlp_result['entities']
        
        # --- STEP 3: FORM ENGINE ---
        logger.info(f"[{document_id}] Running Form Engine...")
        # Assuming we know the form type is 'govt_id_application' 
        # (In real app, detect this from document classification)
        form_result = FormEngine.auto_fill_form("govt_id_application", entities)
        
        # --- STEP 4: Save Results ---
        doc.extracted_text = nlp_result['cleaned_text']
        doc.structured_data = form_result # Save the whole form structure as JSON
        
        doc.status = "COMPLETED"
        db.commit()
        
        logger.info(f"[{document_id}] Done. Form Completion: {form_result['completion_percentage']}%")
        
        return {
            "status": "success", 
            "form_data": form_result
        }

    except Exception as exc:
        try:
            doc.status = "FAILED"
            doc.error_message = str(exc)
            db.commit()
        except:
            pass
        logger.error(f"[{document_id}] Failed: {exc}")
        raise self.retry(exc=exc, countdown=60)
    
    finally:
        db.close()
