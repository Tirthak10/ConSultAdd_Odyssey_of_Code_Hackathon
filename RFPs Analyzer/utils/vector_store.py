from pinecone import Pinecone, ServerlessSpec
import numpy as np
import json
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class VectorStore:
    def __init__(self):
        # Initialize Pinecone client
        api_key = os.getenv('PINECONE_API_KEY')
        if not api_key:
            raise ValueError("PINECONE_API_KEY environment variable is not set")
            
        # Initialize Pinecone with the API key
        self.pc = Pinecone(
            api_key=api_key,
            environment=os.getenv('PINECONE_ENVIRONMENT', 'gcp-starter')  # Add default environment
        )
        self.index_name = "dense-index"

        # Set up directories for metadata and chunks
        self.base_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
        self.chunks_dir = os.path.join(self.base_dir, 'document_chunks')
        self.metadata_dir = os.path.join(self.base_dir, 'metadata')
        
        # Create directories if they don't exist
        for directory in [self.base_dir, self.chunks_dir, self.metadata_dir]:
            os.makedirs(directory, exist_ok=True)

        # Initialize or get existing index
        if not self.pc.list_indexes():
            spec = ServerlessSpec(
                cloud="aws",
                region="us-east-1"
            )
            self.pc.create_index(
                name=self.index_name,
                dimension=384,  # dimension for llama-text-embed-v2
                metric="cosine",
                spec=spec
            )
        self.index = self.pc.Index(self.index_name)
        self.stored_chunks = self.load_stored_chunks()

    def load_stored_chunks(self):
        """Load stored chunks from disk"""
        chunks = []
        chunks_file = os.path.join(self.chunks_dir, 'chunks.json')
        if os.path.exists(chunks_file):
            with open(chunks_file, 'r') as f:
                chunks = json.load(f)
        return chunks

    def store_document(self, file_name, chunks, metadata=None):
        """Store document chunks and metadata in Pinecone"""
        # Generate unique document ID
        doc_id = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Prepare vectors for Pinecone
        vectors = []
        chunks_with_metadata = []
        
        for i, chunk in enumerate(chunks):
            chunk_id = f"{doc_id}_{i}"
            
            # Prepare metadata for the vector
            chunk_metadata = {
                "text": chunk['text'],
                "doc_id": doc_id,
                "chunk_index": i
            }
            if metadata:
                chunk_metadata["metadata"] = metadata

            # Prepare vector for Pinecone
            vector_data = {
                "id": chunk_id,
                "values": chunk['embedding'].tolist(),
                "metadata": chunk_metadata
            }
            vectors.append(vector_data)
            
            # Store chunk info for local reference
            chunks_with_metadata.append({
                "text": chunk['text'],
                "doc_id": doc_id,
                "chunk_index": i,
                "metadata": metadata or {}
            })

        # Upsert vectors to Pinecone
        self.index.upsert(vectors=vectors)
        
        # Store document metadata
        doc_metadata = {
            'doc_id': doc_id,
            'file_name': file_name,
            'timestamp': datetime.now().isoformat(),
            'chunk_count': len(chunks),
            'metadata': metadata or {}
        }
        
        metadata_path = os.path.join(self.metadata_dir, f'{doc_id}.json')
        with open(metadata_path, 'w') as f:
            json.dump(doc_metadata, f, indent=2)
        
        # Update stored chunks
        self.stored_chunks.extend(chunks_with_metadata)
        
        # Save chunks to disk
        chunks_file = os.path.join(self.chunks_dir, 'chunks.json')
        with open(chunks_file, 'w') as f:
            json.dump(self.stored_chunks, f, indent=2)
        
        return doc_id

    def retrieve_chunks(self, query_embedding, top_k=5):
        """Retrieve relevant chunks using Pinecone"""
        query_vector = np.array(query_embedding).astype('float32')
        
        # Query Pinecone
        results = self.index.query(
            vector=query_vector.tolist(),
            top_k=top_k,
            include_metadata=True
        )
        
        # Format results
        retrieved_chunks = []
        for match in results.matches:
            chunk = {
                "text": match.metadata["text"],
                "doc_id": match.metadata["doc_id"],
                "chunk_index": match.metadata["chunk_index"],
                "score": match.score
            }
            retrieved_chunks.append(chunk)
            
        return retrieved_chunks

    def get_document_metadata(self, doc_id):
        """Retrieve document metadata"""
        metadata_path = os.path.join(self.metadata_dir, f'{doc_id}.json')
        if os.path.exists(metadata_path):
            with open(metadata_path, 'r') as f:
                return json.load(f)
        return None

# Initialize global vector store instance
_vector_store = VectorStore()

def store_chunks(chunks, file_name=None, metadata=None):
    """Store chunks with associated metadata"""
    return _vector_store.store_document(file_name, chunks, metadata)

def retrieve_chunks(query_embedding, top_k=5):
    """Retrieve relevant chunks"""
    return _vector_store.retrieve_chunks(query_embedding, top_k)

def get_document_metadata(doc_id):
    """Get metadata for a document"""
    return _vector_store.get_document_metadata(doc_id)