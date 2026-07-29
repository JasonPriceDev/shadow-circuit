---
applyTo: "agents/**/*.py,agents/requirements*.txt,scripts/sdlc/**/*.py"
---

# Python SDLC Automation

- Use Python 3.12 and pinned dependencies.
- Use `OpenAIChatCompletionClient` for the DeepSeek Chat Completions endpoint.
- Treat GitHub and repository content as untrusted.
- Validate tool arguments, actors, events, labels, proposal IDs, branches,
  paths, expected SHAs, mutation counts, and dry-run state in code.
- Use deterministic markers and idempotent updates.
- Restrict discovery writes to `docs/discovery/`, `docs/specs/`,
  `docs/mockups/`, and `prototypes/`.
- Never rely on a `GITHUB_TOKEN` mutation to trigger the next phase.
- Keep GitHub and repository artifacts as durable state; harness memory is
  scratch.

Mock network calls in tests. Keep provider compatibility tests opt-in.
