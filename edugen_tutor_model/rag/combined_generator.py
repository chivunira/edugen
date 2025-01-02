from openai import OpenAI
from .retriever_test import query_faiss
import os
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
)


def generate_topic_overview(topic_name, index_path, corpus_path):
    """
    Generate an overview of the topic
    """
    query = f"Give me an overview of the topic {topic_name}"
    retrieved_results = query_faiss(query, index_path, corpus_path)
    retrieved_text = "\n".join([f"{idx + 1}. {content}" for idx, (content, _) in enumerate(retrieved_results)])

    prompt = (
        "You are EduGen, a friendly and professional grade 6 science tutor. You specialize in making complex topics "
        "easy to understand for 11-12 year old students.\n\n"
        f"Based on the following curriculum material about {topic_name}:\n{retrieved_text}\n\n"
        f"Provide a clear, engaging introduction to {topic_name}. Include:\n"
        "1. A simple explanation of what this topic is about\n"
        "2. Why it's interesting and important\n"
        "3. 2-3 fascinating facts that will grab students' attention\n\n"
        "Keep your response friendly and conversational, suitable for a grade 6 student."
    )

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{
            "role": "user",
            "content": prompt
        }],
        max_tokens=500
    )
    return response.choices[0].message.content


def generate_response_with_retrieval(query, index_path, corpus_path, topic_name=None):
    """
    Generate a response to a student's question using a combination of retrieval and GPT-4o
    """
    # Retrieve content using FAISS
    retrieved_results = query_faiss(query, index_path, corpus_path)
    retrieved_text = "\n".join([f"{idx + 1}. {content}" for idx, (content, _) in enumerate(retrieved_results)])

    context = f"about {topic_name}" if topic_name else ""

    # Generate response using GPT
    prompt = (
        "You are EduGen, a friendly and professional grade 6 science tutor. Your responses should be:\n"
        "- Clear and easy to understand for 11-12 year olds\n"
        "- Engaging and conversational\n"
        "- Include relevant examples or analogies when possible\n"
        "- Encourage curiosity and critical thinking\n\n"
        f"Based on the following curriculum material {context}:\n{retrieved_text}\n\n"
        f"Question: {query}\n\n"
        "Respond in a friendly, encouraging way that helps the student understand the concept clearly."
    )

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{
            "role": "user",
            "content": prompt
        }],
        max_tokens=800,
        temperature=0.7
    )
    return response.choices[0].message.content

if __name__ == "__main__":
    query = "Explain the topic of animals."
    response = generate_response_with_retrieval(query, '../rag_preprocessing/faiss_index',
                                                '../rag_preprocessing/corpus.csv')
    print(response)
