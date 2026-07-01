<div align="center">
Users can query indexed knowledge using natural language while the retrieval engine automatically gathers relevant context before invoking the local LLM.

---

## Citation Grounding

<p align="center">
<img src="assets/screenshots/Upload4.png" width="90%" alt="Citation Grounding"/>
</p>

Every generated answer is accompanied by citations pointing back to the exact document chunks used during generation.

This significantly improves transparency and reduces hallucinations.

---

## Performance Dashboard

<p align="center">
<img src="assets/screenshots/performance.png" width="90%" alt="Performance"/>
</p>

Displays retrieval metrics including:

- Embedding Time
- Retrieval Time
- Generation Time
- Total Response Latency

---

# Architecture

RetrievalGPT follows a modular Retrieval-Augmented Generation (RAG) architecture inspired by production AI systems.

Rather than directly sending user questions to a language model, the application retrieves relevant information from indexed knowledge sources before generation. This retrieval-first design improves factual accuracy while ensuring every answer is grounded in evidence.

The pipeline consists of six primary stages:

1. User Query
2. Hybrid Retrieval
3. Reciprocal Rank Fusion
4. Context Assembly
5. Local LLM Inference
6. Citation-Grounded Response

---

## Retrieval Pipeline

```mermaid
flowchart LR

A([User Query])

A --> B{Hybrid Retrieval}

B --> C[Semantic Search<br/>ChromaDB]

B --> D[Keyword Search<br/>BM25]

C --> E[Reciprocal Rank Fusion]

D --> E

E --> F[Top-k Retrieved Chunks]

F --> G[Prompt Construction]

G --> H[Local LLM<br/>Llama 3.2 via Ollama]

H --> I([Citation Grounded Answer])

style A fill:#6C63FF,color:#fff
style B fill:#303030,color:#fff
style C fill:#7B61FF,color:#fff
style D fill:#0EA5A4,color:#fff
style E fill:#F59E0B,color:#fff
style F fill:#8B5CF6,color:#fff
style G fill:#EC4899,color:#fff
style H fill:#EF4444,color:#fff
style I fill:#10B981,color:#fff
```

---

## Document Ingestion Pipeline

Every supported data source follows a unified ingestion workflow.
</div>