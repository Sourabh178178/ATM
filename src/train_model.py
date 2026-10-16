
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error
from sklearn.model_selection import train_test_split

DATA_PATH = Path("data/kafka_consumed_transactions.csv")
MODEL_DIR = Path("models")
MODEL_DIR.mkdir(parents=True, exist_ok=True)

PREDICTIONS_PATH = Path("data/forecast_results.csv")
METRICS_PATH = Path("data/model_metrics.csv")

# 1. Load transaction records
transactions = pd.read_csv(DATA_PATH, parse_dates=["timestamp"])

# 2. Aggregate transactions into daily demand per ATM
transactions["date"] = transactions["timestamp"].dt.normalize()

daily = (
    transactions.groupby(["atm_id", "date"], as_index=False)
    ["withdrawal_amount"]
    .sum()
    .rename(columns={"withdrawal_amount": "daily_demand"})
)

daily = daily.sort_values(["atm_id", "date"]).reset_index(drop=True)

# 3. Create historical demand features separately for each ATM
grouped = daily.groupby("atm_id")["daily_demand"]

daily["lag_1"] = grouped.shift(1)
daily["lag_2"] = grouped.shift(2)
daily["lag_7"] = grouped.shift(7)
daily["rolling_mean_7"] = (
    daily.groupby("atm_id")["daily_demand"]
    .transform(lambda s: s.shift(1).rolling(7).mean())
)
daily["rolling_mean_14"] = (
    daily.groupby("atm_id")["daily_demand"]
    .transform(lambda s: s.shift(1).rolling(14).mean())
)

daily["day_of_week"] = daily["date"].dt.dayofweek
daily["day_of_month"] = daily["date"].dt.day
daily["month"] = daily["date"].dt.month
daily["is_weekend"] = (daily["day_of_week"] >= 5).astype(int)
daily["is_month_end"] = (daily["day_of_month"] >= 27).astype(int)

FEATURES = [
    "lag_1",
    "lag_2",
    "lag_7",
    "rolling_mean_7",
    "rolling_mean_14",
    "day_of_week",
    "day_of_month",
    "month",
    "is_weekend",
    "is_month_end",
]

model_data = daily.dropna(subset=FEATURES).copy()

if len(model_data) < 50:
    raise ValueError("Not enough daily data to train the model.")

# 4. Chronological split: earlier dates train, later dates test
unique_dates = sorted(model_data["date"].unique())
split_index = int(len(unique_dates) * 0.80)
split_date = unique_dates[split_index]

train = model_data[model_data["date"] < split_date]
test = model_data[model_data["date"] >= split_date]

X_train = train[FEATURES]
y_train = train["daily_demand"]
X_test = test[FEATURES]
y_test = test["daily_demand"]

# 5. Train Random Forest
model = RandomForestRegressor(
    n_estimators=150,
    max_depth=12,
    min_samples_leaf=2,
    random_state=42,
    n_jobs=-1,
)

model.fit(X_train, y_train)

# 6. Evaluate on later unseen dates
test_predictions = np.maximum(0, model.predict(X_test))
mae = mean_absolute_error(y_test, test_predictions)

actual_total = y_test.sum()
weighted_absolute_percentage_error = (
    np.abs(y_test.to_numpy() - test_predictions).sum()
    / actual_total * 100
    if actual_total else 0
)

# 7. Generate next-day forecast for every ATM
latest_rows = (
    model_data.sort_values("date")
    .groupby("atm_id")
    .tail(1)
    .copy()
)

# Forecast the day after each ATM's latest recorded date
next_dates = latest_rows["date"] + pd.Timedelta(days=1)
latest_rows["date"] = next_dates

next_day_features = latest_rows[FEATURES].copy()
forecast = np.maximum(0, model.predict(next_day_features))

results = pd.DataFrame({
    "atm_id": latest_rows["atm_id"].to_numpy(),
    "forecast_date": next_dates.dt.strftime("%Y-%m-%d").to_numpy(),
    "predicted_demand": np.round(forecast, 2),
})

# Add a configurable 10% planning buffer
results["recommended_cash"] = np.ceil(
    results["predicted_demand"] * 1.10 / 500
) * 500

# 8. Save outputs
results.to_csv(PREDICTIONS_PATH, index=False)

metrics = pd.DataFrame([{
    "model": "Random Forest Regressor",
    "train_rows": len(train),
    "test_rows": len(test),
    "mae_rupees": round(float(mae), 2),
    "wape_percent": round(float(weighted_absolute_percentage_error), 2),
    "train_start": str(train["date"].min().date()),
    "train_end": str(train["date"].max().date()),
    "test_start": str(test["date"].min().date()),
    "test_end": str(test["date"].max().date()),
}])
metrics.to_csv(METRICS_PATH, index=False)

joblib.dump(
    {"model": model, "features": FEATURES},
    MODEL_DIR / "atm_forecaster.joblib",
)

# 9. Report results
print("\nATM CASH FORECASTING — MODEL RESULTS")
print("=" * 48)
print(f"Training records : {len(train):,}")
print(f"Testing records  : {len(test):,}")
print(f"MAE              : ₹{mae:,.2f}")
print(f"WAPE             : {weighted_absolute_percentage_error:.2f}%")
print("\nNext-day cash forecasts:")
print(results.to_string(index=False))
print(f"\nSaved predictions: {PREDICTIONS_PATH.resolve()}")
print(f"Saved metrics    : {METRICS_PATH.resolve()}")
print(f"Saved model      : {(MODEL_DIR / 'atm_forecaster.joblib').resolve()}")
