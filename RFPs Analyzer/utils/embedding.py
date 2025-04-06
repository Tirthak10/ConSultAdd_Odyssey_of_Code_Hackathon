import groq
import os
from dotenv import load_dotenv
import numpy as np

# Load environment variables
load_dotenv()

def get_groq_client():
    """Initialize and return Groq client with proper configuration"""
    api_key = os.getenv('GROQ_API_KEY')
    if not api_key:
        raise ValueError("GROQ_API_KEY environment variable is not set")
    return groq.Client(api_key=api_key)

# Initialize client
client = get_groq_client()

def generate_embeddings(chunks):
    """
    Generate embeddings for text chunks using Groq API
    Args:
        chunks: List of text chunks to generate embeddings for
    Returns:
        List of dictionaries containing text and embedding
    """
    embeddings = []
    
    # Process chunks in batches
    for chunk in chunks:
        try:
            # Use Groq embedding endpoint
            response = client.embeddings.create(
                model="mixtral-8x7b-32768",
                input=chunk,
                encoding_format="float"
            )
            
            # Extract embedding from response
            embedding_vector = response.data[0].embedding
            
            # Convert to numpy array for consistency with FAISS
            embedding_vector = np.array(embedding_vector, dtype=np.float32)
            
            embeddings.append({
                "text": chunk,
                "embedding": embedding_vector
            })
            
        except Exception as e:
            print(f"Error generating embedding for chunk: {e}")
            continue
            
    return embeddings
