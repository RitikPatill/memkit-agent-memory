# Contributing to MemKit

## Dev setup

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt -r requirements-dev.txt
pip install -e .
```

## Running tests

```bash
pytest tests/ -v
```

All tests mock the embedder — no model download required.

## Running the server locally

```bash
uvicorn memkit.server:app --reload
```

Server starts at `http://localhost:8000`. The `chroma_data/` directory is created automatically.

## PR conventions

- Branch naming: `feat/<topic>` or `fix/<topic>`
- One logical change per PR
- New behaviour must include tests
- Keep commits atomic; squash fixups before opening PR

## Code style

`ruff>=0.4` is the recommended linter (optional, not in dev deps):

```bash
pip install ruff
ruff check src/ tests/
```
