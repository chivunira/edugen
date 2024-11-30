from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

# OpenAI Client
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
)


def generate_content(prompt):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{
                "role": "user",
                "content": prompt
            }],
            max_tokens=500
        )
        response_message = response.choices[0].message.content
        return response_message
    except Exception as e:
        print(f"Error generating content: {e}")
        return None
