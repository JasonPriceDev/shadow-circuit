---
applyTo: ".github/workflows/**/*.yml,.github/ISSUE_TEMPLATE/**/*.yml"
---

# GitHub Automation

Workflow, permission, and taxonomy changes require explicit authorization.

Workflows must use valid two-space YAML, explicit least-privilege permissions,
timeouts, concurrency, safe manual defaults, and lockfile-aware caching. Use
`python -m pip` and `npm ci`. Do not expose secrets.

SDLC workflow rules:

- `SDLC_AGENT_ENABLED` is the pre-run kill switch.
- Manual dispatch defaults to dry-run.
- Skip secret-dependent PR jobs from forks.
- Filter unmanaged and agent-authored comments.
- GitHub cron is UTC; document Edmonton time.
- Do not assume `GITHUB_TOKEN` writes trigger another workflow.

Issue forms:

- Human forms start with `status:proposed`, never `agent:generated`.
- Normal hierarchy: Spec → Task → PR.
- Expanded hierarchy: Spec → Epic → Feature → Task → PR.
- Use stable paths/symbols, not line numbers.
- Form submission is not approval.

Approval labels are proposal-specific and single-use:
`approve:plan`, `approve:create-issues`, `approve:implement`,
`approve:revise`, `approve:close`.

Parse changed YAML and run `actionlint` when available. Verify permissions,
referenced commands/variables, fork behavior, event-field expressions,
duplicate events, disabled-agent behavior, and dry-run defaults.