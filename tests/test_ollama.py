import ollama

response = ollama.chat(
    model="deepseek-r1:8b",
    messages=[
        {
            "role": "user",
            "content": "Explain what RAG is in simple terms."
        }
    ]
)

print(response["message"]["content"])