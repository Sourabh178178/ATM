import csv
import json
import time
from pathlib import Path
from kafka import KafkaProducer

ROOT = Path(__file__).resolve().parents[2]
CSV_PATH = ROOT / "data" / "atm_transactions.csv"
TOPIC = "atm-transactions-full"
LIMIT = None
DELAY_SECONDS = 0.05

producer = KafkaProducer(
    bootstrap_servers="localhost:9092",
    value_serializer=lambda value: json.dumps(value).encode("utf-8"),
    key_serializer=lambda key: key.encode("utf-8"),
    acks="all",
)

sent = 0
try:
    with CSV_PATH.open("r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            event = {
                "atm_id": row["atm_id"],
                "timestamp": row["timestamp"],
                "withdrawal_amount": float(row["withdrawal_amount"]),
            }

            producer.send(
                TOPIC,
                key=event["atm_id"],
                value=event,
            ).get(timeout=15)

            sent += 1
            if sent % 100 == 0:
                print(f"Published {sent} transactions")

  

            time.sleep(DELAY_SECONDS)

    producer.flush()
    print(f"Finished: published {sent} transactions to {TOPIC}")

finally:
    producer.close()
