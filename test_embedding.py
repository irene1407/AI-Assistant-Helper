import time
from core.retrieval import _embed_query

start = time.perf_counter()

_embed_query("What is RAG?")

print("TIME:", round(time.perf_counter() - start, 2))