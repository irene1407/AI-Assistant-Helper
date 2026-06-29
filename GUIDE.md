# 🧠 How to Build a RAG System — A Guide for 10-Year-Olds

Think of this project like building a **super-smart robot librarian**. 
Here's how everything works and how to build it yourself!

---

## 🤔 What Are We Building?

Imagine you have a **giant pile of books and documents**. 
You want to ask questions like *"What does chapter 3 say about dinosaurs?"* 
and get a perfect answer with the exact page number.

That's exactly what this system does — for ANY documents you give it!

---

## 🧩 The 5 Main Parts (Think of LEGO Blocks)

### 🧱 Block 1: The Brain (Ollama + Llama 3.2)
- **What it is:** A free AI brain that runs on YOUR computer (no internet needed!)
- **What it does:** Reads the document pieces we give it and writes an answer
- **Kid analogy:** Like a really smart friend who reads the books for you

### 🧱 Block 2: The Memory (ChromaDB)
- **What it is:** A special database that stores documents as "number patterns" called embeddings
- **What it does:** Finds documents that MEAN the same thing as your question, even if different words
- **Kid analogy:** Like a magic filing cabinet that groups similar ideas together

### 🧱 Block 3: The Index (BM25)
- **What it is:** A keyword search engine (like the index at the back of a textbook)
- **What it does:** Finds documents containing the EXACT words you searched for
- **Kid analogy:** Like Ctrl+F (Find) on a computer, but smarter

### 🧱 Block 4: The Judge (Cross-Encoder Re-ranker)
- **What it is:** A smaller AI that double-checks which document pieces are TRULY relevant
- **What it does:** Takes the best results from Block 2 and 3, then picks the absolute best ones
- **Kid analogy:** Like a teacher checking your homework and ranking the best answers

### 🧱 Block 5: The Report Card (Ragas + Observability)
- **What it is:** A scoring system that checks if answers are honest and accurate
- **What it does:** Measures if the AI made up information (hallucinated) or used real sources
- **Kid analogy:** Like a spell-checker, but for FACTS instead of spelling

---

## 🚀 Step-by-Step: How to Build This Project

### Step 1: Install the Tools

These are all the software "LEGO pieces" you need:

```
1. Install Python (the programming language we use)
   → Go to python.org and download Python 3.11

2. Install Ollama (the local AI brain)
   → Go to ollama.com and click Download
   → This lets you run AI for FREE on your computer!

3. Download an AI model
   → Open your terminal (black box where you type commands)
   → Type: ollama pull llama3.2
   → Wait for it to download (it's about 2GB, like a big game download)

4. Also download the embedding model:
   → Type: ollama pull nomic-embed-text
```

### Step 2: Set Up the Project Folder

```
📁 rag-system/           ← Main folder (like a school project folder)
│
├── 📁 config/           ← Settings files
│   └── prompts.yaml     ← The instructions we give the AI (like a recipe)
│
├── 📁 core/             ← The main engine parts
│   ├── ingestion.py     ← Reads and chops up your documents
│   ├── retrieval.py     ← Searches for relevant pieces
│   └── generation.py   ← Writes the final answer
│
├── 📁 observability/    ← The "black box recorder" (like on airplanes)
│   └── tracker.py       ← Records everything that happens
│
├── 📁 evaluation/       ← The test/grading system
│   └── evaluate_pipeline.py  ← Grades how good the AI is
│
├── 📁 data/             ← Where documents and databases are stored
│   └── golden_set.json  ← 10 test questions with correct answers
│
└── app.py               ← The website interface you see
```

### Step 3: Install Python Libraries

Open your terminal and type:
```
pip install streamlit chromadb langchain langchain-ollama \
    rank-bm25 sentence-transformers ragas pyyaml \
    pypdf beautifulsoup4 plotly pandas
```

This installs all the helper tools — like adding LEGO pieces to your collection.

### Step 4: Understanding Each File

#### 📄 `config/prompts.yaml` — The AI's Instructions
This file tells the AI the RULES it must follow:
- "Always say WHERE you found the information"
- "If you don't know, say so — don't make things up!"
- "Write [Source: filename, Chunk #3] after every fact"

It's like the rules your teacher gives before a test.

#### 📄 `core/ingestion.py` — The Document Chopper
When you upload a PDF or text file, this code:
1. **Reads** the whole document
2. **Chops** it into pieces (called "chunks") — about 600 words each
3. **Overlaps** pieces by 100 words so we don't lose context at the edges
4. **Converts** each piece to a number pattern (embedding) using the nomic-embed-text AI
5. **Stores** everything in ChromaDB's memory

*Why chop it up?* Because AI can only read a small amount at once — like how you read a book chapter by chapter, not all at once!

#### 📄 `core/retrieval.py` — The Detective
When you ask a question, this code:
1. **Vector search:** Finds pieces that MEAN the same as your question (top 10)
2. **BM25 search:** Finds pieces with the EXACT same words (top 10)
3. **RRF merge:** Combines both lists fairly (like averaging two judges' scores)
4. **Cross-encoder:** Re-reads the top 20 and picks the best 4

*The RRF math (Reciprocal Rank Fusion):*
Score = 1/(60 + position_in_list_1) + 1/(60 + position_in_list_2)
The "60" is to prevent a big gap between rank 1 and rank 2.

#### 📄 `core/generation.py` — The Answer Writer
1. **Sufficiency check:** Asks the AI "do these chunks actually answer the question?"
2. **If YES:** Writes a full answer WITH citations like [Source: document.pdf, Chunk #3]
3. **If NO:** Returns "Evidence insufficient to answer this query safely."

This STOPS the AI from making things up (called "hallucinating")!

#### 📄 `observability/tracker.py` — The Black Box
Records EVERYTHING in a database:
- How long did it take? (latency)
- How many words were processed? (tokens)
- Did the AI cite its sources? (citation coverage)
- Did it refuse to answer? (refusal tracking)

Then calculates:
- **P50 latency:** The "middle" response time (50% faster, 50% slower)
- **P95 latency:** The "worst" response time for 95% of requests

#### 📄 `evaluation/evaluate_pipeline.py` — The Report Card
Uses 10 test questions (in `data/golden_set.json`) to grade the whole system:
- **Faithfulness score:** Did the AI stick to what the documents said? (0.0 to 1.0)
- **Answer Relevancy:** Did it actually answer the question? (0.0 to 1.0)
- **CI/CD Gate:** If Faithfulness < 0.85, it FAILS (like a real software quality check!)

#### 📄 `app.py` — The Website
A two-page website:
- **Page 1 (RAG Workspace):** Upload documents and ask questions
- **Page 2 (Ops Dashboard):** See charts of how well the system is performing

### Step 5: Run the System

```bash
# In your terminal, go to the rag-system folder:
cd rag-system

# Start everything:
bash start.sh
```

Then open your web browser and go to: **http://localhost:8080**

### Step 6: Test It Out!

1. **Upload a document** — Try a PDF from school or a Wikipedia article saved as text
2. **Ask a question** — "What does this say about [topic]?"
3. **See the answer** with citations showing exactly where the information came from
4. **Check the Dashboard** — See how fast and accurate the system is

---

## 🎯 How the Full Pipeline Works (Step by Step)

```
YOU ASK: "What causes earthquakes?"
         ↓
[1] EMBED your question → [0.23, -0.54, 0.87, ...]  (a number pattern)
         ↓
[2] VECTOR SEARCH → Finds top 10 chunks about earthquakes by meaning
[3] BM25 SEARCH   → Finds top 10 chunks containing the word "earthquakes"
         ↓
[4] RRF MERGE → Combines both lists, top 20 candidates
         ↓
[5] CROSS-ENCODER → Re-reads all 20, selects the best 4 chunks
         ↓
[6] SUFFICIENCY CHECK → "Do these 4 chunks actually answer the question?"
         ↓
[7] IF YES: LLM writes answer WITH citations
    IF NO:  Returns "Evidence insufficient to answer this query safely."
         ↓
[8] TRACKER logs: time taken, tokens used, citations found
         ↓
YOU SEE: "Earthquakes are caused by... [Source: geology.pdf, Chunk #7]"
```

---

## 📊 The Numbers You'll See

| Metric | What it means | Good value |
|--------|--------------|------------|
| **P50 latency** | Half your answers are faster than this | < 5,000 ms |
| **P95 latency** | 95% of answers are faster than this | < 15,000 ms |
| **Faithfulness** | Are answers based on real documents? | > 0.85 |
| **Citation coverage** | % of facts that have a source cited | > 70% |
| **Refusal rate** | % of questions answered "I don't know" | < 20% |

---

## 🏆 Why This is a "Gold Standard" Project

1. **Real hybrid search** — combines semantic AND keyword search (most systems only do one!)
2. **Re-ranking** — double-checks results with a second, more precise AI
3. **Citation enforcement** — forces the AI to PROVE its answers
4. **Hallucination prevention** — refuses to answer when evidence is weak
5. **Full observability** — records everything like a flight recorder
6. **Automated evaluation** — grades itself like a student taking a test
7. **CI/CD gate** — automatically fails if quality drops below threshold

---

## 🐛 Troubleshooting

**"Ollama offline" message?**
→ Wait 1-2 minutes for models to download on first run

**"No chunks found" when searching?**
→ Upload a document first in the RAG Workspace tab

**Answer seems wrong?**
→ The document you uploaded may not contain the answer — try asking about what's in the document

**Evaluation fails?**
→ The AI quality dropped — check if Ollama is using the right model

---

*Built with: Python, Streamlit, LangChain, ChromaDB, BM25, Sentence-Transformers, Ragas, Ollama*
