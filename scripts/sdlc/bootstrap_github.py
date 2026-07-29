#!/usr/bin/env python3
"""Preview or create the repository's canonical labels and milestones."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import sys

from github import Auth, Github
from github.GithubException import GithubException

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "agents"))

from sdlc_agent.config import config  # noqa: E402

LABEL_STYLE = {
    "type:": ("1d76db", "Work item type"),
    "area:": ("5319e7", "Primary product or engineering area"),
    "discipline:": ("0e8a16", "Primary delivery discipline"),
    "severity:": ("d93f0b", "Defect severity"),
    "status:": ("fbca04", "Workflow state"),
    "approve:": ("b60205", "Single-use human authorization"),
    "agent:": ("6f42c1", "Created by SDLC automation"),
}


def _style(name: str) -> tuple[str, str]:
    for prefix, style in LABEL_STYLE.items():
        if name.startswith(prefix):
            return style
    raise ValueError(f"No label style for {name}.")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    parser.add_argument(
        "--repository", default=os.environ.get("GITHUB_REPOSITORY", config.full_name)
    )
    args = parser.parse_args()

    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GITHUB_PAT")
    if not token:
        print("Error: GITHUB_TOKEN or GITHUB_PAT is required.", file=sys.stderr)
        return 2
    if args.apply and os.environ.get("SDLC_BOOTSTRAP_APPROVED", "").lower() != "true":
        print("Error: --apply requires SDLC_BOOTSTRAP_APPROVED=true.", file=sys.stderr)
        return 2

    try:
        repo = Github(auth=Auth.Token(token), timeout=20).get_repo(args.repository)
        labels = {label.name: label for label in repo.get_labels()}
        drift = False
        for name in config.all_labels:
            color, description = _style(name)
            current = labels.get(name)
            changed = (
                current is None
                or current.color.lower() != color
                or (current.description or "") != description
            )
            if not changed:
                print(f"label {name}: present")
                continue
            drift = True
            if not args.apply:
                print(f"label {name}: would create/update")
            elif current:
                current.edit(name=name, color=color, description=description)
                print(f"label {name}: updated")
            else:
                repo.create_label(name=name, color=color, description=description)
                print(f"label {name}: created")

        milestones = {
            milestone.title: milestone for milestone in repo.get_milestones(state="all")
        }
        for title in config.milestones:
            if title in milestones:
                print(f"milestone {title}: present")
                continue
            drift = True
            if args.apply:
                repo.create_milestone(title)
                print(f"milestone {title}: created")
            else:
                print(f"milestone {title}: would create")
        return 1 if drift and not args.apply else 0
    except (GithubException, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
