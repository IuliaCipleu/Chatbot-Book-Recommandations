import openai

def search_books(query, collection, top_k=1, model="text-embedding-3-small"):
    response = openai.Embedding.create(
        input=query,
        model=model
    )
    embedding = response["data"][0]["embedding"]
    
    return collection.query(
        query_embeddings=[embedding],
        n_results=top_k
    )
