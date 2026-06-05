from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, Request, Response
from pydantic import BaseModel

from memkit.store import MemoryStore


# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------

class AddRequest(BaseModel):
    text: str
    metadata: dict | None = None


class MemoryResponse(BaseModel):
    id: str
    text: str
    metadata: dict
    score: float | None = None


class AddResponse(BaseModel):
    id: str


# ---------------------------------------------------------------------------
# Lifespan — initialise a single shared store on startup
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.store = MemoryStore()
    yield


app = FastAPI(title="MemKit", lifespan=lifespan)


# ---------------------------------------------------------------------------
# Dependency
# ---------------------------------------------------------------------------

def get_store(request: Request) -> MemoryStore:
    return request.app.state.store


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/healthz")
def healthz():
    return {"status": "ok"}


@app.post("/memories", response_model=AddResponse, status_code=201)
def add_memory(body: AddRequest, store: MemoryStore = Depends(get_store)):
    uid = store.add(body.text, body.metadata)
    return AddResponse(id=uid)


@app.get("/memories/search", response_model=list[MemoryResponse])
def search_memories(q: str, k: int = 5, store: MemoryStore = Depends(get_store)):
    results = store.search(q, k=k)
    return [MemoryResponse(**r) for r in results]


@app.get("/memories", response_model=list[MemoryResponse])
def list_memories(store: MemoryStore = Depends(get_store)):
    results = store.list()
    return [MemoryResponse(**r) for r in results]


@app.delete("/memories/{memory_id}", status_code=204)
def delete_memory(memory_id: str, store: MemoryStore = Depends(get_store)):
    store.delete(memory_id)
    return Response(status_code=204)
