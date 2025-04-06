import spacy
import nltk
from nltk.corpus import stopwords
import string

try:
    stopwords.words('english')
except LookupError:
    nltk.download('stopwords')

nlp = spacy.load("en_core_web_sm")
stop_words = set(stopwords.words('english'))

def preprocess_text(text):
    if text is None:
        return ""
    text = text.lower()
    doc = nlp(text)
    return " ".join([token.lemma_ for token in doc if not token.is_stop and not token.is_punct])

def chunk_text(text, chunk_size=500, chunk_overlap=50):
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size - chunk_overlap):
        chunk = " ".join(words[i:i + chunk_size])
        chunks.append(chunk)
    return chunks
