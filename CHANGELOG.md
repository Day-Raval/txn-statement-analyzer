# Changelog

## 1.0.0 (2026-10-12)
- First public release.
- `scripts/analyze.py` (Python 3.9+, standard library only) computes monthly and total income, spend, refunds and net; spend by category with shares; recurring charges; unusual charges (median + 3 × MAD); possible duplicates; refunds. Every finding cites its CSV rows.
- Column flags for real bank exports: `--date`, `--description`, `--amount`, `--debit`/`--credit`, `--flip-sign`.
- Date ranges with `--start`/`--end`. Unusual charges and subscriptions are still judged against the whole file.
- SKILL.md: the model explains the JSON and never calculates; careful wording ("possible duplicate", never "fraud"); a pre-reply checklist; a fixed disclaimer line.
- Works in Claude Code, Claude.ai, Codex, Gemini CLI, Cursor and GitHub Copilot via `install.sh`, plus an `AGENTS.md` fallback.
- Tests: planted answers in a synthetic statement, messy input, column flags and date ranges. Trigger and behavior tests in `evals/trigger-tests.md`.
