
# Local RAG Chatbot

A fully local, zero-API-cost Retrieval-Augmented Generation (RAG) chatbot that lets you chat with your own PDF documents — no external API keys, no cloud costs, no internet dependency after setup.

Built as a hands-on deep dive into how RAG systems actually work under the hood: from raw PDF text to a working conversational interface, with every piece implemented and understood rather than treated as a black box.

## What it does

Upload PDFs, ask questions in plain English, and get answers grounded in the actual content of your documents — powered entirely by tools running on your own machine.

## Tech Stack

| Component | Tool |
|---|---|
| PDF text extraction | `pdfplumber` |
| Text chunking | Custom sliding-window chunker with overlap |
| Embeddings | `sentence-transformers` (`all-MiniLM-L6-v2`) |
| Vector storage & search | PostgreSQL + `pgvector` |
| LLM | Ollama (`llama3.2:3b`) |
| Ingestion automation | `watchdog` (folder-watching service) |
| UI | Streamlit |

## Architecture

```
                        INGESTION PIPELINE
PDF → Extract Text → Chunk (with overlap) → Embed → Store in PostgreSQL (pgvector)

                        QUERY PIPELINE
User Question → Embed → Vector Similarity Search → Retrieve Top Chunks
                                                          ↓
                                            Build Prompt with Context
                                                          ↓
                                              Ollama LLM → Answer
```

## Key Design Decisions

**PostgreSQL + pgvector over a flat file / pickle store**
Chose a real vector database from the start instead of an in-memory or pickle-based approach. This meant learning proper SQL-based similarity search (`<=>` cosine distance operator) and handling persistent, queryable storage — the same pattern used in real-world production RAG systems.

**Hash-based deduplication over filename-based tracking**
Initially tracked processed files by filename, but this breaks if a file is renamed or if content changes but the name doesn't. Switched to MD5 content hashing, so the system can reliably detect "have I seen this exact content before?" regardless of filename — and correctly reprocesses files if their content changes.

**Automated folder-watching over manual script execution**
Rather than requiring a manual script run every time a new document is added, built a `watchdog`-based service that automatically detects and ingests new PDFs dropped into a folder — with the hash-check ensuring no duplicate processing. This mirrors how a real ingestion pipeline would work: documents get added by a process, not manually triggered by a person each time.

**Sliding-window chunking with overlap**
Text is split into overlapping chunks rather than clean-cut segments, so that ideas split across a chunk boundary aren't lost entirely in either piece — a common failure mode in naive chunking approaches.

## Project Structure

```
local-rag-chatbot/
├── README.md
├── requirements.txt
├── app.py              # Streamlit chat interface (entry point)
├── src/
│   ├── extract.py      # PDF text extraction
│   ├── chunk.py        # Text chunking with overlap
│   ├── embed.py        # Embedding generation
│   ├── store_pg.py     # Manual ingestion into PostgreSQL
│   ├── watcher.py       # Automated folder-watching ingestion service
│   ├── retrieve.py     # Vector similarity search
│   └── generate.py     # Prompt construction + LLM generation
└── pdfs/                # Drop PDFs here for ingestion
```

## Setup

**Prerequisites:** Python 3.10+, PostgreSQL with `pgvector` extension, [Ollama](https://ollama.com)

```bash
# Install dependencies
pip install -r requirements.txt

# Pull the LLM
ollama pull llama3.2:3b

# Set up the database table
CREATE EXTENSION IF NOT EXISTS vector;
CREATE TABLE document_chunks (
    id SERIAL PRIMARY KEY,
    chunk_text TEXT,
    embedding vector(384),
    source_file TEXT,
    file_hash TEXT
);
```

Update the database credentials in `src/store_pg.py` and `src/retrieve.py` before running.

## Usage

**1. Start the ingestion watcher** (in one terminal — watches the `pdfs/` folder and automatically processes new documents):
```bash
python src/watcher.py
```

**2. Launch the chatbot** (in another terminal):
```bash
streamlit run app.py
```

**3.** Drop PDFs into the `pdfs/` folder, and start asking questions in the browser interface.

## What I learned building this

- How the retrieval half of RAG actually works: embeddings, vector similarity, and why chunk size/overlap decisions matter
- How to work with `pgvector` for real vector search inside a relational database, not just an in-memory library
- The importance of idempotent ingestion pipelines — handling duplicates, content changes, and automation properly rather than relying on manual re-runs
- How prompt construction shapes an LLM's grounding — and how to reduce hallucination by explicitly instructing the model to stick to provided context
- The full gap between a "hello world" LLM call and an actual working retrieval-augmented system

