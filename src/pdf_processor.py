import pypdf
import re
from langchain_text_splitters import RecursiveCharacterTextSplitter

def extract_text_from_pdf(pdf_file) -> str:
    """
    Extracts text from a PDF file. 
    Accepts a file path or a file-like object (BytesIO).
    """
    reader = pypdf.PdfReader(pdf_file)
    text_content = []
    
    for i, page in enumerate(reader.pages):
        page_text = page.extract_text()
        if page_text:
            # Clean up excessive linebreaks and double spaces
            cleaned_page = clean_extracted_text(page_text)
            # Annotate text with page numbers so we can trace answers back to references
            text_content.append(f"--- PAGE {i+1} ---\n{cleaned_page}")
            
    return "\n\n".join(text_content)

def clean_extracted_text(text: str) -> str:
    """
    Cleans up common formatting glitches in extracted PDF text.
    """
    # Replace multiple spaces with a single space
    text = re.sub(r'[ \t]+', ' ', text)
    # Replace more than two line breaks with double line breaks
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()

def chunk_text(text: str, chunk_size: int = 1000, chunk_overlap: int = 200) -> list[str]:
    """
    Chunks text into smaller, overlapping segments using RecursiveCharacterTextSplitter.
    """
    # We use a text splitter that tries to split on paragraphs, sentences, and words
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        separators=["\n\n", "\n", " ", ""]
    )
    
    chunks = splitter.split_text(text)
    return chunks
