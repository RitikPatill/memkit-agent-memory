from __future__ import annotations

import uuid
from typing import Any

import chromadb
import frontmatter
from sentence_transformers import SentenceTransformer

from memkit.config import CHROMA_PATH, COLLECTION_NAME, EMBED_MODEL


def _sanitize_metadata(meta: dict) -> dict:
    """Convert any non-scalar metadata values to strings for ChromaDB."""
    result = {}
    for k, v in meta.items():
        if isinstance(v, list):
            result[k] = ",".join(str(i) for i in v)
        elif isinstance(v, (str, int, float, bool)):
            result[k] = v
        else:
            result[k] = str(v)
    return result


class MemoryStore:
    def __init__(
        self,
        chroma_path: str = CHROMA_PATH,
        collection_name: str = COLLECTION_NAME,
        embed_model: str = EMBED_MODEL,
    ) -> None:
        self._model = SentenceTransformer(embed_model)
        self._client = chromadb.PersistentClient(path=chroma_path)
        self._collection = self._client.get_or_create_collection(collection_name)

    def add(self, text: str, metadata: dict | None = None) -> str:
        post = frontmatter.loads(text)
        body: str = post.content
        merged: dict[str, Any] = _sanitize_metadata(dict(post.metadata))
        if metadata:
            merged.update(_sanitize_metadata(metadata))

        uid = str(uuid.uuid4())
        embedding = self._model.encode(body).tolist()
        self._collection.add(
            documents=[body],
            embeddings=[embedding],
            metadatas=[merged],
            ids=[uid],
        )
        return uid

    def search(self, query: str, k: int = 5) -> list[dict]:
        count = self._collection.count()
        if count == 0:
            return []
        k = min(k, count)
        embedding = self._model.encode(query).tolist()
        results = self._collection.query(
            query_embeddings=[embedding],
            n_results=k,
            include=["documents", "metadatas", "distances"],
        )
        output = []
        for i, doc_id in enumerate(results["ids"][0]):
            output.append(
                {
                    "id": doc_id,
                    "text": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i],
                    "score": float(results["distances"][0][i]),
                }
            )
        return output

    def list(self) -> list[dict]:
        results = self._collection.get(include=["documents", "metadatas"])
        output = []
        for i, doc_id in enumerate(results["ids"]):
            output.append(
                {
                    "id": doc_id,
                    "text": results["documents"][i],
                    "metadata": results["metadatas"][i],
                }
            )
        return output

    def delete(self, memory_id: str) -> None:
        self._collection.delete(ids=[memory_id])
