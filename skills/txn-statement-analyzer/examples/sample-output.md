# Sample output (gold standard)

Input: `examples/sample-statement.csv` (synthetic). Command: `python3 scripts/analyze.py examples/sample-statement.csv`. Every number below is copied from the script's JSON.

## Statement summary
sample-statement.csv · 2026-07-01 to 2026-09-30 · 141 transactions

| Month | Income | Spend | Refunds | Net |
|---|---|---|---|---|
| 2026-07 | $8,550.00 | $1,644.20 | $64.20 | $6,970.00 |
| 2026-08 | $5,700.00 | $2,361.32 | $0.00 | $3,338.68 |
| 2026-09 | $5,700.00 | $2,305.10 | $0.00 | $3,394.90 |
| **Total** | **$19,950.00** | **$6,310.62** | **$64.20** | **$13,703.58** |

## Where the money went
| Category | Spend | Share | Charges |
|---|---|---|---|
| Groceries | $2,585.89 | 41.0% | 27 |
| Dining | $1,308.81 | 20.7% | 29 |
| Shopping | $802.55 | 12.7% | 17 |
| Gas | $574.24 | 9.1% | 11 |
| Utilities | $353.49 | 5.6% | 3 |
| Subscriptions | $322.38 | 5.1% | 12 |
| Transport | $201.84 | 3.2% | 10 |
| Coffee | $161.42 | 2.6% | 24 |

## Recurring charges ($107.46/month)
- NETFLIX.COM: $15.49 × 3, last on 2026-09-03 (rows 7, 57, 101)
- SPOTIFY USA: $11.99 × 3, last on 2026-09-08 (rows 19, 63, 110)
- PLANET FITNESS: $24.99 × 3, last on 2026-09-11 (rows 22, 65, 121)
- ADOBE CREATIVE CLOUD: $54.99 × 3, last on 2026-09-18 (rows 33, 82, 132)

## Worth a look
- Unusual: WHOLE FOODS $612.40 on 2026-08-17, versus a usual groceries charge of about $83.47 (row 80)
- Unusual: BLUE HERON STEAKHOUSE $385.00 on 2026-09-05, versus a usual dining charge of about $34.86 (row 106)
- Possible duplicate: AMAZON MKTP $42.99 on 2026-08-14 and 2026-08-14 (rows 73, 74). Check with your bank.
- Refund: TARGET REFUND +$64.20 on 2026-07-29 (row 46)

## Suggested next steps
1. Check the two Amazon $42.99 charges on Aug 14 against your order history, and dispute one if you placed only one order.
2. Confirm the $612.40 Whole Foods charge was a planned stock-up and not an error.
3. Review whether you use all four subscriptions ($107.46/month).

_Computed by analyze.py from your file; not financial advice._
