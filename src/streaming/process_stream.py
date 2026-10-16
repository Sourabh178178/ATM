
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
INPUT = ROOT / "data" / "kafka_consumed_transactions.csv"
DAILY_OUTPUT = ROOT / "data" / "kafka_daily_demand.csv"
SUMMARY_OUTPUT = ROOT / "data" / "kafka_atm_summary.csv"


def main():
    if not INPUT.exists():
        raise FileNotFoundError(f"Input file not found: {INPUT}")

    df = pd.read_csv(INPUT, parse_dates=["timestamp"])

    required = {"atm_id", "timestamp", "withdrawal_amount"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns: {sorted(missing)}")

    df["withdrawal_amount"] = pd.to_numeric(
        df["withdrawal_amount"], errors="raise"
    )

    if df["withdrawal_amount"].isna().any():
        raise ValueError("Missing withdrawal amounts found.")

    if (df["withdrawal_amount"] < 0).any():
        raise ValueError("Negative withdrawal amounts found.")

    df["date"] = df["timestamp"].dt.normalize()

    daily = (
        df.groupby(["atm_id", "date"], as_index=False)
        .agg(
            total_demand=("withdrawal_amount", "sum"),
            transaction_count=("withdrawal_amount", "size"),
            average_withdrawal=("withdrawal_amount", "mean"),
        )
        .sort_values(["date", "atm_id"])
    )

    summary = (
        df.groupby("atm_id", as_index=False)
        .agg(
            total_demand=("withdrawal_amount", "sum"),
            transaction_count=("withdrawal_amount", "size"),
            average_withdrawal=("withdrawal_amount", "mean"),
            maximum_withdrawal=("withdrawal_amount", "max"),
        )
        .sort_values("total_demand", ascending=False)
    )

    daily.to_csv(DAILY_OUTPUT, index=False)
    summary.to_csv(SUMMARY_OUTPUT, index=False)

    print("STREAM ANALYTICS COMPLETE")
    print(f"Input transactions: {len(df):,}")
    print(f"ATMs processed: {df['atm_id'].nunique()}")
    print(f"ATM-day records: {len(daily):,}")
    print(f"Total withdrawals: ₹{df['withdrawal_amount'].sum():,.2f}")
    print(f"Daily output: {DAILY_OUTPUT}")
    print(f"ATM summary: {SUMMARY_OUTPUT}")


if __name__ == "__main__":
    main()
