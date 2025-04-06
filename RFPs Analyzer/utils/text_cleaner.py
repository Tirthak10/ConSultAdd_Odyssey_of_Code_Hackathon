import PyPDF2
from langchain.text_splitter import RecursiveCharacterTextSplitter
import pytesseract
from PIL import Image
import io
import re
import os
from datetime import datetime

def extract_text_from_pdf(file):
    """
    Extract text from PDF file with enhanced handling for scanned documents
    Args:
        file: PDF file object
    Returns:
        str: Extracted text from PDF
    """
    text = ""
    try:
        # Create PDF reader object
        reader = PyPDF2.PdfReader(file)
        
        # Process each page
        for page in reader.pages:
            # Try to extract text directly first
            page_text = page.extract_text()
            
            # If page is mostly empty, it might be scanned
            if len(page_text.strip()) < 50:
                # Extract images from the page
                if '/XObject' in page['/Resources']:
                    xObject = page['/Resources']['/XObject'].get_object()
                    
                    for obj in xObject:
                        if xObject[obj]['/Subtype'] == '/Image':
                            # Extract image
                            image = Image.frombytes(
                                'RGB',
                                (xObject[obj]['/Width'], xObject[obj]['/Height']),
                                page.extract_text()
                            )
                            # Use OCR to get text from image
                            page_text = pytesseract.image_to_string(image)
            
            text += page_text + "\n"
            
    except Exception as e:
        print(f"Error processing PDF: {e}")
        raise
        
    return text

def clean_text(text):
    """
    Clean and normalize extracted text
    Args:
        text: Raw text string
    Returns:
        str: Cleaned text
    """
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove special characters but keep important punctuation
    text = re.sub(r'[^\w\s.,;:!?()\-\']', '', text)
    
    # Fix common OCR errors
    text = text.replace('|', 'I')
    text = text.replace('0', 'O')
    
    return text.strip()

def create_chunks(text, chunk_size=1000, chunk_overlap=200):
    """
    Split text into overlapping chunks
    Args:
        text: Text to split
        chunk_size: Size of each chunk
        chunk_overlap: Number of characters to overlap between chunks
    Returns:
        list: List of text chunks
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        separators=["\n\n", "\n", ".", "!", "?", ";", ",", " "]
    )
    
    return splitter.split_text(text)

def preprocess_file(file):
    """
    Process input file and convert to text chunks
    Args:
        file: Input file (PDF or DOCX)
    Returns:
        list: List of text chunks
    """
    if file.filename.endswith('.pdf'):
        # Extract text from PDF
        text = extract_text_from_pdf(file)
    elif file.filename.endswith('.docx'):
        import docx
        doc = docx.Document(file)
        text = '\n'.join([p.text for p in doc.paragraphs])
    else:
        raise ValueError("Unsupported file format. Please provide PDF or DOCX file.")
    
    # Clean the extracted text
    cleaned_text = clean_text(text)
    
    # Split into chunks
    chunks = create_chunks(cleaned_text)
    
    return chunks
