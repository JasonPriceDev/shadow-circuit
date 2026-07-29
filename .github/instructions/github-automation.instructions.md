---
applyTo: ".github/workflows/**/*.yml,.github/ISSUE_TEMPLATE/**/*.yml"
---

# GitHub Automation

- Use explicit least-privilege permissions, timeouts, concurrency, and safe
  manual defaults.
- `SDLC_AGENT_ENABLED` is the kill switch; manual runs default to dry-run.
- Skip secret-dependent PR jobs from forks.
- GitHub cron is UTC. Do not assume token-authored events retrigger workflows.
- Human-facing templates use `status:proposed`, never `agent:generated`.
- Concept submission authorizes draft discovery artifacts, not implementation.
- Approval labels are proposal-specific and single-use.
- Add a required status check only after a workflow emits that exact check.

Parse YAML and run `actionlint` when available. Workflow, permission, taxonomy,
and dependency changes require explicit authorization.
