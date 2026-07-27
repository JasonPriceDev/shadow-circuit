"""Entry point for the Shadow Circuit SDLC harness agent."""

from __future__ import annotations

import asyncio
import os

from agent_framework import create_harness_agent, todos_remaining
from agent_framework.openai import OpenAIChatCompletionClient
from dotenv import load_dotenv

from .instructions import SDLC_AGENT_INSTRUCTIONS
from .tools import (
    add_taxonomy_labels,
    comment_on_issue,
    consume_current_approval,
    create_branch,
    create_issue,
    create_or_update_draft_pr,
    get_check_runs,
    get_issue,
    get_pull_request,
    get_review_comments,
    read_repo_file,
    record_plan_approval,
    replace_status_label,
    run_build,
    run_npm_ci,
    run_typecheck,
    search_issues,
    update_issue,
    upsert_repo_file,
)


def _env(name: str, default: str = "") -> str:
    return os.environ.get(name, default).strip()


def _build_prompt() -> str:
    trigger = _env("TRIGGER_EVENT", "workflow_dispatch")
    action = _env("GITHUB_EVENT_ACTION")
    issue = _env("ISSUE_NUMBER")
    pr = _env("PR_NUMBER")
    label = _env("GITHUB_EVENT_LABEL_NAME")

    context = (
        f"Trigger={trigger}; action={action or 'none'}; "
        f"issue={issue or 'none'}; pr={pr or 'none'}; label={label or 'none'}."
    )

    if trigger == "workflow_dispatch":
        return f"{context}\n\n{_env('MANUAL_PROMPT', 'Audit repository state and report.')}"
    if trigger == "schedule":
        return (
            f"{context}\n\nProduce one read-only backlog report: stale work, "
            "duplicates, StageCatalog coverage, Spec-to-Task gaps, blocked work, "
            "and milestone health. Do not create or modify resources."
        )
    if trigger == "pull_request":
        return (
            f"{context}\n\nReview PR #{pr}: read its diff, checks, and review "
            "comments; verify one-Task scope, parent Spec, conventions, known "
            "hazards, acceptance evidence, and manual playtest gaps. Update the "
            "existing idempotent review comment."
        )
    if trigger == "issue_comment":
        return (
            f"{context}\n\nA human commented on managed issue #{issue}. Read the "
            "issue and comments, determine whether a question or proposal was "
            "answered, and respond without expanding scope."
        )
    if trigger == "issues" and action == "labeled":
        return (
            f"{context}\n\nProcess label `{label}` on issue #{issue}. If it is "
            "an approval label, locate the exact proposal marker, perform only "
            "the authorized operation, and consume the approval after success."
        )
    if trigger == "issues":
        return (
            f"{context}\n\nRead issue #{issue}. For opened/edited issues, review "
            "type, parent links, duplicates, taxonomy, acceptance criteria, and "
            "ambiguity. Post questions or an idempotent proposal; do not treat "
            "the issue itself as approval."
        )
    return f"{context}\n\nInspect the relevant state and report safely."


async def _main() -> None:
    if _env("SDLC_AGENT_ENABLED", "false").lower() != "true":
        raise RuntimeError("SDLC agent is disabled by SDLC_AGENT_ENABLED.")

    dry_run = _env("DRY_RUN", "false").lower() == "true"
    model = _env("DEEPSEEK_MODEL", "deepseek-v4-pro")
    if dry_run:
        print("[DRY RUN] Mutation tools will return previews only.")

    client = OpenAIChatCompletionClient(
        model=model,
        base_url="https://api.deepseek.com",
        api_key=os.environ["DEEPSEEK_API_KEY"],
    )
    tools = [
        read_repo_file,
        search_issues,
        get_issue,
        get_pull_request,
        get_check_runs,
        get_review_comments,
        comment_on_issue,
        add_taxonomy_labels,
        replace_status_label,
        record_plan_approval,
        create_issue,
        update_issue,
        create_branch,
        upsert_repo_file,
        create_or_update_draft_pr,
        run_npm_ci,
        run_typecheck,
        run_build,
    ]
    agent = create_harness_agent(
        client=client,
        name="sdlc-agent",
        agent_instructions=SDLC_AGENT_INSTRUCTIONS,
        tools=tools,
        max_context_window_tokens=128_000,
        max_output_tokens=16_384,
        loop_should_continue=todos_remaining(),
        loop_max_iterations=10,
        disable_file_memory=True,
        disable_file_access=True,
        disable_web_search=True,
    )

    prompt = _build_prompt()
    print(f"Trigger: {_env('TRIGGER_EVENT', 'workflow_dispatch')}")
    print(f"Model: {model}")
    session = agent.create_session()
    response = await agent.run(prompt, session=session)
    print(f"\nAgent response:\n{response.text}")

    if not dry_run and _env("GITHUB_EVENT_LABEL_NAME").startswith("approve:"):
        result = await consume_current_approval()
        print(f"\nApproval: {result}")


def main() -> None:
    if not os.environ.get("GITHUB_ACTIONS"):
        load_dotenv()
    asyncio.run(_main())


if __name__ == "__main__":
    main()
