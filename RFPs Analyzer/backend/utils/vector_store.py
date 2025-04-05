import faiss # type: ignore
import numpy as np # type: ignore

index = faiss.IndexFlatL2(1536)  # Assuming 1536-dimensional embeddings
stored_chunks = []

def store_chunks(chunks):
    global stored_chunks
    embeddings = [chunk['embedding'] for chunk in chunks]
    vectors = np.array(embeddings).astype('float32')
    index.add(vectors)
    stored_chunks.extend(chunks)

def retrieve_chunks(query_embedding, top_k=5):
    query_vector = np.array(query_embedding).astype('float32').reshape(1, -1)
    distances, indices = index.search(query_vector, top_k)
    return [stored_chunks[i] for i in indices[0]]
