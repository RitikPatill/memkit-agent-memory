from __future__ import annotations

import pathlib

import typer

from memkit.client import MemKitClient

app = typer.Typer(help="MemKit — self-hosted memory backend for LLM agents.")

BASE_URL_OPT = typer.Option(
    "http://localhost:8000",
    envvar="MEMKIT_URL",
    help="MemKit server URL.",
)


@app.command()
def add(
    text_or_file: str = typer.Argument(..., help="Text to store, or path to a file."),
    base_url: str = BASE_URL_OPT,
) -> None:
    """Store a memory (plain text or a Markdown file)."""
    p = pathlib.Path(text_or_file)
    if p.is_file():
        text = p.read_text(encoding="utf-8")
    else:
        text = text_or_file

    client = MemKitClient(base_url)
    memory_id = client.add(text)
    typer.echo(f"Stored memory with id: {memory_id}")


@app.command()
def search(
    query: str = typer.Argument(..., help="Search query."),
    k: int = typer.Option(5, help="Number of results to return."),
    base_url: str = BASE_URL_OPT,
) -> None:
    """Semantic search across stored memories."""
    client = MemKitClient(base_url)
    results = client.search(query, k=k)
    if not results:
        typer.echo("No results found.")
        return
    for i, r in enumerate(results, 1):
        score = r.get("score", 0.0)
        text = r.get("text", "")
        typer.echo(f"[{i}] (score={score:.2f}) {text}")


@app.command(name="list")
def list_memories(
    base_url: str = BASE_URL_OPT,
) -> None:
    """List all stored memories."""
    client = MemKitClient(base_url)
    memories = client.list()
    if not memories:
        typer.echo("No memories stored.")
        return
    for m in memories:
        memory_id = m.get("id", "")
        text = m.get("text", "")[:80]
        typer.echo(f"[{memory_id}] {text}")
