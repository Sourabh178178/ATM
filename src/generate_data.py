
import numpy as np
import pandas as pd
from pathlib import Path

# All project paths are relative to D:\BDA_project
OUTPUT = Path("data/atm_transactions.csv")
OUTPUT.parent.mkdir(parents=True, exist_ok=True)

rng = np.random.default_rng(42)

# 180 days of simulated ATM transactions
dates = pd.date_range(
    end=pd.Timestamp.today().normalize(),
    periods=180,
    freq="D"
)

atm_demand = {
    "ATM001": 52000,
    "ATM002": 18000,
    "ATM003": 75000,
    "ATM004": 32000,
    "ATM005": 12000,
    "ATM006": 45000,
    "ATM007": 60000,
    "ATM008": 25000,
}

records = []

for atm_id, base_demand in atm_demand.items():
    for day in dates:
        weekday_factor = (
            1.15 if day.weekday() < 5 else 0.80
        )

        month_end_factor = (
            1.30 if day.day >= 27 or day.day <= 2
            else 1.0
        )

        daily_demand = max(
            1000,
            base_demand
            * weekday_factor
            * month_end_factor
            * rng.normal(1.0, 0.15)
        )

        transaction_count = int(rng.integers(12, 41))

        # Divide daily withdrawals into individual transactions
        amounts = rng.dirichlet(
            np.ones(transaction_count) * 2
        ) * daily_demand

        for amount in amounts:
            timestamp = (
                day
                + pd.Timedelta(
                    hours=int(rng.integers(7, 23)),
                    minutes=int(rng.integers(0, 60))
                )
            )

            records.append({
                "atm_id": atm_id,
                "timestamp": timestamp,
                "withdrawal_amount": round(
                    float(amount), 2
                )
            })

df = pd.DataFrame(records)
df = df.sort_values("timestamp").reset_index(drop=True)

df.to_csv(OUTPUT, index=False)

print("\nATM CASH FORECASTING — DATA GENERATOR")
print("=" * 45)
print(f"Total transactions : {len(df):,}")
print(f"Unique ATMs        : {df['atm_id'].nunique()}")
print(f"Date range         : {df['timestamp'].min().date()} "
      f"to {df['timestamp'].max().date()}")
print(f"Total withdrawals  : ₹{df['withdrawal_amount'].sum():,.2f}")
print(f"Output file        : {OUTPUT.resolve()}")
print("\nSample transactions:")
print(df.head().to_string(index=False))
print("\nDataset generated successfully!")
