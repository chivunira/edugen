from sentence_transformers import SentenceTransformer
import numpy as np
import pandas as pd


def encode_corpus(tsv_path, model_name="all-MiniLM-L6-v2"):
    """
    Encode the content in a TSV file using SBERT, converting it into embeddings.
    """
    # Load the data
    data = pd.read_csv(tsv_path, sep='\t', header=None, names=['content'])
    corpus = data["content"].tolist()

    # Load the SBERT model
    model = SentenceTransformer(model_name)

    # Encode the corpus
    embeddings = model.encode(corpus, show_progress_bar=True)

    return data, embeddings


if __name__ == "__main__":
    tsv_path = 'grade_6_science_notes.tsv'
    data, embeddings = encode_corpus(tsv_path)

    # Add an explicit index column for unique identification
    data.reset_index(inplace=True)

    # Save the embeddings to a .npy file
    np.save('embeddings.npy', embeddings)

    # Save the data for reference
    data.to_csv('corpus.csv', index=False, header=["id", "content"])

    print("Successfully encoded the corpus and saved the embeddings.")
