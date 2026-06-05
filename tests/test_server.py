import pytest
from fastapi.testclient import TestClient

from memkit.server import app
from memkit.store import MemoryStore


@pytest.fixture
def client(tmp_path):
    app.state.store = MemoryStore(chroma_path=str(tmp_path))
    return TestClient(app)


def test_healthz(client):
    resp = client.get("/healthz")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_add_memory_returns_201_with_id(client):
    resp = client.post("/memories", json={"text": "The user likes dark mode."})
    assert resp.status_code == 201
    data = resp.json()
    assert "id" in data
    assert data["id"]


def test_add_memory_with_frontmatter_stored_correctly(client):
    text = "---\ntags: [preference]\n---\nUser prefers bullet points."
    client.post("/memories", json={"text": text})
    memories = client.get("/memories").json()
    assert len(memories) == 1
    assert "bullet" in memories[0]["text"]


def test_search_returns_results_with_score(client):
    client.post("/memories", json={"text": "Python is a great language."})
    resp = client.get("/memories/search", params={"q": "programming languages", "k": 1})
    assert resp.status_code == 200
    results = resp.json()
    assert len(results) == 1
    r = results[0]
    assert "id" in r
    assert "text" in r
    assert "score" in r
    assert r["score"] is not None


def test_list_returns_all_memories(client):
    client.post("/memories", json={"text": "Memory one."})
    client.post("/memories", json={"text": "Memory two."})
    resp = client.get("/memories")
    assert resp.status_code == 200
    assert len(resp.json()) == 2


def test_delete_removes_memory(client):
    add_resp = client.post("/memories", json={"text": "To be deleted."})
    uid = add_resp.json()["id"]

    del_resp = client.delete(f"/memories/{uid}")
    assert del_resp.status_code == 204

    memories = client.get("/memories").json()
    assert all(m["id"] != uid for m in memories)


def test_delete_nonexistent_returns_204(client):
    resp = client.delete("/memories/nonexistent-id-xyz")
    assert resp.status_code == 204
