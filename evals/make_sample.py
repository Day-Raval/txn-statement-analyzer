"""Regenerate examples/sample-statement.csv (synthetic, deterministic).

Planted answers (asserted by test_analyze.py later):
  recurring : NETFLIX 15.49, SPOTIFY 11.99, PLANET FITNESS 24.99, ADOBE 54.99
  anomalies : WHOLE FOODS 612.40 (groceries), BLUE HERON STEAKHOUSE 385.00 (dining)
  duplicate : AMAZON MKTP 42.99 twice on 2026-08-14
  refund    : TARGET REFUND +64.20 (for the 2026-07-22 TARGET purchase)
"""
import csv, random
from datetime import date, timedelta
from pathlib import Path

rng = random.Random(42)
start = date(2026, 7, 1)
rows = []

def add(d, desc, amt):
    rows.append((d.isoformat(), desc, f"{amt:.2f}"))

def day(n):
    return start + timedelta(days=n)

# income: biweekly payroll (14 days apart, so never matches the ~30-day rule)
for n in range(2, 92, 14):
    add(day(n), "ACME CORP PAYROLL DIRECT DEP", 2850.00)

# planted subscriptions: same amount, 30 days apart, card suffix varies to test normalization
for name, amt, first in [("NETFLIX.COM", 15.49, 4), ("SPOTIFY USA", 11.99, 9),
                         ("PLANET FITNESS #0412", 24.99, 12), ("ADOBE CREATIVE CLOUD", 54.99, 19)]:
    for k in range(3):
        add(day(first + 30 * k), f"{name} CARD {rng.choice(['4821', 'X4821', '*4821'])}", -amt)

# monthly bills that must NOT be flagged recurring (amount varies > 5%)
for k, amt in enumerate([88.12, 121.47, 143.90]):
    add(day(15 + 30 * k), "PG&E ELECTRIC BILL", -amt)

# everyday spend: (merchants, low, high, count)
everyday = [
    (["SAFEWAY #1207", "TRADER JOE'S #552", "WHOLE FOODS #102"], 38, 115, 26),   # groceries
    (["CHIPOTLE #2231", "SWEETGREEN", "PHO HOA", "SUSHI ZONE"], 11, 58, 28),     # dining
    (["STARBUCKS #1234", "PHILZ COFFEE"], 4.5, 9.5, 24),                          # coffee
    (["SHELL OIL 5741", "CHEVRON 0098"], 38, 66, 11),                             # gas
    (["UBER *TRIP", "LYFT *RIDE"], 9, 34, 10),                                    # transport
    (["AMAZON MKTP", "TARGET #0871", "BEST BUY #331"], 14, 95, 14),               # shopping
]
for merchants, lo, hi, count in everyday:
    for _ in range(count):
        add(day(rng.randrange(92)), rng.choice(merchants), -round(rng.uniform(lo, hi), 2))

# planted anomalies, duplicate, refund
add(day(47), "WHOLE FOODS #102", -612.40)
add(day(66), "BLUE HERON STEAKHOUSE", -385.00)
add(date(2026, 8, 14), "AMAZON MKTP", -42.99)
add(date(2026, 8, 14), "AMAZON MKTP", -42.99)
add(date(2026, 7, 22), "TARGET #0871", -64.20)
add(date(2026, 7, 29), "TARGET #0871 REFUND", 64.20)

rows.sort(key=lambda r: r[0])
out = Path(__file__).resolve().parent.parent / "skills/txn-statement-analyzer/examples/sample-statement.csv"
out.parent.mkdir(parents=True, exist_ok=True)
with out.open("w", newline="") as f:
    w = csv.writer(f, lineterminator="\n")
    w.writerow(["Date", "Description", "Amount"])
    w.writerows(rows)
print(f"wrote {len(rows)} rows to {out}")
