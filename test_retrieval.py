import time

from core.retrieval import retrieve

start = time.perf_counter()

result = retrieve("What is RAG?")

print("\nTIMINGS:")
print(result["timings"])

print("\nRERANKED CHUNKS:")
print(len(result["reranked"]))

print("\nTOTAL TIME:")
print(round(time.perf_counter() - start, 2), "seconds")