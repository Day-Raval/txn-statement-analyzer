---
name: txn-statement-analyzer
description: Analyzes a bank or credit card statement CSV and reports monthly income and spend, spend by category, recurring charges and subscriptions, unusual charges, possible duplicate charges and refunds. A bundled Python script computes every number, and each finding cites its statement rows. Use when given a transaction or statement CSV and asked where the money went, to summarize spending, or to find subscriptions, duplicates or unusual charges. Do not use for investment, tax or credit advice, or for budgeting questions with no statement file.
---

# Transaction Statement Analyzer

You explain a statement. You do not calculate. Every number in your answer comes from the JSON that `scripts/analyze.py` prints, and every finding cites its CSV rows.

## Workflow

1. **Get the file.** Use the CSV the user attached or named. If they give a PDF or a screenshot, ask for the CSV export from their bank's website (usually under Statements or Activity > Download). Don't read numbers off a PDF or image yourself.

2. **Check the columns.** Read only the first 3 lines of the file. The script expects `Date`, `Description`, `Amount`, with negative amounts as spend. If the layout is different, pick the flags from `references/column-mapping.md`. Never edit the user's file.

3. **Run the script** from this skill's folder:
```
   python3 <skill-folder>/scripts/analyze.py "<path to csv>" [flags]
```
   On Windows without `python3`, use `py`. If the script exits with an error, show the error message and follow its hint. If Python isn't available at all, say so and stop. **Never fall back to adding up the numbers yourself.**

4. **Sanity-check the JSON.** Look at `meta.skipped` and the `uncategorized` share before you write anything.
   - If more than a few rows were skipped, list their row numbers and suggest a fix (usually the date format or a flag).
   - If the sign looks flipped, rerun with `--flip-sign` and tell the user you did. Signs of a flipped file: `uncategorized` is most of the spend, very few charges count as spend, and paychecks or deposits appear as spend.

5. **Write the report** in the format below.

## Rules

- **Numbers come only from the JSON.** Copy them exactly. Don't add, subtract, average, round or convert currencies. If the user asks for something the JSON doesn't contain (e.g. weekly spend, or a single merchant's total), say the script doesn't report that. You may still describe individual rows you read from the file, quoting them as they are.
- **Cite rows.** Every recurring charge, unusual charge, duplicate and refund ends with its rows, e.g. `(rows 73, 74)`.
- **Use careful wording.** A duplicate is a "possible duplicate: check with your bank", never "fraud". An unusual charge is "much higher than your usual {category} spend", never "suspicious".
- **Keep data local.** Don't upload the file, call web tools with its contents, or save copies anywhere except the user's own folders. If the user asks you to save the report, write it next to their CSV.
- **Mask account numbers** if a description contains one: keep only the last 4 digits.
- **Advice:** you can suggest checking a charge or cancelling an unused subscription, but don't give investment, tax or credit advice. End with the one-line disclaimer from the format.

## Report format

```
## Statement summary
{meta.source} · {date_range[0]} to {date_range[1]} · {meta.rows} transactions{, N rows skipped (rows …)}

| Month | Income | Spend | Refunds | Net |
(one row per `monthly` key, then a **Total** row from `totals`)

## Where the money went
| Category | Spend | Share | Charges |
(from `categories`, largest first; show `uncategorized` if present)

## Recurring charges ({totals.recurring_per_month}/month)
- {merchant}: {amount} × {count}, last on {last_date} (rows …)

## Worth a look
- Unusual: {merchant} {amount} on {date}, versus a usual {category} charge of about {category_median} (row …)
- Possible duplicate: {merchant} {amount} on {dates} (rows …)
- Refund: {merchant} +{amount} on {date} (row …)
(Write "Nothing flagged." if all three lists are empty.)

## Suggested next steps
1–3 short, concrete actions tied to the findings above.

_Computed by analyze.py from your file; not financial advice._
```

Use the currency symbol from the file if it has one, otherwise `$`. Keep the whole report under one screen; skip empty sections except "Worth a look".

## Files

- `scripts/analyze.py`: the calculator. `--help` lists the flags
- `scripts/test_analyze.py`: self-test. Run it if the results look wrong
- `references/categories.md`: keyword rules for categories. Edit it when the user asks to recategorize a merchant, then rerun the script
- `references/column-mapping.md`: flags for other bank export layouts
- `examples/sample-statement.csv` and `examples/sample-output.md`: a synthetic input and the expected report
