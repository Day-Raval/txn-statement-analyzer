#!/usr/bin/env python3
"""Analyze a bank statement CSV and print JSON. Standard library only.

Usage: python3 analyze.py STATEMENT.csv [--categories FILE] [column options]
       python3 analyze.py --help

Input: CSV with Date, Description, Amount columns (case-insensitive). Negative amount = spend.
Other layouts: --date/--description/--amount rename columns, --debit/--credit for split columns,
--flip-sign when purchases are positive. See references/column-mapping.md.
Every finding carries `rows` (CSV line numbers) so each number can be traced back to the source.
"""
import argparse, csv, json, re, statistics, sys
from collections import defaultdict
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path

DATE_FORMATS = ("%Y-%m-%d", "%m/%d/%Y", "%m/%d/%y", "%d-%b-%Y")
NOISE = re.compile(r"#\d+|\bCARD\s+\S+|\*\w+|\b\d{3,}\b")  # store numbers, card suffixes, ref ids
CENT = Decimal("0.01")


def parse_date(s):
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(s.strip(), fmt).date()
        except ValueError:
            pass
    return None


def parse_amount(s):
    s = s.strip().replace("$", "").replace(",", "")
    neg = s.startswith("(") and s.endswith(")")  # accounting style (12.00) = negative
    try:
        v = Decimal(s.strip("()"))
    except InvalidOperation:
        return None
    return -v if neg else v


def normalize(desc):
    return re.sub(r"\s+", " ", NOISE.sub("", desc.upper())).strip()


def load_rules(path):
    rules = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        m = re.match(r"^-\s*([\w ]+?)\s*:\s*(.+)$", line)
        if m:
            rules.append((m[1].strip(), [k.strip().upper() for k in m[2].split(",") if k.strip()]))
    return rules


def categorize(merchant, rules):
    for name, keywords in rules:
        if any(k in merchant for k in keywords):
            return name
    return "uncategorized"


def money(d):
    return float(Decimal(d).quantize(CENT))  # Decimal() also accepts the int 0 from an empty sum()


def load(path, names, flip_sign=False):
    """names: header names for date, description, amount, debit, credit (case-insensitive)."""
    txns, skipped = [], []
    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        cols = {c.strip().lower(): c for c in (reader.fieldnames or [])}
        pick = {k: cols.get(v.strip().lower()) for k, v in names.items() if v}
        split = bool(names["debit"] or names["credit"])
        need = ["date", "description"] + ([k for k in ("debit", "credit") if names[k]] if split else ["amount"])
        missing = [names[k] for k in need if not pick.get(k)]
        if missing:
            sys.exit(f"error: missing column(s) {missing}; found {reader.fieldnames}. "
                     "Pass --date/--description/--amount (or --debit/--credit). See references/column-mapping.md")
        for line, r in enumerate(reader, start=2):
            d = parse_date(r[pick["date"]] or "")
            desc = (r[pick["description"]] or "").strip()
            if split:  # blank cell = 0; debit is money out, credit is money in
                parts = [parse_amount((r[pick[k]] or "").strip() or "0") if pick.get(k) else Decimal(0)
                         for k in ("debit", "credit")]
                a = None if None in parts else parts[1] - abs(parts[0])
            else:
                a = parse_amount(r[pick["amount"]] or "")
            if d is None or a is None or not desc:
                skipped.append(line)
                continue
            if flip_sign:
                a = -a
            txns.append({"row": line, "date": d, "desc": desc, "merchant": normalize(desc), "amount": a})
    return txns, skipped


def analyze(txns, rules):
    refunds = [t for t in txns if t["amount"] > 0 and "REFUND" in t["desc"].upper()]
    refund_rows = {t["row"] for t in refunds}
    spend = [t for t in txns if t["amount"] < 0]
    for t in spend:
        t["category"] = categorize(t["merchant"], rules)

    monthly = defaultdict(lambda: {"income": Decimal(0), "spend": Decimal(0), "refunds": Decimal(0)})
    for t in txns:
        m = monthly[t["date"].strftime("%Y-%m")]
        key = "refunds" if t["row"] in refund_rows else "income" if t["amount"] > 0 else "spend"
        m[key] += abs(t["amount"])
    monthly_out = {k: {"income": money(v["income"]), "spend": money(v["spend"]), "refunds": money(v["refunds"]),
                       "net": money(v["income"] + v["refunds"] - v["spend"])} for k, v in sorted(monthly.items())}

    cats = defaultdict(list)
    for t in spend:
        cats[t["category"]].append(t)
    total_spend = sum(v["spend"] for v in monthly.values())
    categories = {c: {"total": money(sum(-t["amount"] for t in ts)), "count": len(ts),
                      "share_pct": float(round(sum(-t["amount"] for t in ts) * 100 / total_spend, 1)) if total_spend else 0.0}
                  for c, ts in sorted(cats.items(), key=lambda kv: sum(t["amount"] for t in kv[1]))}

    # recurring: >=3 charges, amounts within 5% of their median, consecutive gaps 30 +/- 5 days
    # shortcut: needs every charge from a merchant to fit; a one-off extra purchase hides the series
    by_merchant = defaultdict(list)
    for t in spend:
        by_merchant[t["merchant"]].append(t)
    recurring = []
    for m, ts in by_merchant.items():
        ts.sort(key=lambda t: t["date"])
        amts = [-t["amount"] for t in ts]
        med = statistics.median(amts)
        if len(ts) >= 3 and all(abs(a - med) <= med * Decimal("0.05") for a in amts) \
                and all(25 <= (b["date"] - a["date"]).days <= 35 for a, b in zip(ts, ts[1:])):
            recurring.append({"merchant": m, "amount": money(med), "count": len(ts),
                              "last_date": ts[-1]["date"].isoformat(), "rows": [t["row"] for t in ts]})

    # anomalies: amount > category median + 3 * MAD (needs >= 5 charges and MAD > 0)
    # recurring charges are expected, so they are left out of the check
    recurring_rows = {r for item in recurring for r in item["rows"]}
    anomalies = []
    for c, ts in cats.items():
        ts = [t for t in ts if t["row"] not in recurring_rows]
        amts = [-t["amount"] for t in ts]
        if len(amts) < 5:
            continue
        med = statistics.median(amts)
        mad = statistics.median(abs(a - med) for a in amts)
        if mad == 0:
            continue
        limit = med + 3 * mad
        for t in ts:
            if -t["amount"] > limit:
                anomalies.append({"merchant": t["merchant"], "category": c, "amount": money(-t["amount"]),
                                  "date": t["date"].isoformat(), "category_median": money(med),
                                  "threshold": money(limit), "rows": [t["row"]]})

    # duplicates: same merchant and amount within 2 days
    duplicates = []
    ordered = sorted(spend, key=lambda t: t["date"])
    for i, a in enumerate(ordered):
        for b in ordered[i + 1:]:
            if (b["date"] - a["date"]).days > 2:
                break
            if a["merchant"] == b["merchant"] and a["amount"] == b["amount"]:
                duplicates.append({"merchant": a["merchant"], "amount": money(-a["amount"]),
                                   "dates": [a["date"].isoformat(), b["date"].isoformat()], "rows": [a["row"], b["row"]]})

    totals = {k: money(sum(v[k] for v in monthly.values())) for k in ("income", "spend", "refunds")}
    totals["net"] = money(sum(v["income"] + v["refunds"] - v["spend"] for v in monthly.values()))
    totals["recurring_per_month"] = money(sum(Decimal(str(r["amount"])) for r in recurring))

    refunds_out = [{"merchant": t["merchant"], "amount": money(t["amount"]), "date": t["date"].isoformat(),
                    "rows": [t["row"]]} for t in refunds]
    return monthly_out, totals, categories, recurring, anomalies, duplicates, refunds_out


def main(argv=None):
    here = Path(__file__).resolve().parent.parent
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("csv")
    p.add_argument("--categories", default=str(here / "references" / "categories.md"))
    p.add_argument("--date", default="Date", help="date column header")
    p.add_argument("--description", default="Description", help="description column header")
    p.add_argument("--amount", default="Amount", help="signed amount column header")
    p.add_argument("--debit", help="money-out column (use with --credit instead of --amount)")
    p.add_argument("--credit", help="money-in column (use with --debit instead of --amount)")
    p.add_argument("--flip-sign", action="store_true", help="file shows purchases as positive numbers")
    args = p.parse_args(argv)

    names = {"date": args.date, "description": args.description, "amount": args.amount,
             "debit": args.debit, "credit": args.credit}
    txns, skipped = load(args.csv, names, args.flip_sign)
    if not txns:
        sys.exit("error: no valid rows found")
    monthly, totals, categories, recurring, anomalies, duplicates, refunds = analyze(txns, load_rules(args.categories))
    dates = [t["date"] for t in txns]
    out = {
        "meta": {"source": Path(args.csv).name, "rows": len(txns), "skipped": len(skipped), "skipped_rows": skipped,
                 "date_range": [min(dates).isoformat(), max(dates).isoformat()]},
        "totals": totals, "monthly": monthly, "categories": categories, "recurring": recurring,
        "anomalies": anomalies, "duplicates": duplicates, "refunds": refunds,
    }
    json.dump(out, sys.stdout, indent=2)
    print()


if __name__ == "__main__":
    main()
