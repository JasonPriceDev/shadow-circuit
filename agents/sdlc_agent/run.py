"""Entry point for the Shadow Circuit SDLC harness agent.

Invoked by .github/workflows/sdlc-agent.yml. Reads environment variables to
determine the trigger event and constructs a prompt, then runs the harness agent
with instructions from instructions.py and tools from tools.py.
"""

from __future__ import annotations

import asyncio
import os
import sys

from agent_framework import create_harness_agent, todos_remaining
from agent_framework.openai import OpenAIChatClient
from agent_framework.file_memory import FileMemoryStore

from .instructions import SDL_AGENT_INSTRUCTIONS
from .tools import (
    add_labels,
    comment_on_issue,
    create_branch,
    create_issue,
    create_pull_request,
    get_issue,
    read_repo_file,
    run_build,
    run_typecheck,
    search_issues,
    update_issue,
)


def _build_prompt() -> str:
    """Determine what the agent should do based on the trigger event."""
    trigger = os.environ.get("TRIGGER_EVENT", "manual")

    if trigger == "workflow_dispatch":
        return os.environ.get("PROMPT", "Review the repository state and report.")

    if trigger == "schedule":
        return (
            "Nightly backlog curation: check for stale issues (no activity in "
            "14+ days), un-tracked stages compared to src/levels/StageCatalog.ts, "
            "duplicate detection by title similarity, and spec-to-issue coverage "
            "gaps. Post findings as a single comment on the backlog-health issue "
            "(create it if it does not exist)."
        )

    if trigger == "pull_request" or trigger == "pull_request_target":
        pr_number = os.environ.get("PR_NUMBER", "")
        return (
            f"PR #{pr_number} was opened or updated. Review the diff, check CI "
            "status, and comment a structured Definition-of-Done checklist: "
            "1) CI status, 2) references to parent spec and task issue, "
            "3) repo conventions, 4) anti-patterns from the known-defects list, "
            "5) scope containment, 6) test/acceptance gaps."
        )

    if trigger == "issues":
        action = os.environ.get("GITHUB_EVENT_ACTION", "opened")
        issue_number = os.environ.get("ISSUE_NUMBER", "")

        if action == "labeled":
            label = os.environ.get("GITHUB_EVENT_LABEL_NAME", "")
            if label == "ready-for-planning":
                return (
                    f"Issue #{issue_number} was labeled ready-for-planning. "
                    "Read the issue, its linked spec and design docs, create a "
                    "todo list, and post a task breakdown as a comment."
                )
            if label == "ready-for-scaffold":
                return (
                    f"Issue #{issue_number} was labeled ready-for-scaffold. "
                    "Create a branch from main named agent/<issue-number>-<slug>, "
                    "then open one draft PR with file stubs and TODOs matching "
                    "repo conventions. Reference the task issue and parent spec."
                )
            return (
                f"Issue #{issue_number} received label '{label}'. "
                "Assess whether this label requires agent action and respond "
                "appropriately."
            )

        if action == "edited":
            return (
                f"Issue #{issue_number} was edited. Re-read it and re-triage "
                "if the body changed substantially. Do not act on minor edits."
            )

        # Default: issue opened
        return (
            f"Issue #{issue_number} was opened. Read the issue and determine "
            "its type from the labels or body. "
            "If type:spec — review the spec, check consistency, ask questions, "
            "and generate a task breakdown. "
            "If type:bug — assign severity, attempt root-cause analysis, propose "
            "a fix plan, and ask for confirmation. "
            "If type:feature — read linked spec, assign area/discipline labels, "
            "and assign a milestone. "
            "If untyped — assign type, area, and discipline labels. Check for "
            "duplicates. Ask the human if unclassifiable."
        )

    # Fallback for unknown triggers
    return (
        f"Triggered by {trigger}. Review the repository state and report any "
        "issues that need attention."
    )


async def _main() -> None:
    dry_run = os.environ.get("DRY_RUN", "false").lower() == "true"

    if dry_run:
        print("[DRY RUN] No GitHub writes will be performed.")
        print(f"[DRY RUN] Prompt:\n{_build_prompt()}")
        return

    agent = create_harness_agent(
        client=OpenAIChatClient(
            model=os.environ.get("DEEPSEEK_MODEL", "deepseek-v4-pro"),
            base_url="https://api.deepseek.com",
            api_key=os.environ["DEEPSEEK_API_KEY"],
        ),
        name="sdlc-agent",
        agent_instructions=SDL_AGENT_INSTRUCTIONS,
        tools=[
            add_labels,
            comment_on_issue,
            create_branch,
            create_issue,
            create_pull_request,
            get_issue,
            read_repo_file,
            run_build,
            run_typecheck,
            search_issues,
            update_issue,
        ],
        memory_store=FileMemoryStore("./.github/agent-memory"),
        max_context_window_tokens=128_000,
        max_output_tokens=16_384,
        loop_should_continue=todos_remaining(),
        loop_max_iterations=15,
    )

    prompt = _build_prompt()
    print(f"Trigger: {os.environ.get('TRIGGER_EVENT', 'manual')}")
    print(f"Model: {os.environ.get('DEEPSEEK_MODEL', 'deepseek-v4-pro')}")

    session = agent.create_session()
    response = await agent.run(prompt, session=session)
    print(f"\nAgent response:\n{response.text}")


def main() -> None:
    asyncio.run(_main())


if __name__ == "__main__":
    main()
