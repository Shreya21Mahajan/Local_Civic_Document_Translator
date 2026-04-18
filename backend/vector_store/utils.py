# backend/vector_store/utils.py

def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list:
    """
    Splits long text into smaller overlapping chunks for better RAG retrieval.
    
    Args:
        text: The input text to split.
        chunk_size: Maximum number of words per chunk.
        overlap: Number of words to overlap between chunks.
    
    Returns:
        A list of text chunks.
    """
    if not text:
        return []
        
    words = text.split()
    chunks = []
    
    # If text is shorter than chunk_size, return as is
    if len(words) <= chunk_size:
        return [text]
    
    # Slide window over words
    for i in range(0, len(words), chunk_size - overlap):
        chunk_words = words[i : i + chunk_size]
        chunk = " ".join(chunk_words)
        chunks.append(chunk)
        
        # Stop if we've reached the end
        if i + chunk_size >= len(words):
            break
            
    return chunks