from __future__ import annotations

import httpx


class MemKitClient:
    """Synchronous HTTP client wrapping the MemKit REST API."""

    def __init__(self, base_url: str = "http://localhost:8000") -> None:
        self._base_url = base_url.rstrip("/")

    def add(self, text: str, metadata: dict | None = None) -> str:
        """Store a memory and return its ID."""
        payload: dict = {"text": text}
        if metadata:
            payload["metadata"] = metadata
        with httpx.Client() as client:
            response = client.post(f"{self._base_url}/memories", json=payload)
            response.raise_for_status()
            return response.json()["id"]

    def search(self, query: str, k: int = 5) -> list[dict]:
        """Semantic top-k retrieval. Returns a list of memory dicts."""
        with httpx.Client() as client:
            response = client.get(
                f"{self._base_url}/memories/search",
                params={"q": query, "k": k},
            )
            response.raise_for_status()
            return response.json()

    def list(self) -> list[dict]:
        """List all memories with metadata."""
        with httpx.Client() as client:
            response = client.get(f"{self._base_url}/memories")
            response.raise_for_status()
            return response.json()

    def delete(self, memory_id: str) -> None:
        """Remove a memory by ID."""
        with httpx.Client() as client:
            response = client.delete(f"{self._base_url}/memories/{memory_id}")
            response.raise_for_status()
