![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue) ![License MIT](https://img.shields.io/badge/license-MIT-green)

# MemKit

**Self-hosted memory backend for LLM agents — no cloud account required.**

Give your agent persistent, semantic memory in one command. MemKit stores Markdown snippets locally, embeds them with a CPU-friendly model, and serves them over a clean REST API that any framework can call.

---

## Why MemKit

Most agent tutorials either skip memory entirely or offload it to Pinecone or Weaviate. Developers prototyping locally shouldn't need a cloud account and a credit card to give their agent a memory. MemKit runs with one command and survives process restarts.

---

## Status

**M1 — scaffold complete.** The following are in place; nothing beyond this list is functional yet.

| Item | Details |
|------|---------|
| Package layout | `src/memkit/` with `__init__.py` and `config.py` |
| Dependency manifest | `requirements.txt` with pinned versions of FastAPI, Uvicorn, sentence-transformers, ChromaDB, python-frontmatter, Typer, Pydantic |
| Build config | `pyproject.toml` declaring the `memkit` entry-point (wired in M4) |
| Docker stub | `docker-compose.yml` + `Dockerfile` — server is not yet wired; see M3 |
| Test harness | `tests/test_scaffold.py` verifying package import and layout |
| License | MIT (`LICENSE`) |

Embedding, storage, the REST server, and the CLI are implemented in M2–M4 respectively. See the [Roadmap](#roadmap).

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

> **Not yet functional.** The server is wired in M3. The commands below reflect the intended end-state.

```bash
# 1. Start the server
docker compose up

# 2. Store a memory
curl -X POST http://localhost:8000/memories \
  -H "Content-Type: application/json" \
  -d '{"content": "User prefers concise answers."}'

# 3. Retrieve semantically similar memories
curl "http://localhost:8000/memories/search?q=how+should+I+respond&k=3"
```

---

## API Endpoints

> **Not yet functional.** The FastAPI server ships in M3.

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/memories` | Store a new memory snippet |
| `GET` | `/memories/search?q=...&k=5` | Semantic top-k retrieval |
| `GET` | `/memories` | List all memories with metadata |
| `DELETE` | `/memories/{id}` | Remove a memory by ID |

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
| **M1** (now) | Scaffold, README, package layout |
| **M2** | Embedding + ChromaDB core (`store`, `search`) |
| **M3** | FastAPI server, Docker image |
| **M4** | CLI (`memkit add/search/list`) |
| **M5** | Python client class + chatbot integration example |

---

## License

MIT — see [LICENSE](LICENSE).
