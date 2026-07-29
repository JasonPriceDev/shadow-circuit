---
name: sync-sdlc
description: Validate the Concept-to-Spec-to-Task-to-PR graph, detect upstream drift, assess downstream impact, and safely synchronize managed GitHub issue metadata. Use after changing concepts, decisions, Specs, plans, Tasks, issue links, statuses, or traceability metadata.
---

# Synchronize SDLC Artifacts

1. Treat Markdown Specs as canonical requirements, the manifest as canonical
   relationships, GitHub comments as discussion, labels as workflow state, and
   PRs/CI as evidence.
2. Run `python scripts/sdlc/traceability.py validate`.
3. Detect upstream changes with
   `python scripts/sdlc/traceability.py impact --format markdown`.
4. For every affected descendant, read the changed upstream content and
   classify it as `unaffected`, `needs-clarification`, `needs-revision`,
   `obsolete`, or `new-work`.
5. Explain evidence and proposed changes. Do not rewrite approved artifacts,
   close issues, or change acceptance criteria without human approval.
6. Preview issue synchronization with `python scripts/sdlc/sync_issues.py`.
7. Use `--apply` only after the required approval. The script may update only
   the marker-delimited managed block and mapped workflow labels.
8. After approved artifact changes, run
   `python scripts/sdlc/traceability.py snapshot`.
9. Re-run validation and report changed files, affected descendants, GitHub
   mutations, and remaining human decisions.

The scripts under `scripts/sdlc/` are authoritative for graph and issue
mechanics; do not reproduce their behavior with ad hoc parsing.
