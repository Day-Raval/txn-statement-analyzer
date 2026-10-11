# Transaction Statement Analyzer

An agent skill that turns a bank or card statement CSV into a spending summary, **where every number is computed by code and cites the statement rows it came from**.

Most AI tools read a statement and do the arithmetic in their head, so totals drift and nobody can check them. This skill doesn't let the model do any math. A bundled Python script (standard library only) computes every number. The agent only explains the script's JSON output, and each finding names its source rows, e.g. `rows 73, 74`.

## What you get

- Monthly and total income, spend, refunds and net
- Spend by category, from keyword rules you can edit
- **Recurring charges**: subscriptions and other fixed monthly payments
- **Unusual charges**: amounts far above what's normal for that category
- **Possible duplicates**: same merchant and amount within 2 days
- **Refunds**, kept separate so they don't inflate income
- Row citations on every finding, plus a count of any rows the script skipped

Run on the bundled sample, it finds 4 subscriptions (Netflix, Spotify, Planet Fitness, Adobe), 2 unusual charges (Whole Foods $612.40 against a usual $83, a $385 steakhouse bill against a usual $35), 1 duplicate (Amazon $42.99 twice on Aug 14) and 1 refund (Target +$64.20).

## Requirements

- Python 3.9 or newer (`python3 --version`). No packages to install.
- A CSV export of your statement. The default layout is `Date`, `Description`, `Amount` with negative amounts as spend. Other layouts (different headers, Debit/Credit columns, positive purchases) work with flags; see `references/column-mapping.md`.

## Install

Works in Claude Code, Claude.ai, OpenAI Codex, Gemini CLI, Cursor and GitHub Copilot. The skill uses the open SKILL.md format, so any compatible agent can load it.

**Any agent (recommended)**: clone the repo and run the installer. It detects which agents you have and copies the skill into each one's skills folder.
```
git clone https://github.com/Day-Raval/txn-statement-analyzer.git
cd txn-statement-analyzer
./install.sh              # agents detected on this machine
./install.sh --all        # all five
./install.sh codex gemini # only these
./install.sh --project    # into ./.agents/skills and ./.claude/skills of the current repo
./install.sh --uninstall
```
On Windows with WSL, install into your Windows home folder so Windows-native agents can find the skill: `HOME=/mnt/c/Users/<you> ./install.sh`

| Agent | Skills folder the installer uses |
|---|---|
| Claude Code | `~/.claude/skills/` |
| OpenAI Codex | `~/.agents/skills/` |
| Gemini CLI | `~/.gemini/skills/` |
| Cursor | `~/.cursor/skills/` |
| GitHub Copilot | `~/.copilot/skills/` |

**Claude Code plugin** (gets updates with `claude plugin update`):
```
claude plugin marketplace add Day-Raval/txn-statement-analyzer
claude plugin install txn-statement-analyzer@txn-statement-analyzer
```

**Claude.ai**: zip the `skills/txn-statement-analyzer/` folder and upload it under Settings > Capabilities > Skills. You need code execution turned on, because the skill runs a Python script.

**Agents without skill support**: open this repo in the agent. `AGENTS.md` tells it to follow `skills/txn-statement-analyzer/SKILL.md`.

## Use

```
Analyze my statement: ~/Downloads/statement.csv
```
Or attach the CSV and ask: "Where did my money go last month?", "Find my subscriptions" or "Any duplicate or unusual charges?"

To run the script without an agent:
```
python3 skills/txn-statement-analyzer/scripts/analyze.py statement.csv
```

## Try it with sample data

```
Analyze skills/txn-statement-analyzer/examples/sample-statement.csv
```
Compare the result with `examples/sample-output.md`. The sample is synthetic: 141 transactions from Jul–Sep 2026, made by `evals/make_sample.py`, with known answers planted in it.

## How it works

```
statement.csv ──► scripts/analyze.py ──► JSON (numbers + row citations) ──► agent writes the summary
                        ▲
            references/categories.md
```

| Finding | Rule |
|---|---|
| Merchant | Description in uppercase, with store numbers (`#1234`), card suffixes and reference IDs removed |
| Category | First keyword rule in `categories.md` that matches the merchant; anything else is `uncategorized` |
| Recurring | Same merchant, at least 3 charges, each amount within 5% of the median, about 30 days apart (±5 days) |
| Unusual | Amount above the category median + 3 × MAD (median absolute deviation). Only checked for categories with 5 or more charges; recurring charges are left out |
| Duplicate | Same merchant and same amount within 2 days |
| Refund | Positive amount whose description contains `REFUND` |

The output JSON has the keys `meta`, `totals`, `monthly`, `categories`, `recurring`, `anomalies`, `duplicates` and `refunds`. The skill's instructions tell the agent to use only numbers from this JSON and to say so when a question needs data the JSON doesn't have.

## Customize

- `references/categories.md`: add your merchants or new categories, one line per category
- `references/column-mapping.md`: which flags to use for other bank export layouts

## Privacy

Your statement is read on your machine by a local Python script. The script makes no network calls, the skill has no MCP servers, and the results appear only in your chat. The agent you use still sees the script's output (merchant names and amounts) the same way it sees anything you paste, so use an agent and plan whose data policy you're comfortable with.

The repo's `.gitignore` excludes every `*.csv` except the synthetic sample, and CI fails if any other CSV is committed. Never commit a real statement.

## Limits

- This is not financial advice. It reports what's in the file and flags things to check.
- Rules are simple on purpose so you can check them. A merchant with one extra purchase on top of a subscription won't show as recurring. A bank that writes refunds without the word `REFUND` will show them as income.
- One account and one currency per file.

## Troubleshooting

| Problem | Fix |
|---|---|
| `missing column(s)` | Pass your header names, e.g. `--date "Transaction Date" --description Payee`, or `--debit Debit --credit Credit` (see `references/column-mapping.md`) |
| Spend shows as income | Your bank exports purchases as positive amounts; add `--flip-sign` |
| Many rows `skipped` | The date format isn't recognized. Supported: `2026-07-01`, `07/01/2026`, `07/01/26`, `01-Jul-2026` |
| Lots of `uncategorized` | Add your merchants to `references/categories.md` |
| `python3: command not found` | Install Python 3.9+ (on Windows, use `py` in place of `python3`) |
| Skill doesn't load | Start a new session, mention "statement" or "transactions" with your CSV, or check the skill is in your agent's skills folder |
| Other issues | Open an issue: https://github.com/Day-Raval/txn-statement-analyzer/issues |

## Testing

```
python3 skills/txn-statement-analyzer/scripts/test_analyze.py
```
This checks every planted answer and total in the sample, messy input (accounting-style negatives, `$` and commas, bad rows) and the column flags (Debit/Credit, `--flip-sign`, wrong headers). CI runs it on every push. `evals/trigger-tests.md` has prompts that should and shouldn't load the skill.

## Security

See [SECURITY.md](SECURITY.md) to report a vulnerability.

## License

MIT
