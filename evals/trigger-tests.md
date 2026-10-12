# Trigger and behavior tests

Run each prompt in a fresh session with the skill installed. Fill in the last column.
Target: all positives trigger, no negatives trigger, and every behavior test passes.

## Trigger tests

| # | Prompt | Should trigger | Triggered |
|---|---|---|---|
| 1 | Analyze my statement: skills/txn-statement-analyzer/examples/sample-statement.csv | Y | |
| 2 | Where did my money go last quarter? <attach CSV> | Y | |
| 3 | Find all my subscriptions in this bank export. <attach CSV> | Y | |
| 4 | Are there any duplicate or weird charges on my card statement? <attach CSV> | Y | |
| 5 | Summarize my spending by category from transactions.csv | Y | |
| 6 | How should I invest $10,000? | N | |
| 7 | Make me a monthly budget template in Excel. | N | |
| 8 | What's a good credit utilization ratio? | N | |
| 9 | Clean up this CSV of customer emails. <attach CSV> | N | |
| 10 | Explain what a chargeback is. | N | |

## Behavior tests

| # | Setup | Prompt | Pass if | Result |
|---|---|---|---|---|
| B1 | none | Analyze my bank statement PDF. <attach any PDF> | Asks for the CSV export; reads no numbers off the PDF | |
| B2 | sample CSV | How much did I spend on coffee in the second week of August? | Says the script doesn't report weekly totals; doesn't add rows up itself | |
| B3 | flipped copy (see below) | Analyze ~/flipped.csv | Notices the sign looks wrong, reruns with `--flip-sign`, says so | |
| B4 | split copy (see below) | Analyze ~/split.csv | Reads the header, runs with `--debit Debit --credit Credit` | |
| B5 | sample CSV | Is the Amazon double charge fraud? | Calls it a possible duplicate to check with the bank, not fraud | |

Make the B3 and B4 files outside the repo (the repo's `.gitignore` blocks extra CSVs anyway):
```
python3 - <<'PY'
import csv, pathlib
src = list(csv.reader(open("skills/txn-statement-analyzer/examples/sample-statement.csv")))
home = pathlib.Path.home()
with open(home / "flipped.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(src[0])
    w.writerows([d, s, f"{-float(a):.2f}"] for d, s, a in src[1:])
with open(home / "split.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["Date", "Description", "Debit", "Credit"])
    w.writerows([d, s, f"{-float(a):.2f}" if float(a) < 0 else "", a if float(a) > 0 else ""] for d, s, a in src[1:])
print("wrote", home / "flipped.csv", "and", home / "split.csv")
PY
```
Delete both files when you're done.

## Quality checks (run 1, the sample)

- [ ] The agent ran `analyze.py` (visible in the tool calls) and didn't compute anything itself
- [ ] Every number matches `skills/txn-statement-analyzer/examples/sample-output.md`
- [ ] Every recurring charge, unusual charge, duplicate and refund cites rows, and the rows match
- [ ] Wording says "possible duplicate", not "fraud" or "suspicious"
- [ ] Ends with the "not financial advice" line
- [ ] Fits on about one screen

## Results: v1.0.0, Claude.ai, 2026-10-12

| Test | Result | Notes |
|---|---|---|
| Triggers 1–5 | 5/5 loaded | #5 noticed the file name didn't match the attachment and used the attachment |
| Triggers 6–10 | 0/5 loaded | #7 loaded the xlsx skill instead; #9 (a CSV of emails) did not load this skill |
| B1 PDF | Pass | Asked for the CSV export, quoted no numbers |
| B2 weekly question | Pass | |
| B2b "coffee in August" | Pass | After two fixes: `--start`/`--end` added; baselines taken from the whole file |
| B3 flipped signs | Pass | Clean chat; spotted 99.7% uncategorized and reran with `--flip-sign` |
| B4 Debit/Credit columns | Pass | |
| B5 "is it fraud?" | Pass | "Possible duplicate: check with your bank" |
| Quality checks (sample) | Pass | Every number matches `examples/sample-output.md`; disclaimer is the last line after the checklist fix |

Bugs found by these tests and fixed before release: missing disclaimer, a model-written date filter, false unusual-charge flags in one-month ranges, and a misleading flipped-sign hint.
