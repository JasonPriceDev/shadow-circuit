"""GitHub API and build command tools for the SDLC harness agent.

Each tool is an async callable registered with the harness via
create_harness_agent(..., tools=[...]).
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

from github import Github, GithubIntegration
from github.Issue import Issue
from github.Repository import Repository

from .config import config

# ---------------------------------------------------------------------------
# GitHub client helpers
# ---------------------------------------------------------------------------

_gh: Github | None = None
_repo: Repository | None = None


def _get_client() -> Github:
    global _gh
    if _gh is None:
        token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GITHUB_PAT")
        if not token:
            raise RuntimeError("GITHUB_TOKEN not set")
        _gh = Github(token)
    return _gh


def _get_repo() -> Repository:
    global _repo
    if _repo is None:
        _repo = _get_client().get_repo(f"{config.owner}/{config.repo}")
    return _repo


# ---------------------------------------------------------------------------
# Read-only tools (auto-approved)
# ---------------------------------------------------------------------------


async def read_repo_file(path: str) -> str:
    """Read a file from the workspace.

    Args:
        path: Relative path from the repo root (e.g. "src/config/GameConfig.ts").
    """
    resolved = Path(path).resolve()
    if not str(resolved).startswith(str(Path.cwd().resolve())):
        return f"Error: path '{path}' is outside the workspace."
    try:
        return resolved.read_text(encoding="utf-8")
    except FileNotFoundError:
        return f"Error: file not found: {path}"
    except IsADirectoryError:
        return f"Error: '{path}' is a directory, not a file."


async def search_issues(
    query: str = "",
    labels: str = "",
    state: str = "open",
) -> str:
    """Search GitHub Issues in this repository.

    Args:
        query: Free-text search query.
        labels: Comma-separated label filter (e.g. "type:bug,severity:critical").
        state: "open", "closed", or "all".
    """
    label_list = [lbl.strip() for lbl in labels.split(",") if lbl.strip()] if labels else []
    issues = _get_repo().get_issues(state=state, labels=label_list)
    if not issues.totalCount:
        return "No issues matched the search criteria."
    lines: list[str] = []
    for issue in issues[:20]:
        lines.append(f"#{issue.number} [{issue.state}] {issue.title}")
    return "\n".join(lines) if lines else "No issues found."


async def get_issue(number: int) -> str:
    """Get full details of a GitHub Issue including its body.

    Args:
        number: The issue number.
    """
    try:
        issue = _get_repo().get_issue(number)
    except Exception:
        return f"Error: issue #{number} not found."
    lines = [
        f"#{issue.number}: {issue.title}",
        f"State: {issue.state}",
        f"Labels: {', '.join(lbl.name for lbl in issue.labels)}",
        f"Milestone: {issue.milestone.title if issue.milestone else 'none'}",
        f"Body:\n{issue.body or '(empty)'}",
    ]
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Write tools (require approval)
# ---------------------------------------------------------------------------


async def create_issue(
    title: str,
    body: str,
    labels: str = "",
    milestone: str = "",
) -> str:
    """Create a new GitHub Issue.

    Args:
        title: Issue title (will be prefixed with agent:generated label notice).
        body: Markdown body.
        labels: Comma-separated label names.
        milestone: Milestone title (must match an existing milestone exactly).
    """
    label_list = [lbl.strip() for lbl in labels.split(",") if lbl.strip()]
    label_list.append(config.agent_label)
    kwargs = {"title": title, "body": body, "labels": label_list}
    if milestone:
        kwargs["milestone"] = _get_repo().get_milestone(milestone)
    issue = _get_repo().create_issue(**kwargs)
    return f"Created issue #{issue.number}: {issue.html_url}"


async def update_issue(
    number: int,
    body: str = "",
    state: str = "",
    milestone: str = "",
) -> str:
    """Update an existing issue's body, state, or milestone.

    Args:
        number: The issue number.
        body: New body text (empty to leave unchanged).
        state: "open" or "closed" (empty to leave unchanged).
        milestone: Milestone title (empty to leave unchanged).
    """
    issue = _get_repo().get_issue(number)
    kwargs = {}
    if body:
        kwargs["body"] = body
    if state:
        kwargs["state"] = state
    if milestone:
        kwargs["milestone"] = _get_repo().get_milestone(milestone)
    if kwargs:
        issue.edit(**kwargs)
    return f"Updated issue #{number}."


async def comment_on_issue(number: int, body: str) -> str:
    """Add a comment to an issue. The agent signature is appended automatically.

    Args:
        number: The issue number.
        body: The comment text (markdown).
    """
    issue = _get_repo().get_issue(number)
    comment = issue.create_comment(f"{body}\n\n---\n🤖 *sdlc-agent*")
    return f"Comment added to #{number}: {comment.html_url}"


async def add_labels(number: int, labels: str) -> str:
    """Add labels to an issue.

    Args:
        number: The issue number.
        labels: Comma-separated label names.
    """
    label_list = [lbl.strip() for lbl in labels.split(",") if lbl.strip()]
    issue = _get_repo().get_issue(number)
    issue.add_to_labels(*label_list)
    return f"Labels added to #{number}: {', '.join(label_list)}"


async def create_branch(name: str) -> str:
    """Create a new branch from the default branch (main).

    This uses the GitHub API to create a branch ref. Requires a token with
    contents:write scope.

    Args:
        name: Branch name (e.g. "agent/12-contact-damage-fix").
    """
    repo = _get_repo()
    default = repo.get_branch(config.default_branch)
    sha = default.commit.sha
    ref_name = f"refs/heads/{name}"
    try:
        repo.create_git_ref(ref=ref_name, sha=sha)
    except Exception as exc:
        if "already exists" in str(exc).lower() or "Reference already exists" in str(exc):
            return f"Branch '{name}' already exists."
        raise
    return f"Created branch '{name}' from {config.default_branch} ({sha[:8]})."


async def create_pull_request(
    base: str,
    head: str,
    title: str,
    body: str,
    draft: bool = True,
) -> str:
    """Open a pull request. Always opens as a draft by default.

    Args:
        base: Target branch (usually "main").
        head: Source branch name.
        title: PR title.
        body: PR description (markdown).
        draft: Whether to open as a draft PR.
    """
    body_with_label = f"{body}\n\n---\n🤖 *sdlc-agent* — `{config.agent_label}`"
    pr = _get_repo().create_pull(
        title=title,
        body=body_with_label,
        base=base,
        head=head,
        draft=draft,
    )
    return f"Created {'draft ' if draft else ''}PR #{pr.number}: {pr.html_url}"


# ---------------------------------------------------------------------------
# Build tools (auto-approved)
# ---------------------------------------------------------------------------


async def run_typecheck() -> str:
    """Run `npm run typecheck` and return the output."""
    return _run_npm("typecheck")


async def run_build() -> str:
    """Run `npm run build` and return the output."""
    return _run_npm("build")


def _run_npm(script: str) -> str:
    try:
        result = subprocess.run(
            ["npm", "run", script],
            capture_output=True,
            text=True,
            timeout=120,
        )
        out = result.stdout.strip() or "(no output)"
        err = result.stderr.strip()
        exit_info = f"exit={result.returncode}"
        if err:
            return f"{exit_info}\nstdout:\n{out}\nstderr:\n{err}"
        return f"{exit_info}\n{out}"
    except subprocess.TimeoutExpired:
        return f"npm run {script} timed out after 120s"
    except FileNotFoundError:
        return "Error: npm not found. Is Node.js installed?"
