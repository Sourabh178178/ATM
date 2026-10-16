import csv
import json
from pathlib import Path
from kafka import KafkaConsumer

ROOT = Path(__file__).resolve().parents[2]
OUTPUT_PATH = ROOT / "data" / "kafka_consumed_transactions.csv"
TOPIC = "atm-transactions-full"
TARGET_COUNT = 37910

consumer = KafkaConsumer(
    TOPIC,
    bootstrap_servers="localhost:9092",
    auto_offset_reset="earliest",
    enable_auto_commit=False,
    group_id="atm-analytics-consumer",
    value_deserializer=lambda value: json.loads(value.decode("utf-8")),
)

fields = ["atm_id", "timestamp", "withdrawal_amount"]
received = 0

try:
    with OUTPUT_PATH.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()

        print(f"Listening for up to {TARGET_COUNT} events...")
        for message in consumer:
            event = message.value
            writer.writerow({
                "atm_id": event["atm_id"],
                "timestamp": event["timestamp"],
                "withdrawal_amount": event["withdrawal_amount"],
            })
            received += 1

            if received % 100 == 0:
                file.flush()
                print(f"Consumed {received} transactions")

            if received >= TARGET_COUNT:
                break

    print(f"Finished: saved {received} transactions to {OUTPUT_PATH}")

finally:
    consumer.close()
