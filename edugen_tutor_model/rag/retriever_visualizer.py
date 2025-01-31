import matplotlib
matplotlib.use('TkAgg')  # Set the backend before importing pyplot
import matplotlib.pyplot as plt
import numpy as np
from sentence_transformers import SentenceTransformer
import pandas as pd
import faiss
import seaborn as sns


def visualize_retrieval(query, index_path, corpus_path, model_name="all-MiniLM-L6-v2", top_k=5):
    """
    Create visualizations showing how the retriever finds similar content.
    """
    # Load the FAISS index and corpus
    index = faiss.read_index(index_path)
    corpus = pd.read_csv(corpus_path)

    # Get the model and encode query
    model = SentenceTransformer(model_name)
    query_embedding = model.encode([query])

    # Get all corpus embeddings for comparison
    corpus_embeddings = index.reconstruct_n(0, index.ntotal)

    # Search index
    distances, indices = index.search(query_embedding, top_k)

    # Convert distances to similarity scores (1 / (1 + distance))
    similarities = 1 / (1 + distances[0])

    # Create bar plot of similarity scores
    plt.figure(figsize=(12, 6))
    plt.subplot(1, 2, 1)

    # Create bars
    bars = plt.bar(range(len(similarities)), similarities)

    # Customize the plot
    plt.title('Similarity Scores for Retrieved Content\n(Higher is More Similar)', pad=20)
    plt.xlabel('Retrieved Document Rank')
    plt.ylabel('Similarity Score')

    # Add similarity score labels on top of bars
    for i, (bar, score) in enumerate(zip(bars, similarities)):
        plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height(),
                 f'{score:.3f}',
                 ha='center', va='bottom')

    # Create a more detailed view of the top matches
    plt.subplot(1, 2, 2)

    # Create a matrix of similarity scores
    similarity_matrix = np.zeros((1, top_k))
    similarity_matrix[0] = similarities

    # Create a heatmap
    sns.heatmap(similarity_matrix,
                annot=True,
                cmap='YlOrRd',
                xticklabels=[f"Match {i + 1}\n{corpus.iloc[idx]['content'][:30]}..."
                             for i, idx in enumerate(indices[0])],
                yticklabels=[f"Query:\n{query}"],
                cbar_kws={'label': 'Similarity Score'})

    plt.title('Query-Document Similarity Heatmap', pad=20)
    plt.tight_layout()
    try:
        plt.show()
    except Exception as e:
        print(f"Error showing plot: {e}")
        print("Try running the script outside of PyCharm or using a different matplotlib backend")
    finally:
        plt.close('all')  # Clean up figures

    # Print detailed results
    print("\nDetailed Retrieval Results:")
    print(f"Query: {query}\n")
    for i, (idx, similarity) in enumerate(zip(indices[0], similarities)):
        print(f"Match {i + 1} (Similarity: {similarity:.3f}):")
        print(f"Content: {corpus.iloc[idx]['content']}")
        print()


if __name__ == "__main__":
    # Example usage
    query = "Explain the parts of a bee"
    visualize_retrieval(
        query=query,
        index_path='../rag_preprocessing/faiss_index',
        corpus_path='../rag_preprocessing/corpus.csv'
    )