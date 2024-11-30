import faiss
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer


def query_faiss(query, index_path, corpus_path, model_name="all-MiniLM-L6-v2", top_k=5):
    """
    Query the FAISS index and return the top-k results
    """
    # Load the FAISS index and corpus
    index = faiss.read_index(index_path)
    corpus = pd.read_csv(corpus_path)

    # Encode query
    model = SentenceTransformer(model_name)
    query_embedding = model.encode([query])

    # Search index
    distances, indices = index.search(query_embedding, top_k)

    # Retrieve results
    results = [(corpus.iloc[idx]['content'], distances[0][i]) for i, idx in enumerate(indices[0])]

    return results


if __name__ == "__main__":
    query = "Explain the male reproductive system"
    results = query_faiss(query, '../preprocessing/faiss_index', '../preprocessing/corpus.csv')

    for idx, (content, score) in enumerate(results):
        print(f"Rank {idx + 1} | Score: {score} \n Content: {content}\n")