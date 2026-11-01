---
name: review-python-before-main
description: Reviews Python code against project style before any push to main. Use when the user asks to push to main, git push origin main, merge to main, or review Python before pushing.
---

# Review Python before pushing to main

Do this **before** any `git push` to `main` (or `master`). Do not push until the review is clean or the user explicitly overrides.

## Workflow

1. Identify the merge base: `origin/main` if it exists, else `main`.
2. Collect the Python diff (committed on this branch, staged, and unstaged):

```bash
git fetch origin main 2>/dev/null || true
BASE=$(git rev-parse --verify origin/main 2>/dev/null || git rev-parse --verify main)
git diff "$BASE"...HEAD -- '*.py'
git diff HEAD -- '*.py'
```

3. Also list untracked `*.py` files (`git status --short`) and read them in full.
4. Review only Python. Ignore config/docs unless they affect Python runtime.
5. Report findings. If any **blocker** exists, stop and do not push.
6. If the review is clean (or only non-blockers and the user still wants to push), then push — and only if they asked to push.

If there is no Python diff, say so in one sentence and proceed with the push only if they asked.

## Checklist

Apply [`.cursor/rules/python-only.mdc`](../../rules/python-only.mdc) and [`.cursor/rules/python-style.mdc`](../../rules/python-style.mdc):

- [ ] Python only — no other languages or their package ecosystems
- [ ] PEP 8: 4-space indent, `snake_case` / `PascalCase`
- [ ] Public functions have type hints (`list[str]`, not `List[str]`)
- [ ] f-strings unless a format is reused
- [ ] No bare `except:` or empty `except Exception`
- [ ] Specific exceptions; no swallowed errors
- [ ] Functions small and named for what they do
- [ ] Lookahead correctness: empty inputs, missing columns, timezone/date alignment for market data
- [ ] No secrets, credentials, or live trading / order-placement code

## Report format

```markdown
## Python review vs main

**Verdict:** Blockers | Ready to push

| Severity | Location | Finding |
| --- | --- | --- |
| Blocker / Suggestion / Nit | file.py:line | ... |

**Push:** skipped | proceeding
```

- **Blocker**: must fix before push to main
- **Suggestion**: should fix; do not block unless the user wants a clean review
- **Nit**: optional

Do not force-push to `main`. Do not skip hooks.
