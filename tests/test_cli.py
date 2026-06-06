"""Unit tests for the Typer CLI using CliRunner with mocked MemKitClient."""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from memkit.cli import app

runner = CliRunner()


class TestAddCommand:
    def test_add_text(self):
        with patch("memkit.cli.MemKitClient") as mock_cls:
            mock_client = mock_cls.return_value
            mock_client.add.return_value = "mem-abc"

            result = runner.invoke(app, ["add", "hello world"])

        assert result.exit_code == 0
        mock_client.add.assert_called_once_with("hello world")
        assert "mem-abc" in result.output

    def test_add_file(self, tmp_path):
        mem_file = tmp_path / "mem.md"
        mem_file.write_text("# Memory\nThis is a test memory.")

        with patch("memkit.cli.MemKitClient") as mock_cls:
            mock_client = mock_cls.return_value
            mock_client.add.return_value = "mem-xyz"

            result = runner.invoke(app, ["add", str(mem_file)])

        assert result.exit_code == 0
        mock_client.add.assert_called_once_with("# Memory\nThis is a test memory.")

    def test_add_uses_base_url(self):
        with patch("memkit.cli.MemKitClient") as mock_cls:
            mock_client = mock_cls.return_value
            mock_client.add.return_value = "id-1"

            runner.invoke(app, ["add", "text", "--base-url", "http://myserver:9000"])

        mock_cls.assert_called_once_with("http://myserver:9000")


class TestSearchCommand:
    def test_search_output(self):
        fake_results = [{"id": "1", "text": "relevant result", "score": 0.88}]

        with patch("memkit.cli.MemKitClient") as mock_cls:
            mock_client = mock_cls.return_value
            mock_client.search.return_value = fake_results

            result = runner.invoke(app, ["search", "my query"])

        assert result.exit_code == 0
        assert "relevant result" in result.output
        assert "0.88" in result.output

    def test_search_no_results(self):
        with patch("memkit.cli.MemKitClient") as mock_cls:
            mock_client = mock_cls.return_value
            mock_client.search.return_value = []

            result = runner.invoke(app, ["search", "nothing"])

        assert result.exit_code == 0
        assert "No results" in result.output

    def test_search_passes_k(self):
        with patch("memkit.cli.MemKitClient") as mock_cls:
            mock_client = mock_cls.return_value
            mock_client.search.return_value = []

            runner.invoke(app, ["search", "query", "--k", "10"])

        mock_client.search.assert_called_once_with("query", k=10)


class TestListCommand:
    def test_list_output(self):
        fake_memories = [
            {"id": "abc", "text": "first memory stored here"},
            {"id": "def", "text": "second memory stored here"},
        ]

        with patch("memkit.cli.MemKitClient") as mock_cls:
            mock_client = mock_cls.return_value
            mock_client.list.return_value = fake_memories

            result = runner.invoke(app, ["list"])

        assert result.exit_code == 0
        assert "abc" in result.output
        assert "first memory" in result.output

    def test_list_empty(self):
        with patch("memkit.cli.MemKitClient") as mock_cls:
            mock_client = mock_cls.return_value
            mock_client.list.return_value = []

            result = runner.invoke(app, ["list"])

        assert result.exit_code == 0
        assert "No memories" in result.output
