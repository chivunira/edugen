import faiss
import numpy as np


def create_faiss_index(embeddings_path, index_path="faiss_index"):
    """
    Create a Faiss index from the embeddings.
    """
    # Load embeddings
    embeddings = np.load(embeddings_path)

    # Create FAISS index
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)

    # Save the index
    faiss.write_index(index, index_path)


if __name__ == "__main__":
    create_faiss_index('embeddings.npy')