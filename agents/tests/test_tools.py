"""Unit tests for SDLC agent tools.

These tests mock the GitHub API and filesystem. Run with:

    python -m pytest agents/tests/
"""

from __future__ import annotations

import os
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# ---------------------------------------------------------------------------
# config tests
# ---------------------------------------------------------------------------


class TestRepoConfig:
    def test_default_owner(self) -> None:
        from agents.sdlc_agent.config import config

        assert config.owner == "JasonPriceDev"
        assert config.repo == "shadow-circuit"

    def test_all_labels_includes_agent_label(self) -> None:
        from agents.sdlc_agent.config import config

        labels = config.all_labels()
        assert config.agent_label in labels
        assert "type:bug" in labels
        assert "severity:critical" in labels


# ---------------------------------------------------------------------------
# read_repo_file tests
# ---------------------------------------------------------------------------


class TestReadRepoFile:
    def test_reads_existing_file(self, tmp_path: Path) -> None:
        from agents.sdlc_agent.tools import read_repo_file

        f = tmp_path / "test.txt"
        f.write_text("hello")

        with patch("pathlib.Path.cwd", return_value=tmp_path):
            with patch("pathlib.Path.resolve", side_effect=lambda self: self):
                result = asyncio_run(read_repo_file(str(f)))

        assert "hello" in result

    def test_file_not_found(self) -> None:
        from agents.sdlc_agent.tools import read_repo_file

        result = asyncio_run(read_repo_file("nonexistent.txt"))
        assert "not found" in result.lower()


# ---------------------------------------------------------------------------
# build tools tests
# ---------------------------------------------------------------------------


class TestRunTypecheck:
    def test_success(self) -> None:
        from agents.sdlc_agent.tools import run_typecheck

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0, stdout="", stderr=""
            )
            result = asyncio_run(run_typecheck())
            assert "exit=0" in result


class TestRunBuild:
    def test_failure(self) -> None:
        from agents.sdlc_agent.tools import run_build

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=1, stdout="", stderr="Build failed"
            )
            result = asyncio_run(run_build())
            assert "exit=1" in result
            assert "Build failed" in result


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------


def asyncio_run(coro):
    import asyncio

    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro)
    # Already in an event loop — create a new one (testing only).
    import concurrent.futures

    with concurrent.futures.ThreadPoolExecutor() as pool:
        return pool.submit(asyncio.run, coro).result()
