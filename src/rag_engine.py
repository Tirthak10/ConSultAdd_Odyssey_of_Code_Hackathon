from sentence_transformers import SentenceTransformer
import chromadb
from config import CHROMA_SETTINGS
import os
from summarizer import summarize_text

class RAGEngine:
    def __init__(self, collection_name="rfp_documents", model_name="all-mpnet-base-v2"):
        self.model = SentenceTransformer(model_name)
        
        # Ensure persist directory exists
        os.makedirs(CHROMA_SETTINGS["persist_directory"], exist_ok=True)
        
        # Initialize ChromaDB with new configuration
        self.chroma_client = chromadb.PersistentClient(path=CHROMA_SETTINGS["persist_directory"])
        
        # Try to get existing collection or create new one
        try:
            self.collection = self.chroma_client.get_collection("rfp_docs")
        except:
            self.collection = self.chroma_client.create_collection("rfp_docs")

    def add_documents(self, documents):
        embeddings = self.model.encode(documents).tolist()
        self.collection.add(
            documents=documents,
            embeddings=embeddings,
            ids=[f"doc_{i}" for i in range(len(documents))]
        )

    def get_relevant_context(self, query, top_n=3):
        query_embedding = self.model.encode([query]).tolist()
        results = self.collection.query(query_embeddings=query_embedding, n_results=top_n)
        return "\n".join(results['documents'][0])

    def query(self, query, top_n=3):
        context = self.get_relevant_context(query, top_n)
        return self.get_summarized_answer(query, context)

    def get_summarized_answer(self, question, context):
        prompt = f"User Question: {question}\nContext: {context}\nAnswer:"
        return summarize_text(context)
