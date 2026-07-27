---
applyTo: "agents/**/*.py,agents/requirements*.txt"
---

# Python SDLC Agent

- Use Python 3.12 and pinned dependencies.
- Use `OpenAIChatCompletionClient` with `https://api.deepseek.com`; do not use
  the Responses-oriented `OpenAIChatClient` without a compatibility test.
- Re-test tool calls, reasoning parameters, looping, compaction, and telemetry
  after model or framework upgrades.

GitHub is durable state; harness memory is scratch. In Actions, approval is a
single-use label tied to an exact proposal ID, not an interactive prompt.

Tools must:

- Use narrow typed schemas and independently validate model arguments.
- Enforce authorization and `DRY_RUN` in code.
- Reject traversal, symlink escape, and non-allowlisted paths.
- Use fixed command allowlists, expected-SHA checks, deterministic markers, and
  idempotent mutations.
- Redact secrets and fail closed when identity, approval, target, or revision
  cannot be verified.
- Bound timeouts, retries, model/tool iterations, mutations, and cost.

Never rely on `GITHUB_TOKEN` mutations to trigger the next phase. Never push to
`main`, merge, force-push, delete branches, or self-modify workflow/approval
policy. Apply `agent:generated` only to agent-created resources.

Test dry-run, invalid/consumed approvals, duplicate events, path restrictions,
SHA conflicts, recursion filtering, partial failures, and secret redaction.
Mock network calls in unit tests; keep real-provider tests opt-in.