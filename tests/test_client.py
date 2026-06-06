"""Unit tests for MemKitClient using mocked httpx."""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from memkit.client import MemKitClient


def _make_response(json_data, status_code: int = 200) -> MagicMock:
    response = MagicMock()
    response.status_code = status_code
    response.json.return_value = json_data
    response.raise_for_status.return_value = None
    return response


class TestMemKitClientAdd:
    def test_add_returns_id(self):
        with patch("memkit.client.httpx.Client") as mock_cls:
            mock_http = mock_cls.return_value.__enter__.return_value
            mock_http.post.return_value = _make_response({"id": "abc"}, 201)

            client = MemKitClient("http://localhost:8000")
            result = client.add("hello world")

        assert result == "abc"
        mock_http.post.assert_called_once_with(
            "http://localhost:8000/memories",
            json={"text": "hello world"},
        )

    def test_add_with_metadata(self):
        with patch("memkit.client.httpx.Client") as mock_cls:
            mock_http = mock_cls.return_value.__enter__.return_value
            mock_http.post.return_value = _make_response({"id": "xyz"}, 201)

            client = MemKitClient()
            result = client.add("text", metadata={"tags": ["test"]})

        assert result == "xyz"
        _, kwargs = mock_http.post.call_args
        assert kwargs["json"]["metadata"] == {"tags": ["test"]}


class TestMemKitClientSearch:
    def test_search_returns_list(self):
        fake_results = [
            {"id": "1", "text": "relevant memory", "score": 0.95},
        ]
        with patch("memkit.client.httpx.Client") as mock_cls:
            mock_http = mock_cls.return_value.__enter__.return_value
            mock_http.get.return_value = _make_response(fake_results)

            client = MemKitClient()
            results = client.search("query", k=3)

        assert results == fake_results
        mock_http.get.assert_called_once_with(
            "http://localhost:8000/memories/search",
            params={"q": "query", "k": 3},
        )


class TestMemKitClientList:
    def test_list_returns_list(self):
        fake_memories = [
            {"id": "1", "text": "memory one"},
            {"id": "2", "text": "memory two"},
        ]
        with patch("memkit.client.httpx.Client") as mock_cls:
            mock_http = mock_cls.return_value.__enter__.return_value
            mock_http.get.return_value = _make_response(fake_memories)

            client = MemKitClient()
            result = client.list()

        assert result == fake_memories
        mock_http.get.assert_called_once_with("http://localhost:8000/memories")


class TestMemKitClientDelete:
    def test_delete_calls_delete_endpoint(self):
        with patch("memkit.client.httpx.Client") as mock_cls:
            mock_http = mock_cls.return_value.__enter__.return_value
            mock_http.delete.return_value = _make_response(None, 204)

            client = MemKitClient()
            client.delete("mem-123")

        mock_http.delete.assert_called_once_with(
            "http://localhost:8000/memories/mem-123"
        )
