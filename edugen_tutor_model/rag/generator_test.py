from edugen_tutor_model.rag.gpt_generator import generate_content

def test_gpt_plugin():
    query = "Explain the topic of animals."
    response = generate_content(query)
    if response:
        print("Response from GPT plugin:")
        print(response)
    else:
        print("No response received or an error occurred.")


if __name__ == "__main__":
    test_gpt_plugin()