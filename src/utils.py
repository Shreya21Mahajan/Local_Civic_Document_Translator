def clean_text(text: str) -> str:
    """
    Basic text cleaning utility
    """
    if not text:
        return ""

    text = text.strip()
    text = text.replace("\n", " ")
    text = " ".join(text.split())  # remove extra spaces

    return text


def validate_text(text: str) -> bool:
    """
    Check if extracted text is valid
    """
    return bool(text and text.strip())