import openai # type: ignore

def generate_embeddings(chunks):
    embeddings = []
    for chunk in chunks:
        response = openai.Embedding.create(input=chunk, model="text-embedding-ada-002")
        embeddings.append({"text": chunk, "embedding": response['data'][0]['embedding']})
    return embeddings
