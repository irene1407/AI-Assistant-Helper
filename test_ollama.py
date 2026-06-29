import time
from langchain_ollama import ChatOllama

llm = ChatOllama(
    model="llama3.2:latest",
    temperature=0,
)

start = time.perf_counter()

response = llm.invoke(
    "What is RAG? Answer in one sentence."
)

elapsed = time.perf_counter() - start

print("TIME:", round(elapsed, 2), "seconds")
print(response.content)