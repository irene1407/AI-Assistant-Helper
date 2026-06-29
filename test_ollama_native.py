import time
from ollama import chat

start = time.perf_counter()

response = chat(
    model="llama3.2",
    messages=[
        {
            "role": "user",
            "content": "What is RAG? Answer in one sentence."
        }
    ]
)

print(response["message"]["content"])

elapsed = time.perf_counter() - start

print("TIME:", round(elapsed,2), "seconds")