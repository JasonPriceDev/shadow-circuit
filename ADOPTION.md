# Adopt the SDLC Package

1. Copy this directory tree into the repository root. Preserve the existing
   `docs/plans/concept.md` and product source.
2. Rebuild the development container.
3. In VS Code, run `DeepSeek: Set API Key`; select DeepSeek V4 Pro.
4. Run:

   ```bash
   python scripts/sdlc/traceability.py validate
   python -m unittest discover -s tests -p "test_*.py"
   npm ci
   npm run typecheck
   npm run build
   ```

5. Run the **SDLC Bootstrap** workflow first with `apply: false`, then with
   `apply: true`.
6. Add the Actions secret `DEEPSEEK_API_KEY`.
7. Add Actions variables:
   - `DEEPSEEK_MODEL=deepseek-v4-pro`
   - `SDLC_AGENT_ENABLED=true`
8. Run **SDLC Agent** manually with `dry_run: true`.
9. Open a Concept issue or select the **Discovery** custom agent in VS Code.

`docs/sdlc/manifest.json` starts empty so adoption cannot overwrite existing
traceability. The first discovery run should register the Concept and generated
artifacts, then run:

```bash
python scripts/sdlc/traceability.py snapshot
```

In branch protection, require the existing `CI / check` context. Add
`SDLC Traceability / traceability` only after it has successfully run and you
want traceability to block relevant PRs. Do not require the conditional SDLC
Agent workflow.
