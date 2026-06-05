import pytest
from memkit.store import MemoryStore


def test_add_and_list(tmp_path):
    store = MemoryStore(chroma_path=str(tmp_path))
    uid = store.add("The sky is blue.")
    assert isinstance(uid, str) and len(uid) > 0

    memories = store.list()
    assert len(memories) == 1
    assert memories[0]["id"] == uid
    assert memories[0]["text"] == "The sky is blue."


def test_add_with_frontmatter(tmp_path):
    store = MemoryStore(chroma_path=str(tmp_path))
    text = "---\ntags: [preference, tone]\nsource: test\n---\nUser prefers bullet points."
    uid = store.add(text)

    memories = store.list()
    assert len(memories) == 1
    mem = memories[0]
    assert mem["text"] == "User prefers bullet points."
    assert mem["metadata"]["source"] == "test"
    # tags list is stored as comma-joined string
    assert "preference" in mem["metadata"]["tags"]


def test_search_returns_relevant(tmp_path):
    store = MemoryStore(chroma_path=str(tmp_path))
    store.add("The capital of France is Paris.")
    store.add("Python is a programming language.")

    results = store.search("What is the capital city of France?", k=1)
    assert len(results) == 1
    assert "Paris" in results[0]["text"]


def test_delete_removes_entry(tmp_path):
    store = MemoryStore(chroma_path=str(tmp_path))
    uid = store.add("Temporary memory.")
    store.delete(uid)

    memories = store.list()
    assert memories == []


def test_search_k_respected(tmp_path):
    store = MemoryStore(chroma_path=str(tmp_path))
    store.add("Memory about cats.")
    store.add("Memory about dogs.")
    store.add("Memory about birds.")

    results = store.search("animals", k=2)
    assert len(results) == 2
