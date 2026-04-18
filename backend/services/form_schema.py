# backend/services/form_schema.py
from typing import List, Dict, Any, Optional
from enum import Enum

class FieldType(str, Enum):
    TEXT = "text"
    DATE = "date"
    EMAIL = "email"
    NUMBER = "number"
    SELECT = "select"

class FormDefinition:
    """
    Defines the structure of a form and how to map NLP entities to it.
    """
    def __init__(self, form_id: str, title: str, fields: List[Dict[str, Any]]):
        self.form_id = form_id
        self.title = title
        self.fields = fields

# Example: Government ID Application Form
GOVT_ID_FORM = FormDefinition(
    form_id="govt_id_application",
    title="Government ID Application",
    fields=[
        {
            "id": "full_name",
            "label": "Full Name",
            "type": FieldType.TEXT,
            "required": True,
            "mapping_keys": ["PERSON"], 
            "placeholder": "e.g. John Doe"
        },
        {
            "id": "date_of_birth",
            "label": "Date of Birth",
            "type": FieldType.DATE,
            "required": True,
            "mapping_keys": ["DATE"],
            "placeholder": "YYYY-MM-DD"
        },
        {
            "id": "email_address",
            "label": "Email Address",
            "type": FieldType.EMAIL,
            "required": False,
            "mapping_keys": ["EMAIL"],
            "placeholder": "john@example.com"
        },
        {
            "id": "phone_number",
            "label": "Phone Number",
            "type": FieldType.TEXT,
            "required": False,
            "mapping_keys": ["PHONE"],
            "placeholder": "+1 234 567 890"
        },
        {
            "id": "city",
            "label": "City / Location",
            "type": FieldType.TEXT,
            "required": True,
            "mapping_keys": ["GPE"], 
            "placeholder": "e.g. New York"
        },
        {
            "id": "id_number",
            "label": "ID Number",
            "type": FieldType.TEXT,
            "required": False,
            "mapping_keys": ["ID_NUMBER"],
            "placeholder": "e.g. A1234567"
        }
    ]
)

# Registry of all available forms
FORM_REGISTRY = {
    "govt_id_application": GOVT_ID_FORM
}

def get_form_definition(form_id: str) -> Optional[FormDefinition]:
    return FORM_REGISTRY.get(form_id)