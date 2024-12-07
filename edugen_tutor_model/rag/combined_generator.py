from openai import OpenAI
from retriever_test import query_faiss
import os
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
)


def generate_response_with_retrieval(query, index_path, corpus_path, gpt_model="gpt-4o-mini", max_tokens=500):
    """
    Combine FAISS retrieval with GPT generation
    """
    # Retrieve content using FAISS
    retrieved_results = query_faiss(query, index_path, corpus_path)
    retrieved_text = "\n".join([f"{idx + 1}. {content}" for idx, (content, _) in enumerate(retrieved_results)])

    # Generate response using GPT
    prompt = f"Using the following curriculum material:\n{retrieved_text}\nAnswer the question: {query}"
    response = client.chat.completions.create(
        model=gpt_model,
        messages=[{
            "role": "user",
            "content": prompt
        }],
        max_tokens=max_tokens
    )
    response_message = response.choices[0].message.content
    return response_message

if __name__ == "__main__":
    query = "Explain the topic of animals."
    response = generate_response_with_retrieval(query, '../rag_preprocessing/faiss_index',
                                                '../rag_preprocessing/corpus.csv')
    print(response)
