import PyPDF2 # type: ignore
from langchain.text_splitter import RecursiveCharacterTextSplitter # type: ignore
import pytesseract # type: ignore
from PIL import Image # type: ignore

def preprocess_file(file):
    if file.filename.endswith('.pdf'):
        reader = PyPDF2.PdfReader(file)
        text = ''.join(page.extract_text() for page in reader.pages)
    elif file.filename.endswith('.docx'):
        import docx # type: ignore
        doc = docx.Document(file)
        text = '\n'.join([p.text for p in doc.paragraphs])
    else:
        raise ValueError("Unsupported file format")

    # Split text into chunks
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = splitter.split_text(text)
    return chunks
