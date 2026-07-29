#!/usr/bin/env python3
"""Validate and compare the repository's SDLC artifact graph."""

from __future__ import annotations

import argparse
from collections import defaultdict, deque
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MANIFEST = ROOT / "docs/sdlc/manifest.json"
DEFAULT_STATE = ROOT / "docs/sdlc/state.json"
ID_RE = re.compile(r"^[A-Z][A-Z0-9-]{2,63}$")
KINDS = {
    "concept",
    "decision",
    "spec",
    "prototype",
    "epic",
    "feature",
    "task",
}
STATUSES = {
    "draft",
    "proposed",
    "needs-review",
    "approved",
    "in-progress",
    "done",
    "blocked",
    "obsolete",
}


class ManifestError(ValueError):
    """Raised when traceability metadata is invalid."""


def _read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ManifestError(f"Missing file: {path.relative_to(ROOT)}") from exc
    except json.JSONDecodeError as exc:
        raise ManifestError(f"Invalid JSON in {path.relative_to(ROOT)}: {exc}") from exc
    if not isinstance(value, dict):
        raise ManifestError(f"{path.relative_to(ROOT)} must contain an object.")
    return value


def _relative_path(value: str) -> Path:
    candidate = PurePosixPath(value)
    if candidate.is_absolute() or ".." in candidate.parts or not candidate.parts:
        raise ManifestError(f"Invalid repository-relative path: {value!r}")
    resolved = (ROOT / candidate.as_posix()).resolve()
    try:
        resolved.relative_to(ROOT)
    except ValueError as exc:
        raise ManifestError(f"Path escapes repository: {value!r}") from exc
    return resolved


def _digest(path: Path) -> str:
    return f"sha256:{hashlib.sha256(path.read_bytes()).hexdigest()}"


def load_manifest(path: Path = DEFAULT_MANIFEST) -> dict[str, dict[str, Any]]:
    raw = _read_json(path)
    if raw.get("schema_version") != 1:
        raise ManifestError("manifest schema_version must be 1.")
    items = raw.get("artifacts")
    if not isinstance(items, list):
        raise ManifestError("manifest artifacts must be an array.")

    artifacts: dict[str, dict[str, Any]] = {}
    paths: set[str] = set()
    issues: set[int] = set()
    for index, item in enumerate(items):
        where = f"artifacts[{index}]"
        if not isinstance(item, dict):
            raise ManifestError(f"{where} must be an object.")

        artifact_id = item.get("id")
        if not isinstance(artifact_id, str) or not ID_RE.fullmatch(artifact_id):
            raise ManifestError(f"{where}.id must match {ID_RE.pattern}.")
        if artifact_id in artifacts:
            raise ManifestError(f"Duplicate artifact id: {artifact_id}")

        kind = item.get("kind")
        if kind not in KINDS:
            raise ManifestError(f"{artifact_id}: invalid kind {kind!r}.")
        status = item.get("status")
        if status not in STATUSES:
            raise ManifestError(f"{artifact_id}: invalid status {status!r}.")

        upstream = item.get("upstream", [])
        if not isinstance(upstream, list) or not all(
            isinstance(value, str) for value in upstream
        ):
            raise ManifestError(f"{artifact_id}: upstream must be a string array.")
        if len(upstream) != len(set(upstream)):
            raise ManifestError(f"{artifact_id}: duplicate upstream ids.")

        artifact_path = item.get("path")
        if artifact_path is not None:
            if not isinstance(artifact_path, str):
                raise ManifestError(f"{artifact_id}: path must be a string or null.")
            resolved = _relative_path(artifact_path)
            if artifact_path in paths:
                raise ManifestError(f"Duplicate artifact path: {artifact_path}")
            if not resolved.is_file():
                raise ManifestError(f"{artifact_id}: missing artifact file {artifact_path}.")
            paths.add(artifact_path)

        issue = item.get("github_issue")
        if issue is not None:
            if not isinstance(issue, int) or isinstance(issue, bool) or issue <= 0:
                raise ManifestError(f"{artifact_id}: github_issue must be positive or null.")
            if issue in issues:
                raise ManifestError(f"Duplicate github_issue: {issue}")
            issues.add(issue)

        artifacts[artifact_id] = dict(item)

    for artifact_id, item in artifacts.items():
        for parent in item.get("upstream", []):
            if parent not in artifacts:
                raise ManifestError(f"{artifact_id}: unknown upstream id {parent}.")
            if parent == artifact_id:
                raise ManifestError(f"{artifact_id}: cannot depend on itself.")

    _assert_acyclic(artifacts)
    return artifacts


def _assert_acyclic(artifacts: dict[str, dict[str, Any]]) -> None:
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(artifact_id: str, trail: list[str]) -> None:
        if artifact_id in visiting:
            cycle = " → ".join([*trail, artifact_id])
            raise ManifestError(f"Traceability cycle: {cycle}")
        if artifact_id in visited:
            return
        visiting.add(artifact_id)
        for parent in artifacts[artifact_id].get("upstream", []):
            visit(parent, [*trail, artifact_id])
        visiting.remove(artifact_id)
        visited.add(artifact_id)

    for artifact_id in artifacts:
        visit(artifact_id, [])


def build_state(artifacts: dict[str, dict[str, Any]]) -> dict[str, Any]:
    state: dict[str, Any] = {"schema_version": 1, "artifacts": {}}
    for artifact_id in sorted(artifacts):
        item = artifacts[artifact_id]
        path = item.get("path")
        state["artifacts"][artifact_id] = {
            "path": path,
            "sha256": _digest(_relative_path(path)) if path else None,
            "status": item["status"],
            "upstream": sorted(item.get("upstream", [])),
            "github_issue": item.get("github_issue"),
        }
    return state


def _load_state(path: Path) -> dict[str, Any]:
    state = _read_json(path)
    if state.get("schema_version") != 1 or not isinstance(
        state.get("artifacts"), dict
    ):
        raise ManifestError("state must use schema_version 1 and an artifacts object.")
    return state


def impact(
    artifacts: dict[str, dict[str, Any]], baseline: dict[str, Any]
) -> tuple[list[str], list[str]]:
    current = build_state(artifacts)["artifacts"]
    previous = baseline["artifacts"]
    changed = sorted(
        artifact_id
        for artifact_id in set(current) | set(previous)
        if current.get(artifact_id) != previous.get(artifact_id)
    )

    children: dict[str, set[str]] = defaultdict(set)
    for artifact_id, item in artifacts.items():
        for parent in item.get("upstream", []):
            children[parent].add(artifact_id)

    affected: set[str] = set()
    queue: deque[str] = deque(changed)
    while queue:
        parent = queue.popleft()
        for child in sorted(children.get(parent, ())):
            if child not in affected and child not in changed:
                affected.add(child)
                queue.append(child)
    return changed, sorted(affected)


def _render_markdown(changed: list[str], affected: list[str]) -> str:
    lines = ["## SDLC impact assessment", ""]
    if not changed:
        return "\n".join([*lines, "No artifact drift detected."])
    lines.extend(["### Changed artifacts", ""])
    lines.extend(f"- `{artifact_id}`" for artifact_id in changed)
    lines.extend(["", "### Downstream artifacts requiring assessment", ""])
    if affected:
        lines.extend(f"- [ ] `{artifact_id}`" for artifact_id in affected)
    else:
        lines.append("None.")
    lines.extend(
        [
            "",
            "A changed relationship, status, issue link, or file hash counts as drift.",
            "Classify descendants before updating the committed snapshot.",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--manifest", type=Path, default=DEFAULT_MANIFEST, help=argparse.SUPPRESS
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("validate")

    snapshot_parser = subparsers.add_parser("snapshot")
    snapshot_parser.add_argument("--output", type=Path, default=DEFAULT_STATE)
    snapshot_parser.add_argument("--check", action="store_true")

    impact_parser = subparsers.add_parser("impact")
    impact_parser.add_argument("--baseline", type=Path, default=DEFAULT_STATE)
    impact_parser.add_argument("--format", choices=("json", "markdown"), default="json")
    args = parser.parse_args()

    try:
        artifacts = load_manifest(args.manifest)
        if args.command == "validate":
            print(f"Traceability valid: {len(artifacts)} artifacts.")
            return 0

        current = build_state(artifacts)
        if args.command == "snapshot":
            rendered = json.dumps(current, indent=2, sort_keys=True) + "\n"
            if args.check:
                existing = args.output.read_text(encoding="utf-8")
                if existing != rendered:
                    print("Traceability snapshot is stale.", file=sys.stderr)
                    return 1
                print("Traceability snapshot is current.")
                return 0
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(rendered, encoding="utf-8")
            print(f"Wrote {args.output.relative_to(ROOT)}.")
            return 0

        changed, affected = impact(artifacts, _load_state(args.baseline))
        if args.format == "markdown":
            print(_render_markdown(changed, affected))
        else:
            print(json.dumps({"changed": changed, "affected": affected}, indent=2))
        return 0
    except (ManifestError, OSError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
