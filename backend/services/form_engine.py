#services/form_engine.py
import re
from typing import Dict, List, Any, Optional
from .form_schema import FormDefinition, get_form_definition, FieldType
import logging

logger = logging.getLogger(__name__)

class FormEngine:
    
    @staticmethod
    def auto_fill_form(form_id: str, entities: Dict[str, List[str]]) -> Dict[str, Any]:
        """
        Maps extracted NLP entities to form fields based on predefined rules.
        Returns the form structure with pre-filled values.
        """
        form_def = get_form_definition(form_id)
        if not form_def:
            return {"error": f"Form '{form_id}' not found"}

        filled_fields = []
        confidence_score = 0.0
        total_fields = len(form_def.fields)
        filled_count = 0

        for field in form_def.fields:
            field_id = field["id"]
            mapping_keys = field.get("mapping_keys", [])
            value = None
            
            # Try to find a match in extracted entities
            for key in mapping_keys:
                if key in entities and entities[key]:
                    # Take the first match (simple strategy)
                    value = entities[key][0] 
                    filled_count += 1
                    break
            
            # If no entity found, leave empty for user to fill
            filled_fields.append({
                "id": field_id,
                "label": field["label"],
                "type": field["type"].value,
                "value": value,
                "required": field["required"],
                "placeholder": field["placeholder"],
                "is_auto_filled": value is not None
            })

        if total_fields > 0:
            confidence_score = round((filled_count / total_fields) * 100, 2)

        return {
            "form_id": form_id,
            "title": form_def.title,
            "fields": filled_fields,
            "completion_percentage": confidence_score,
            "message": f"Auto-filled {filled_count}/{total_fields} fields."
        }

    @staticmethod
    def validate_field(field_id: str, value: str, field_type: str) -> Dict[str, Any]:
        """
        Validates a single field value based on type.
        """
        errors = []
        
        if not value and field_id == "full_name": # Example strict rule
             # In real app, check 'required' flag from schema
             pass 

        if field_type == "email":
            pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
            if not re.match(pattern, value):
                errors.append("Invalid email format.")
        
        elif field_type == "date":
            # Simple YYYY-MM-DD check
            pattern = r'^\d{4}-\d{2}-\d{2}$'
            if not re.match(pattern, value):
                errors.append("Date must be in YYYY-MM-DD format.")
        
        elif field_type == "number":
            if not value.isdigit():
                errors.append("Must be a valid number.")

        return {
            "valid": len(errors) == 0,
            "errors": errors
        }

    @staticmethod
    def generate_next_step(current_step: int, form_data: Dict) -> Dict[str, Any]:
        """
        Generates guidance for the next step (e.g., "Please review your name").
        Useful for a guided wizard UI.
        """
        # Simple logic: Just return the next unfilled required field
        # In a real app, this could be complex business logic
        return {
            "current_step": current_step,
            "next_step": current_step + 1,
            "instruction": "Please review the highlighted fields.",
            "focus_field": None # Could return ID of field needing attention
        }