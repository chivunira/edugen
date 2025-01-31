import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import seaborn as sns


def analyze_embeddings(embeddings_path, corpus_path=None):
    """
    Analyze embeddings with basic statistics and visualization
    """
    # Load embeddings
    embeddings = np.load(embeddings_path)

    # Basic statistics
    print("\nEmbedding Statistics:")
    print(f"Number of embeddings: {embeddings.shape[0]}")
    print(f"Embedding dimension: {embeddings.shape[1]}")
    print(f"\nMean value: {embeddings.mean():.6f}")
    print(f"Standard deviation: {embeddings.std():.6f}")
    print(f"Min value: {embeddings.min():.6f}")
    print(f"Max value: {embeddings.max():.6f}")

    # Sample values from first embedding
    print("\nSample values from first embedding vector:")
    print("First 10 dimensions:", embeddings[0][:10].round(4))

    # Create a simple visualization
    plt.figure(figsize=(12, 4))

    # Plot 1: Distribution of all embedding values
    plt.subplot(1, 2, 1)
    sns.histplot(embeddings.flatten(), bins=50)
    plt.title('Distribution of Embedding Values')
    plt.xlabel('Value')
    plt.ylabel('Count')

    # Plot 2: Mean values across dimensions
    plt.subplot(1, 2, 2)
    dimension_means = embeddings.mean(axis=0)
    plt.plot(dimension_means, alpha=0.7)
    plt.title('Mean Values Across Embedding Dimensions')
    plt.xlabel('Dimension')
    plt.ylabel('Mean Value')

    plt.tight_layout()
    plt.show()

    # If corpus is provided, show some content examples
    if corpus_path:
        corpus = pd.read_csv(corpus_path)
        print("\nExample content and their embedding statistics:")
        for i in range(min(3, len(corpus))):
            print(f"\nDocument {i + 1}:")
            print(f"Content: {corpus.iloc[i]['content'][:100]}...")
            print(f"Mean embedding value: {embeddings[i].mean():.6f}")
            print(f"Std embedding value: {embeddings[i].std():.6f}")


if __name__ == "__main__":
    # Example usage
    analyze_embeddings(
        embeddings_path='../rag_preprocessing/embeddings.npy',
        corpus_path='../rag_preprocessing/corpus.csv'
    )