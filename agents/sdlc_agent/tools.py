"""Validated repository, GitHub, discovery, and build tools."""

from __future__ import annotations

import asyncio
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
from typing import Callable, TypeVar

from github import Auth, Github
from github.GithubException import UnknownObjectException
from github.Repository import Repository

from .config import config

T = TypeVar("T")
_gh: Github | None = None
_repo: Repository | None = None
_MAX_OUTPUT = 12_000
_PROPOSAL_RE = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9._-]{0,63}$")
_TASK_BRANCH_RE = re.compile(r"^agent/task-(\d+)-[a-z0-9][a-z0-9-]{0,49}$")
_DISCOVERY_BRANCH_RE = re.compile(
    r"^agent/discovery-(\d+)-[a-z0-9][a-z0-9-]{0,49}$"
)
_protected_operations: set[str] = set()
_discovery_file_mutations = 0


def _truthy(name: str) -> bool:
    return os.environ.get(name, "").lower() == "true"


def _dry_run(message: str) -> str | None:
    return f"[DRY RUN] {message}" if _truthy("DRY_RUN") else None


async def _thread(call: Callable[[], T]) -> T:
    return await asyncio.to_thread(call)


def _get_client() -> Github:
    global _gh
    if _gh is None:
        token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GITHUB_PAT")
        if not token:
            raise RuntimeError("GITHUB_TOKEN or GITHUB_PAT is required.")
        _gh = Github(auth=Auth.Token(token), timeout=20)
    return _gh


def _get_repo() -> Repository:
    global _repo
    if _repo is None:
        _repo = _get_client().get_repo(config.full_name)
    return _repo


def _split_labels(labels: str) -> list[str]:
    return list(dict.fromkeys(part.strip() for part in labels.split(",") if part.strip()))


def _validate_proposal_id(proposal_id: str) -> None:
    if not _PROPOSAL_RE.fullmatch(proposal_id):
        raise ValueError("Invalid proposal_id.")


def _proposal_marker(proposal_id: str) -> str:
    _validate_proposal_id(proposal_id)
    return f"<!-- sdlc-agent:proposal:{proposal_id} -->"


def _operation_marker(operation: str, subject: str, proposal_id: str) -> str:
    return f"<!-- sdlc-agent:{operation}:{subject}:{proposal_id} -->"


def _current_issue_number() -> int:
    value = os.environ.get("ISSUE_NUMBER", "")
    if not value.isdigit():
        raise PermissionError("This operation requires an issue event.")
    return int(value)


def _current_pr_number() -> int:
    value = os.environ.get("PR_NUMBER", "")
    if not value.isdigit():
        raise PermissionError("This operation requires a pull-request event.")
    return int(value)


def _assert_approver() -> None:
    if os.environ.get("GITHUB_ACTOR", "") not in config.approvers:
        raise PermissionError("The triggering actor is not an approved approver.")


def _assert_event_target(number: int) -> None:
    """Prevent unprotected tools from mutating an unrelated issue or PR."""
    if _truthy("DRY_RUN"):
        return
    targets = {
        int(value)
        for value in (
            os.environ.get("ISSUE_NUMBER", ""),
            os.environ.get("PR_NUMBER", ""),
        )
        if value.isdigit()
    }
    if number not in targets:
        raise PermissionError("Mutation target does not match the triggering event.")


def _assert_approval(required: str, proposal_id: str) -> int:
    _validate_proposal_id(proposal_id)
    if _truthy("DRY_RUN"):
        value = os.environ.get("ISSUE_NUMBER", "")
        return int(value) if value.isdigit() else -1
    if os.environ.get("TRIGGER_EVENT") != "issues":
        raise PermissionError("Protected mutation requires an issues event.")
    if os.environ.get("GITHUB_EVENT_ACTION") != "labeled":
        raise PermissionError("Protected mutation requires a labeled event.")
    if os.environ.get("GITHUB_EVENT_LABEL_NAME") != required:
        raise PermissionError(f"Required approval label: {required}.")
    _assert_approver()

    number = _current_issue_number()
    issue = _get_repo().get_issue(number)
    if required not in {label.name for label in issue.labels}:
        raise PermissionError("Approval label is no longer present.")
    marker = _proposal_marker(proposal_id)
    if not any(marker in (comment.body or "") for comment in issue.get_comments()):
        raise PermissionError("Matching proposal marker was not found.")
    return number


def _is_revision_command() -> bool:
    body = os.environ.get("GITHUB_EVENT_COMMENT_BODY", "").lstrip()
    first_line = body.splitlines()[0] if body else ""
    return first_line == "/revise" or first_line.startswith("/revise ")


def _assert_discovery_authority(concept_issue: int, branch: str = "") -> None:
    if _truthy("DRY_RUN"):
        return
    _assert_approver()
    concept = _get_repo().get_issue(concept_issue)
    if "type:concept" not in {label.name for label in concept.labels}:
        raise PermissionError("Discovery target must have the type:concept label.")

    trigger = os.environ.get("TRIGGER_EVENT", "")
    action = os.environ.get("GITHUB_EVENT_ACTION", "")
    if trigger == "issues" and action in {"opened", "edited"}:
        if _current_issue_number() != concept_issue:
            raise PermissionError("Concept event does not match the discovery target.")
        return

    if trigger == "issue_comment" and action in {"created", "edited"}:
        if not _is_revision_command():
            raise PermissionError("Draft revision requires an approver /revise comment.")
        current = _current_issue_number()
        if current == concept_issue:
            return
        try:
            pr = _get_repo().get_pull(current)
        except UnknownObjectException as exc:
            raise PermissionError("Revision comment is not on the Concept or its PR.") from exc
        match = _DISCOVERY_BRANCH_RE.fullmatch(pr.head.ref)
        if not match or int(match.group(1)) != concept_issue:
            raise PermissionError("PR is not the Concept's discovery branch.")
        return

    if trigger in {"pull_request_review", "pull_request_review_comment"}:
        if action not in {"created", "edited", "submitted"} or not _is_revision_command():
            raise PermissionError("Draft revision requires an approver /revise review.")
        pr = _get_repo().get_pull(_current_pr_number())
        match = _DISCOVERY_BRANCH_RE.fullmatch(pr.head.ref)
        if not match or int(match.group(1)) != concept_issue:
            raise PermissionError("Review is not on the Concept's discovery branch.")
        return

    raise PermissionError("Event does not authorize discovery-file changes.")


def _mark_protected_mutation(operation: str) -> None:
    _protected_operations.add(operation)


def _safe_relative_path(
    path: str,
    *,
    allow_restricted: bool = False,
    allowed_prefixes: tuple[str, ...] | None = None,
) -> PurePosixPath:
    if "\\" in path:
        raise ValueError("Path must use forward slashes.")
    candidate = PurePosixPath(path)
    if candidate.is_absolute() or ".." in candidate.parts or not candidate.parts:
        raise ValueError("Path must be repository-relative without traversal.")
    normalized = candidate.as_posix()
    if allowed_prefixes and not any(
        normalized.startswith(prefix) for prefix in allowed_prefixes
    ):
        raise PermissionError(f"Path is outside the allowed discovery roots: {normalized}")
    if not allow_restricted and any(
        normalized == prefix.rstrip("/") or normalized.startswith(prefix)
        for prefix in config.restricted_paths
    ):
        raise PermissionError(f"Restricted path: {normalized}")
    return candidate


def _truncate(value: str) -> str:
    if len(value) <= _MAX_OUTPUT:
        return value
    return f"{value[:_MAX_OUTPUT]}\n...[truncated]"


def _find_milestone(title: str):
    for milestone in _get_repo().get_milestones(state="open"):
        if milestone.title == title:
            return milestone
    raise ValueError(f"Unknown open milestone: {title}")


def _validate_discovery_branch(name: str, concept_issue: int) -> None:
    match = _DISCOVERY_BRANCH_RE.fullmatch(name)
    if not match or int(match.group(1)) != concept_issue:
        raise ValueError(
            f"Branch must match agent/discovery-{concept_issue}-<slug>."
        )


def _validate_task_branch(name: str, task_issue: int) -> None:
    match = _TASK_BRANCH_RE.fullmatch(name)
    if not match or (task_issue > 0 and int(match.group(1)) != task_issue):
        raise ValueError(f"Branch must match agent/task-{task_issue}-<slug>.")


async def get_repo_context() -> str:
    """Return repository identity and the current default-branch SHA."""

    def read() -> str:
        repo = _get_repo()
        sha = repo.get_branch(config.default_branch).commit.sha
        return "\n".join(
            [
                f"Repository: {config.full_name}",
                f"Default branch: {config.default_branch}",
                f"Default SHA: {sha}",
                f"Event SHA: {os.environ.get('GITHUB_SHA', 'unknown')}",
            ]
        )

    return await _thread(read)


async def list_repo_files(root: str = ".", limit: int = 500) -> str:
    """List repository files below a safe relative root."""
    if limit < 1 or limit > 1_000:
        return "Error: limit must be between 1 and 1000."
    try:
        relative = PurePosixPath() if root == "." else _safe_relative_path(
            root, allow_restricted=True
        )
    except (ValueError, PermissionError) as exc:
        return f"Error: {exc}"
    base = (Path.cwd() / relative.as_posix()).resolve()
    repo_root = Path.cwd().resolve()
    try:
        base.relative_to(repo_root)
    except ValueError:
        return "Error: root escapes the repository."
    if not base.exists():
        return f"Error: root not found: {root}"

    ignored = {".git", ".venv", "node_modules", "dist", "__pycache__"}
    files: list[str] = []
    for path in base.rglob("*"):
        if not path.is_file() or ignored.intersection(path.relative_to(repo_root).parts):
            continue
        try:
            path.resolve().relative_to(repo_root)
        except ValueError:
            continue
        files.append(path.relative_to(repo_root).as_posix())
    files.sort()
    suffix = "\n...[truncated]" if len(files) > limit else ""
    return "\n".join(files[:limit]) + suffix


async def search_repo_text(
    query: str, root: str = ".", limit: int = 50
) -> str:
    """Search UTF-8 repository files for a literal string."""
    if not query or len(query) > 200:
        return "Error: query must contain 1-200 characters."
    if limit < 1 or limit > 200:
        return "Error: limit must be between 1 and 200."
    try:
        relative = PurePosixPath() if root == "." else _safe_relative_path(
            root, allow_restricted=True
        )
    except (ValueError, PermissionError) as exc:
        return f"Error: {exc}"
    repo_root = Path.cwd().resolve()
    base = (repo_root / relative.as_posix()).resolve()
    if not base.exists():
        return f"Error: root not found: {root}"

    ignored = {".git", ".venv", "node_modules", "dist", "__pycache__"}
    matches: list[str] = []
    needle = query.casefold()
    for path in base.rglob("*"):
        if not path.is_file() or ignored.intersection(path.relative_to(repo_root).parts):
            continue
        try:
            path.resolve().relative_to(repo_root)
        except ValueError:
            continue
        try:
            for line_number, line in enumerate(
                path.read_text(encoding="utf-8").splitlines(), start=1
            ):
                if needle in line.casefold():
                    matches.append(
                        f"{path.relative_to(repo_root).as_posix()}:{line_number}: "
                        f"{line[:300]}"
                    )
                    if len(matches) == limit:
                        return "\n".join(matches) + "\n...[truncated]"
        except (UnicodeDecodeError, OSError):
            continue
    return "\n".join(matches) if matches else "No matches."


async def read_repo_file(path: str, ref: str = "") -> str:
    """Read a UTF-8 file locally or from a GitHub ref and include its SHA."""
    try:
        relative = _safe_relative_path(path, allow_restricted=True)
    except (ValueError, PermissionError) as exc:
        return f"Error reading {path}: {exc}"

    if ref:
        def read_remote() -> str:
            value = _get_repo().get_contents(relative.as_posix(), ref=ref)
            if isinstance(value, list):
                raise IsADirectoryError(path)
            text = value.decoded_content.decode("utf-8")
            return _truncate(f"SHA: {value.sha}\n{text}")

        try:
            return await _thread(read_remote)
        except (UnknownObjectException, UnicodeDecodeError, IsADirectoryError) as exc:
            return f"Error reading {path} at {ref}: {exc}"

    root = Path.cwd().resolve()
    resolved = (root / relative.as_posix()).resolve()
    try:
        resolved.relative_to(root)
    except ValueError:
        return f"Error: path escapes the repository: {path}"
    try:
        return _truncate(await _thread(lambda: resolved.read_text(encoding="utf-8")))
    except (FileNotFoundError, IsADirectoryError, UnicodeDecodeError) as exc:
        return f"Error reading {path}: {exc}"


async def search_issues(query: str = "", labels: str = "", state: str = "open") -> str:
    """Search issues by literal text and exact labels; return at most 30."""
    if state not in {"open", "closed", "all"}:
        return "Error: state must be open, closed, or all."
    requested = _split_labels(labels)

    def search() -> list[str]:
        results: list[str] = []
        needle = query.casefold()
        for issue in _get_repo().get_issues(state=state, labels=requested):
            haystack = f"{issue.title}\n{issue.body or ''}".casefold()
            if needle and needle not in haystack:
                continue
            results.append(f"#{issue.number} [{issue.state}] {issue.title}")
            if len(results) == 30:
                break
        return results

    lines = await _thread(search)
    return "\n".join(lines) if lines else "No issues matched."


async def get_issue(number: int) -> str:
    """Read an issue, labels, milestone, body, and up to 50 comments."""

    def read() -> str:
        issue = _get_repo().get_issue(number)
        comments: list[str] = []
        for index, comment in enumerate(issue.get_comments()):
            if index == 50:
                break
            comments.append(f"- {comment.user.login}: {comment.body or '(empty)'}")
        return "\n".join(
            [
                f"#{issue.number}: {issue.title}",
                f"State: {issue.state}",
                f"Labels: {', '.join(label.name for label in issue.labels)}",
                f"Milestone: {issue.milestone.title if issue.milestone else 'none'}",
                f"Body:\n{issue.body or '(empty)'}",
                "Comments:\n" + ("\n".join(comments) if comments else "(none)"),
            ]
        )

    try:
        return _truncate(await _thread(read))
    except UnknownObjectException:
        return f"Error: issue #{number} not found."


async def get_pull_request(number: int) -> str:
    """Read PR metadata and changed-file patches."""

    def read() -> str:
        pr = _get_repo().get_pull(number)
        files = [
            f"## {file.filename} ({file.status}, +{file.additions}/-{file.deletions})\n"
            f"{file.patch or '(patch unavailable)'}"
            for file in pr.get_files()
        ]
        return "\n".join(
            [
                f"PR #{pr.number}: {pr.title}",
                f"State: {pr.state}; draft={pr.draft}; base={pr.base.ref}; "
                f"head={pr.head.ref}; head_sha={pr.head.sha}",
                f"Body:\n{pr.body or '(empty)'}",
                "Files:\n" + ("\n".join(files) if files else "(none)"),
            ]
        )

    try:
        return _truncate(await _thread(read))
    except UnknownObjectException:
        return f"Error: PR #{number} not found."


async def get_check_runs(ref: str) -> str:
    """Read check runs for a branch, tag, or commit SHA."""

    def read() -> list[str]:
        commit = _get_repo().get_commit(ref)
        return [
            f"{check.name}: status={check.status}, conclusion={check.conclusion}, "
            f"url={check.html_url}"
            for check in commit.get_check_runs()
        ]

    try:
        lines = await _thread(read)
        return "\n".join(lines) if lines else "No check runs found."
    except UnknownObjectException:
        return f"Error: ref not found: {ref}"


async def get_review_comments(number: int) -> str:
    """Read inline review comments for a pull request."""

    def read() -> list[str]:
        pr = _get_repo().get_pull(number)
        return [
            f"{comment.user.login} on {comment.path}: {comment.body}"
            for comment in pr.get_review_comments()
        ]

    try:
        lines = await _thread(read)
        return _truncate("\n".join(lines)) if lines else "No review comments."
    except UnknownObjectException:
        return f"Error: PR #{number} not found."


async def comment_on_issue(number: int, body: str, marker: str) -> str:
    """Create or update an idempotent signed issue or PR comment."""
    _assert_event_target(number)
    safe_marker = re.sub(r"[^a-zA-Z0-9._:-]", "-", marker)[:96]
    if not safe_marker:
        return "Error: marker is required."
    token = f"<!-- sdlc-agent:{safe_marker} -->"
    preview = _dry_run(f"Would comment on #{number} with marker {safe_marker}.")
    if preview:
        return preview

    def write() -> str:
        issue = _get_repo().get_issue(number)
        rendered = f"{token}\n{body}\n\n---\n🤖 *sdlc-agent*"
        for comment in issue.get_comments():
            if token in (comment.body or ""):
                comment.edit(rendered)
                return f"Updated comment: {comment.html_url}"
        comment = issue.create_comment(rendered)
        return f"Created comment: {comment.html_url}"

    return await _thread(write)


async def add_taxonomy_labels(number: int, labels: str) -> str:
    """Add validated type, area, discipline, or severity labels."""
    _assert_event_target(number)
    requested = _split_labels(labels)
    if not requested:
        return "Error: at least one taxonomy label is required."
    invalid = sorted(set(requested) - set(config.taxonomy_labels))
    if invalid:
        return f"Error: non-taxonomy labels rejected: {', '.join(invalid)}"
    preview = _dry_run(f"Would add labels to #{number}: {', '.join(requested)}")
    if preview:
        return preview
    await _thread(lambda: _get_repo().get_issue(number).add_to_labels(*requested))
    return f"Added labels to #{number}: {', '.join(requested)}"


async def replace_status_label(number: int, status: str) -> str:
    """Replace the issue's primary status label except final completion."""
    _assert_event_target(number)
    if status not in config.status_labels:
        return f"Error: invalid status label: {status}"
    if status == "status:done":
        return "Error: status:done requires the approved completion flow."
    preview = _dry_run(f"Would set #{number} status to {status}.")
    if preview:
        return preview

    def write() -> None:
        issue = _get_repo().get_issue(number)
        for label in list(issue.labels):
            if label.name in config.status_labels:
                issue.remove_from_labels(label)
        issue.add_to_labels(status)

    await _thread(write)
    return f"Set #{number} status to {status}."


async def create_discovery_branch(
    name: str, concept_issue: int, base_sha: str
) -> str:
    """Create or reuse an authorized Concept discovery branch."""
    _assert_discovery_authority(concept_issue)
    _validate_discovery_branch(name, concept_issue)
    preview = _dry_run(f"Would create discovery branch {name} at {base_sha}.")
    if preview:
        return preview

    def write() -> str:
        default_sha = _get_repo().get_branch(config.default_branch).commit.sha
        if base_sha != default_sha:
            raise ValueError("base_sha no longer matches the default branch.")
        try:
            existing = _get_repo().get_branch(name)
            return f"Reused branch {name} at {existing.commit.sha[:8]}."
        except UnknownObjectException:
            _get_repo().create_git_ref(ref=f"refs/heads/{name}", sha=base_sha)
            return f"Created branch {name} at {base_sha[:8]}."

    return await _thread(write)


async def upsert_discovery_file(
    path: str,
    content: str,
    branch: str,
    message: str,
    concept_issue: int,
    expected_sha: str = "",
) -> str:
    """Create or update one authorized discovery-package text file."""
    global _discovery_file_mutations
    _assert_discovery_authority(concept_issue, branch)
    _validate_discovery_branch(branch, concept_issue)
    relative = _safe_relative_path(
        path,
        allow_restricted=True,
        allowed_prefixes=config.discovery_paths,
    )
    if _discovery_file_mutations >= config.max_discovery_files_per_run:
        return "Error: discovery file mutation limit reached for this run."
    preview = _dry_run(f"Would upsert discovery file {relative} on {branch}.")
    if preview:
        return preview

    result = await _thread(
        lambda: _upsert_remote_file(
            relative, content, branch, message, expected_sha
        )
    )
    _discovery_file_mutations += 1
    return result


async def create_or_update_discovery_pr(
    head: str,
    title: str,
    body: str,
    concept_issue: int,
) -> str:
    """Create or update the Concept's authorized draft discovery PR."""
    _assert_discovery_authority(concept_issue, head)
    _validate_discovery_branch(head, concept_issue)
    marker = f"<!-- sdlc-agent:discovery-pr:{concept_issue} -->"
    preview = _dry_run(f"Would create or update discovery PR from {head}.")
    if preview:
        return preview

    def write() -> str:
        pulls = _get_repo().get_pulls(
            state="open",
            head=f"{config.full_name.split('/', 1)[0]}:{head}",
            base=config.default_branch,
        )
        existing = next(iter(pulls), None)
        rendered = (
            f"{marker}\nConcept: #{concept_issue}\n\n{body}\n\n"
            "---\n🤖 *Draft discovery package; not production authorization.*"
        )
        if existing:
            existing.edit(title=title, body=rendered)
            return f"Updated discovery PR #{existing.number}: {existing.html_url}"
        pr = _get_repo().create_pull(
            title=title,
            body=rendered,
            base=config.default_branch,
            head=head,
            draft=True,
        )
        _get_repo().get_issue(pr.number).add_to_labels(config.agent_label)
        return f"Created discovery PR #{pr.number}: {pr.html_url}"

    return await _thread(write)


async def approve_spec_package(proposal_id: str) -> str:
    """Record approval of an exact discovery/specification package."""
    number = _assert_approval("approve:spec", proposal_id)
    marker = _operation_marker("spec-approved", str(number), proposal_id)
    preview = _dry_run(f"Would record Spec package {proposal_id} on #{number}.")
    if preview:
        return preview

    result = await _thread(
        lambda: _record_approval_comment(
            number, marker, f"Spec package `{proposal_id}` approved"
        )
    )
    _mark_protected_mutation("approve-spec")
    return result


async def record_plan_approval(proposal_id: str) -> str:
    """Record approval of an exact marked delivery plan."""
    number = _assert_approval("approve:plan", proposal_id)
    marker = _operation_marker("plan-approved", str(number), proposal_id)
    preview = _dry_run(f"Would record plan {proposal_id} on #{number}.")
    if preview:
        return preview

    result = await _thread(
        lambda: _record_approval_comment(
            number, marker, f"Plan `{proposal_id}` approved"
        )
    )
    _mark_protected_mutation("approve-plan")
    return result


def _record_approval_comment(number: int, marker: str, text: str) -> str:
    issue = _get_repo().get_issue(number)
    for comment in issue.get_comments():
        if marker in (comment.body or ""):
            return f"Reused approval record: {comment.html_url}"
    actor = os.environ.get("GITHUB_ACTOR", "unknown")
    comment = issue.create_comment(f"{marker}\n{text} by @{actor}.")
    return f"Recorded approval: {comment.html_url}"


async def create_issue(
    title: str,
    body: str,
    labels: str,
    proposal_id: str,
    item_id: str,
    milestone: str = "",
) -> str:
    """Create one approved, idempotent agent issue."""
    _assert_approval("approve:create-issues", proposal_id)
    _validate_proposal_id(item_id)
    requested = _split_labels(labels)
    allowed = set(config.taxonomy_labels + config.status_labels)
    invalid = sorted(set(requested) - allowed)
    if invalid:
        return f"Error: invalid labels: {', '.join(invalid)}"
    if len(set(requested) & set(config.status_labels)) > 1:
        return "Error: at most one status label may be supplied."
    if not set(requested) & set(config.status_labels):
        requested.append("status:proposed")
    marker = _operation_marker("create-issue", item_id, proposal_id)
    preview = _dry_run(f"Would create issue '{title}' for {proposal_id}.")
    if preview:
        return preview

    def write() -> str:
        for issue in _get_repo().get_issues(state="all"):
            if marker in (issue.body or ""):
                return f"Reused issue #{issue.number}: {issue.html_url}"
        milestone_obj = _find_milestone(milestone) if milestone else None
        issue = _get_repo().create_issue(
            title=title,
            body=f"{marker}\n{body}",
            labels=list(dict.fromkeys([*requested, config.agent_label])),
            milestone=milestone_obj,
        )
        return f"Created issue #{issue.number}: {issue.html_url}"

    result = await _thread(write)
    _mark_protected_mutation("create-issue")
    return result


async def update_issue(
    number: int,
    proposal_id: str,
    body: str = "",
    milestone: str = "",
    state: str = "",
) -> str:
    """Apply an approved issue revision or closure."""
    required = "approve:close" if state == "closed" else "approve:revise"
    approved_number = _assert_approval(required, proposal_id)
    if approved_number > 0 and number != approved_number:
        return "Error: approval may update only its triggering issue."
    if state not in {"", "open", "closed"}:
        return "Error: state must be open, closed, or empty."
    preview = _dry_run(f"Would update issue #{number} under {required}.")
    if preview:
        return preview

    def write() -> None:
        kwargs = {}
        if body:
            kwargs["body"] = body
        if milestone:
            kwargs["milestone"] = _find_milestone(milestone)
        if state:
            kwargs["state"] = state
        if kwargs:
            _get_repo().get_issue(number).edit(**kwargs)

    await _thread(write)
    _mark_protected_mutation("update-issue")
    return f"Updated issue #{number}."


async def create_branch(name: str, proposal_id: str, base_sha: str) -> str:
    """Create or reuse an approved deterministic Task branch."""
    task = _assert_approval("approve:implement", proposal_id)
    _validate_task_branch(name, task)
    preview = _dry_run(f"Would create Task branch {name} at {base_sha}.")
    if preview:
        return preview

    def write() -> str:
        default_sha = _get_repo().get_branch(config.default_branch).commit.sha
        if base_sha != default_sha:
            raise ValueError("base_sha no longer matches the default branch.")
        try:
            existing = _get_repo().get_branch(name)
            return f"Reused branch {name} at {existing.commit.sha[:8]}."
        except UnknownObjectException:
            _get_repo().create_git_ref(ref=f"refs/heads/{name}", sha=base_sha)
            return f"Created branch {name} at {base_sha[:8]}."

    result = await _thread(write)
    _mark_protected_mutation("create-branch")
    return result


def _upsert_remote_file(
    relative: PurePosixPath,
    content: str,
    branch: str,
    message: str,
    expected_sha: str,
) -> str:
    try:
        current = _get_repo().get_contents(relative.as_posix(), ref=branch)
        if isinstance(current, list):
            raise ValueError("Path is a directory.")
        if not expected_sha or current.sha != expected_sha:
            raise ValueError("expected_sha is required and must match the file.")
        result = _get_repo().update_file(
            relative.as_posix(),
            message,
            content,
            current.sha,
            branch=branch,
        )
        return f"Updated {relative} at {result['commit'].sha[:8]}."
    except UnknownObjectException:
        if expected_sha:
            raise ValueError("expected_sha supplied for a new file.")
        result = _get_repo().create_file(
            relative.as_posix(),
            message,
            content,
            branch=branch,
        )
        return f"Created {relative} at {result['commit'].sha[:8]}."


async def upsert_repo_file(
    path: str,
    content: str,
    branch: str,
    message: str,
    proposal_id: str,
    expected_sha: str = "",
) -> str:
    """Create or replace one approved UTF-8 file on a Task branch."""
    label = os.environ.get("GITHUB_EVENT_LABEL_NAME")
    required = "approve:revise" if label == "approve:revise" else "approve:implement"
    task = _assert_approval(required, proposal_id)
    _validate_task_branch(branch, task)
    relative = _safe_relative_path(path)
    preview = _dry_run(f"Would upsert {relative} on {branch}.")
    if preview:
        return preview

    result = await _thread(
        lambda: _upsert_remote_file(
            relative, content, branch, message, expected_sha
        )
    )
    _mark_protected_mutation("upsert-file")
    return result


async def create_or_update_draft_pr(
    head: str,
    title: str,
    body: str,
    proposal_id: str,
) -> str:
    """Create or update the approved Task's draft pull request."""
    label = os.environ.get("GITHUB_EVENT_LABEL_NAME")
    required = "approve:revise" if label == "approve:revise" else "approve:implement"
    task = _assert_approval(required, proposal_id)
    _validate_task_branch(head, task)
    marker = _operation_marker("draft-pr", str(task), proposal_id)
    preview = _dry_run(f"Would create or update draft PR from {head}.")
    if preview:
        return preview

    def write() -> str:
        pulls = _get_repo().get_pulls(
            state="open",
            head=f"{config.full_name.split('/', 1)[0]}:{head}",
            base=config.default_branch,
        )
        existing = next(iter(pulls), None)
        rendered = f"{marker}\n{body}\n\n---\n🤖 *sdlc-agent*"
        if existing:
            existing.edit(title=title, body=rendered)
            return f"Updated PR #{existing.number}: {existing.html_url}"
        pr = _get_repo().create_pull(
            title=title,
            body=rendered,
            base=config.default_branch,
            head=head,
            draft=True,
        )
        _get_repo().get_issue(pr.number).add_to_labels(config.agent_label)
        return f"Created draft PR #{pr.number}: {pr.html_url}"

    result = await _thread(write)
    _mark_protected_mutation("draft-pr")
    return result


async def consume_current_approval() -> str:
    """Remove the current approval label after its protected operation succeeds."""
    label = os.environ.get("GITHUB_EVENT_LABEL_NAME", "")
    if label not in config.approval_labels:
        return "No approval label to consume."
    if os.environ.get("GITHUB_ACTOR", "") not in config.approvers:
        return f"Did not consume {label}: actor is not an approver."
    required_operations = {
        "approve:spec": {"approve-spec"},
        "approve:plan": {"approve-plan"},
        "approve:create-issues": {"create-issue"},
        "approve:implement": {"draft-pr"},
        "approve:revise": {"update-issue", "upsert-file", "draft-pr"},
        "approve:close": {"update-issue"},
    }
    if not (_protected_operations & required_operations.get(label, set())):
        return f"Did not consume {label}: protected operation did not succeed."
    number = _current_issue_number()
    preview = _dry_run(f"Would consume {label} on #{number}.")
    if preview:
        return preview

    def write() -> str:
        issue = _get_repo().get_issue(number)
        issue.remove_from_labels(label)
        actor = os.environ.get("GITHUB_ACTOR", "unknown")
        run_id = os.environ.get("GITHUB_RUN_ID", "local")
        comment = issue.create_comment(
            f"<!-- sdlc-agent:approval-consumed:{label}:{run_id} -->\n"
            f"Consumed `{label}` from @{actor} after the authorized operation."
        )
        return f"Consumed {label}: {comment.html_url}"

    return await _thread(write)


async def run_npm_ci() -> str:
    """Run npm ci."""
    return await _run_command(["npm", "ci"], timeout=300)


async def run_typecheck() -> str:
    """Run npm run typecheck."""
    return await _run_command(["npm", "run", "typecheck"], timeout=180)


async def run_build() -> str:
    """Run npm run build."""
    return await _run_command(["npm", "run", "build"], timeout=180)


async def run_traceability_validate() -> str:
    """Validate the local SDLC artifact graph."""
    return await _run_command(
        ["python", "scripts/sdlc/traceability.py", "validate"], timeout=60
    )


async def run_traceability_impact() -> str:
    """Report changed upstream artifacts and affected descendants."""
    return await _run_command(
        [
            "python",
            "scripts/sdlc/traceability.py",
            "impact",
            "--format",
            "markdown",
        ],
        timeout=60,
    )


async def _run_command(command: list[str], timeout: int) -> str:
    def run() -> str:
        try:
            result = subprocess.run(
                command,
                cwd=Path.cwd(),
                capture_output=True,
                text=True,
                timeout=timeout,
                check=False,
            )
        except (FileNotFoundError, subprocess.TimeoutExpired) as exc:
            return f"Error running {' '.join(command)}: {exc}"
        return _truncate(
            f"exit={result.returncode}\n"
            f"stdout:\n{result.stdout.strip() or '(empty)'}\n"
            f"stderr:\n{result.stderr.strip() or '(empty)'}"
        )

    return await _thread(run)
