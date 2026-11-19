
import csv
from datetime import datetime
from pathlib import Path

INPUT_FILE = Path("data/data.txt")
OUTPUT_FILE = Path("data/cleaned_sensor_data.csv")

MAX_VALID_RECORDS = 10000

records = []
invalid = 0

with INPUT_FILE.open("r", encoding="utf-8") as file:
    for line in file:
        parts = line.strip().split()

        if len(parts) != 8:
            invalid += 1
            continue

        try:
            timestamp = datetime.fromisoformat(
                parts[0] + " " + parts[1]
            )

            epoch = int(parts[2])
            sensor_id = int(parts[3])

            temperature = float(parts[4])
            humidity = float(parts[5])
            light = float(parts[6])
            voltage = float(parts[7])

            # Conservative validation for this demonstration.
            if not (-20 <= temperature <= 60):
                invalid += 1
                continue

            if not (0 <= humidity <= 100):
                invalid += 1
                continue

            if light < 0 or voltage <= 0:
                invalid += 1
                continue

            records.append({
                "timestamp": timestamp,
                "epoch": epoch,
                "sensor_id": sensor_id,
                "temperature": temperature,
                "humidity": humidity,
                "light": light,
                "voltage": voltage
            })

        except (ValueError, OverflowError):
            invalid += 1
            continue

        if len(records) >= MAX_VALID_RECORDS:
            break

records.sort(key=lambda record: record["timestamp"])

OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

with OUTPUT_FILE.open("w", newline="", encoding="utf-8") as file:
    writer = csv.DictWriter(
        file,
        fieldnames=[
            "timestamp",
            "epoch",
            "sensor_id",
            "temperature",
            "humidity",
            "light",
            "voltage"
        ]
    )

    writer.writeheader()
    writer.writerows(records)

print("Data cleaning completed!")
print(f"Valid records: {len(records)}")
print(f"Rejected records: {invalid}")
print(f"Output file: {OUTPUT_FILE}")
