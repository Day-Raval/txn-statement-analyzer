#!/usr/bin/env python3
"""Check analyze.py against the planted answers in examples/sample-statement.csv.

Run: python3 skills/txn-statement-analyzer/scripts/test_analyze.py
"""
import contextlib, io, json, sys, tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import analyze  # noqa: E402

SAMPLE = HERE.parent / "examples" / "sample-statement.csv"


def run(path):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        analyze.main([str(path)])
    return json.loads(buf.getvalue())


def test_sample():
    out = run(SAMPLE)
    assert out["meta"]["rows"] == 141 and out["meta"]["skipped"] == 0, out["meta"]
    assert out["meta"]["date_range"] == ["2026-07-01", "2026-09-30"]

    rec = {r["merchant"]: r["amount"] for r in out["recurring"]}
    assert rec == {"NETFLIX.COM": 15.49, "SPOTIFY USA": 11.99, "PLANET FITNESS": 24.99,
                   "ADOBE CREATIVE CLOUD": 54.99}, rec

    anom = {(a["merchant"], a["amount"]) for a in out["anomalies"]}
    assert anom == {("WHOLE FOODS", 612.40), ("BLUE HERON STEAKHOUSE", 385.00)}, anom

    dups = [(d["merchant"], d["amount"], d["dates"][0]) for d in out["duplicates"]]
    assert dups == [("AMAZON MKTP", 42.99, "2026-08-14")], dups

    refs = [(r["merchant"], r["amount"]) for r in out["refunds"]]
    assert refs == [("TARGET REFUND", 64.20)], refs

    assert "uncategorized" not in out["categories"], out["categories"]
    assert out["totals"] == {"income": 19950.0, "spend": 6310.62, "refunds": 64.2, "net": 13703.58,
                             "recurring_per_month": 107.46}, out["totals"]
    assert abs(sum(c["share_pct"] for c in out["categories"].values()) - 100) < 0.5
    # every finding cites at least one source row
    for key in ("recurring", "anomalies", "duplicates", "refunds"):
        assert all(item["rows"] for item in out[key]), key


def run_text(csv_text, *flags):
    with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False) as f:
        f.write(csv_text)
    try:
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            analyze.main([f.name, *flags])
        return json.loads(buf.getvalue())
    finally:
        Path(f.name).unlink()


def test_messy_input():
    out = run_text("date,description,amount\n"
                   "07/01/2026,\"COFFEE SHOP #12\",\"($4.50)\"\n"
                   "not-a-date,BAD ROW,-1.00\n"
                   "2026-07-02,PAYCHECK,\"$1,000.00\"\n")
    assert out["meta"]["rows"] == 2 and out["meta"]["skipped_rows"] == [3], out["meta"]
    assert out["monthly"]["2026-07"] == {"income": 1000.0, "spend": 4.5, "refunds": 0.0, "net": 995.5}
    assert out["categories"]["uncategorized"]["total"] == 4.5


def test_column_options():
    # split debit/credit columns with custom headers
    out = run_text("Posted,Payee,Debit,Credit\n"
                   "2026-07-01,COFFEE SHOP,4.50,\n"
                   "2026-07-02,PAYCHECK,,1000.00\n",
                   "--date", "Posted", "--description", "Payee", "--debit", "Debit", "--credit", "Credit")
    assert out["monthly"]["2026-07"] == {"income": 1000.0, "spend": 4.5, "refunds": 0.0, "net": 995.5}
    # card export with purchases as positive numbers
    out = run_text("Date,Description,Amount\n2026-07-01,COFFEE SHOP,4.50\n2026-07-02,PAYMENT THANK YOU,-50.00\n",
                   "--flip-sign")
    assert out["monthly"]["2026-07"]["spend"] == 4.5 and out["monthly"]["2026-07"]["income"] == 50.0
    # wrong header gives a clear error, not a crash
    try:
        run_text("When,What,HowMuch\n2026-07-01,X,-1\n")
        raise AssertionError("expected SystemExit")
    except SystemExit as e:
        assert "missing column" in str(e.code)


def test_date_range():
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        analyze.main([str(SAMPLE), "--start", "2026-08-01", "--end", "2026-08-31"])
    out = json.loads(buf.getvalue())
    assert out["meta"]["date_range"] == ["2026-08-01", "2026-08-31"], out["meta"]
    assert list(out["monthly"]) == ["2026-08"], out["monthly"]
    assert out["categories"]["coffee"] == {"total": 44.65, "count": 6, "share_pct": 1.9}, out["categories"]["coffee"]
    assert out["duplicates"][0]["rows"] == [73, 74]  # row numbers still point at the original file
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            analyze.main([str(SAMPLE), "--start", "2027-01-01"])
        raise AssertionError("expected SystemExit")
    except SystemExit as e:
        assert "date range" in str(e.code)


if __name__ == "__main__":
    test_sample()
    test_messy_input()
    test_column_options()
    test_date_range()
    print("all tests passed")
