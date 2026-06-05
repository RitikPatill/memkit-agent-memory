![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue) ![License MIT](https://img.shields.io/badge/license-MIT-green)

# MemKit

**Self-hosted memory backend for LLM agents — no cloud account required.**

Give your agent persistent, semantic memory in one command. MemKit stores Markdown snippets locally, embeds them with a CPU-friendly model, and serves them over a clean REST API that any framework can call.

---

## Why MemKit

Most agent tutorials either skip memory entirely or offload it to Pinecone or Weaviate. Developers prototyping locally shouldn't need a cloud account and a credit card to give their agent a memory. MemKit runs with one command and survives process restarts.

---

## Status

**M3 — FastAPI REST server complete.**

| Item | Details |
|------|---------|
| Package layout | `src/memkit/` with `__init__.py`, `config.py`, `store.py`, `server.py` |
| `MemoryStore` | `add`, `search`, `list`, `delete` — fully functional |
| Embedding | `all-MiniLM-L6-v2` via `sentence-transformers`, CPU-only |
| Storage | ChromaDB with file-system persistence (`./chroma_data/`) |
| Front-matter parsing | `python-frontmatter` — YAML metadata extracted automatically |
| REST API | FastAPI server with 5 endpoints; lifespan hook initialises the store |
| Test suite | `tests/test_store.py` + `tests/test_server.py` — full coverage |
| Dependency manifest | `requirements.txt` with all runtime deps pinned |
| Build config | `pyproject.toml` declaring the `memkit` entry-point (wired in M4) |
| Docker | `docker-compose.yml` + `Dockerfile` — `docker compose up` starts the server |
| License | MIT (`LICENSE`) |

The CLI is implemented in M4. See the [Roadmap](#roadmap).

### Using `MemoryStore` directly

```python
from memkit import MemoryStore

store = MemoryStore()  # persists to ./chroma_data/ by default

# Store a plain memory
store.add("The user prefers concise answers.")

# Store a memory with YAML front-matter
store.add("""---
tags: [preference, tone]
source: conversation
---
User prefers bullet-point answers over long paragraphs.""")

# Semantic search
results = store.search("how should I format responses?", k=3)
for r in results:
    print(r["score"], r["text"])

# List all
all_memories = store.list()

# Delete by ID
store.delete(results[0]["id"])
```

---

## Architecture

```
 Agent / Client
      │
      │  HTTP (REST)
      ▼
 ┌─────────────────────────────┐
 │        FastAPI Server        │
 │  POST /memories              │
 │  GET  /memories/search?q=…   │
 │  GET  /memories              │
 │  DELETE /memories/{id}       │
 └────────────┬────────────────┘
              │
              ▼
 ┌─────────────────────────────┐
 │   sentence-transformers      │
 │   all-MiniLM-L6-v2 (CPU)    │
 │   ~80 MB, no API key         │
 └────────────┬────────────────┘
              │  embeddings
              ▼
 ┌─────────────────────────────┐
 │   ChromaDB (disk)            │
 │   ./chroma_data/             │
 │   persists across restarts   │
 └─────────────────────────────┘
```

---

## Quick Start

```bash
# 1. Start the server
docker compose up

# 2. Store a memory
curl -X POST http://localhost:8000/memories \
  -H "Content-Type: application/json" \
  -d '{"text": "User prefers concise answers."}'

# 3. Retrieve semantically similar memories
curl "http://localhost:8000/memories/search?q=how+should+I+respond&k=3"
```

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/healthz` | Health check — returns `{"status": "ok"}` |
| `POST` | `/memories` | Store a new memory snippet (returns `201`) |
| `GET` | `/memories/search?q=...&k=5` | Semantic top-k retrieval |
| `GET` | `/memories` | List all memories with metadata |
| `DELETE` | `/memories/{memory_id}` | Remove a memory by ID (returns `204`) |

---

## CLI Usage

> **Not yet functional.** The CLI entry-point (`memkit.cli:app`) is declared in `pyproject.toml` but implemented in M4.

```bash
pip install -e .

memkit add "The user's name is Alice."
memkit search "what is the user's name"
memkit list
```

| Command | Description |
|---------|-------------|
| `memkit add <text>` | Store a memory |
| `memkit search <query>` | Semantic search |
| `memkit list` | List all memories |

---

## How It Works

1. **Embed** — incoming text is passed through `all-MiniLM-L6-v2` to produce a 384-dimensional vector.
2. **Store** — the vector plus original text and YAML front-matter metadata are written to ChromaDB on disk.
3. **Retrieve** — at query time the same model embeds the query and ChromaDB returns the top-k nearest neighbours by cosine similarity.

Memory snippets are plain Markdown and can include optional YAML front-matter:

```markdown
---
tags: [preference, tone]
source: conversation
created_at: 2026-06-01
---
User prefers bullet-point answers over long paragraphs.
```

---

## Roadmap

| Milestone | What ships |
|-----------|-----------|
| **M1** ✓ | Scaffold, README, package layout |
| **M2** ✓ | `MemoryStore`: embed, store, search, list, delete + unit tests |
| **M3** ✓ | FastAPI server (`server.py`), 5 endpoints, Docker image |
| **M4** | CLI (`memkit add/search/list`) |
| **M5** | Python client class + chatbot integration example |

---

## License

MIT — see [LICENSE](LICENSE).
