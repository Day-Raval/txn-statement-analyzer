# Agent instructions

This repository contains one agent skill: `skills/txn-statement-analyzer/`.

If your agent does not load SKILL.md skills automatically and the user asks to analyze a bank or card statement CSV (spending summary, categories, subscriptions, duplicate or unusual charges):
1. Read `skills/txn-statement-analyzer/SKILL.md` and follow its procedure exactly.
2. Resolve its `scripts/`, `references/` and `examples/` paths relative to `skills/txn-statement-analyzer/`.
3. Never compute numbers yourself: every number comes from the JSON that `scripts/analyze.py` prints.

For any other request, ignore this file.
