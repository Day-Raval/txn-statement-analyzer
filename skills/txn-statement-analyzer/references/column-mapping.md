# Column mapping

`analyze.py` expects a CSV with a header row and the columns `Date`, `Description` and `Amount` (any letter case), where a negative amount is money spent. For any other layout, pass flags. Don't edit the user's file.

## Pick the flags

| What the first lines look like | Flags |
|---|---|
| `Date,Description,Amount` with negative spend | none |
| Different header names, e.g. `Transaction Date,Payee,Amount` | `--date "Transaction Date" --description Payee` |
| Separate money-out and money-in columns, e.g. `Date,Description,Debit,Credit` | `--debit Debit --credit Credit` |
| Only a money-out column (card exports) | `--debit "Charge Amount"` |
| Purchases are positive and payments are negative (common for credit cards) | `--flip-sign` |
| Several date columns (`Transaction Date`, `Post Date`) | use the transaction date: `--date "Transaction Date"` |

Flags can be combined, e.g. `--date "Trans. Date" --description Memo --flip-sign`. Header names must match the file exactly, apart from letter case; put names with spaces or dots in quotes.

## What the script accepts

- **Dates**: `2026-07-01`, `07/01/2026`, `07/01/26`, `01-Jul-2026`. Rows with any other date format are skipped and listed in `meta.skipped_rows`.
- **Amounts**: `-12.50`, `$1,234.56`, and accounting style `(12.50)` for negatives. With `--debit`/`--credit`, blank cells count as 0 and the debit is always treated as money out, whatever its sign.
- **Encoding**: UTF-8, with or without a byte order mark (BOM).

## How to tell the sign is wrong

After a run, if `totals.income` is close to zero but there's plenty of spend, or a store like a grocery chain shows up as income, the file uses positive amounts for purchases. Rerun with `--flip-sign`.

## Not supported

- PDF or image statements: ask for the CSV export instead.
- Files with extra lines above the header row: ask the user to delete those lines in a copy of the file, or to export again without a summary section.
- Several accounts or currencies in one file: run the script once per account.
