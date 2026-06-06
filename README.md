![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue) ![License MIT](https://img.shields.io/badge/license-MIT-green)

# MemKit

**Self-hosted memory backend for LLM agents — no cloud account required.**

Give your agent persistent, semantic memory in one command. MemKit stores Markdown snippets locally, embeds them with a CPU-friendly model, and serves them over a clean REST API that any framework can call.

---

## Why MemKit

Most agent tutorials either skip memory entirely or offload it to Pinecone or Weaviate. Developers prototyping locally shouldn't need a cloud account and a credit card to give their agent a memory. MemKit runs with one command and survives process restarts.

---

## Status

**M4 — CLI + Python client complete.**

| Item | Details |
|------|---------|
| Package layout | `src/memkit/` with `__init__.py`, `config.py`, `store.py`, `server.py`, `client.py`, `cli.py` |
| `MemoryStore` | `add`, `search`, `list`, `delete` — fully functional |
| `MemKitClient` | Synchronous Python client wrapping all four REST endpoints via `httpx` |
| CLI | `memkit add/search/list` — Typer app, supports `MEMKIT_URL` env var |
| Embedding | `all-MiniLM-L6-v2` via `sentence-transformers`, CPU-only |
| Storage | ChromaDB with file-system persistence (`./chroma_data/`) |
| Front-matter parsing | `python-frontmatter` — YAML metadata extracted automatically |
| REST API | FastAPI server with 5 endpoints; lifespan hook initialises the store |
| Test suite | `tests/test_store.py` + `tests/test_server.py` + `tests/test_client.py` + `tests/test_cli.py` |
| Dependency manifest | `requirements.txt` with all runtime deps pinned |
| Build config | `pyproject.toml` declaring the `memkit` entry-point |
| Docker | `docker-compose.yml` + `Dockerfile` — `docker compose up` starts the server |
| Chatbot example | `examples/chatbot.py` — memory-augmented chat via Anthropic API |
| License | MIT (`LICENSE`) |

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
 ┌────────────────────────────────────────────┐
 │  Access Layer                               │
 │  memkit CLI  │  MemKitClient  │  HTTP/curl  │
 └─────────────────────┬──────────────────────┘
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
# 1. Install the package and start the server
pip install -e .
docker compose up          # or: uvicorn memkit.server:app --reload

# 2. Store a memory
memkit add "User prefers concise answers."

# 3. Retrieve semantically similar memories
memkit search "how should I respond" --k 3
```

Raw HTTP also works against the same server — see [API Endpoints](#api-endpoints).

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

```bash
pip install -e .

# Start the server first (or use docker compose up)
# Then use the CLI:
memkit add "The user's name is Alice."
memkit add path/to/memory.md           # read from file
memkit search "what is the user's name"
memkit list

# Point at a non-default server
MEMKIT_URL=http://myserver:8000 memkit list
```

| Command | Description |
|---------|-------------|
| `memkit add <text\|file>` | Store a memory (raw text or Markdown file) |
| `memkit search <query>` | Semantic search (use `--k N` for top-N results) |
| `memkit list` | List all memories |

## Python Client

```python
from memkit import MemKitClient

client = MemKitClient("http://localhost:8000")

# Store a memory
memory_id = client.add("The user prefers concise answers.")

# Semantic search
results = client.search("how should I format responses?", k=3)
for r in results:
    print(r["score"], r["text"])

# List all
all_memories = client.list()

# Delete by ID
client.delete(memory_id)
```

---

## Examples

### Memory-augmented chatbot

`examples/chatbot.py` is a terminal chat loop that retrieves the top-3 relevant
memories on each turn and injects them as a system prompt before calling the
Anthropic API.

```bash
# Seed some memories first
memkit add "The user's name is Alice."
memkit add "The user prefers concise, bullet-point answers."

# Run the chatbot (requires a running MemKit server)
ANTHROPIC_API_KEY=sk-... python examples/chatbot.py
```

The bot will incorporate stored facts automatically without any manual prompt
engineering.

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
| **M4** ✓ | CLI (`memkit add/search/list`), `MemKitClient`, chatbot example |

---

## License

MIT — see [LICENSE](LICENSE).
